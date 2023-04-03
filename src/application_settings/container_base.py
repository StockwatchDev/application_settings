# pylint: disable=consider-alternative-union-syntax
"""Base classes for containers and sections for configuration and settings."""
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict, fields, replace
from enum import Enum, unique
from pathlib import Path
from re import sub
from typing import Any, Literal, Optional, TypeVar

import tomli_w
from pathvalidate import is_valid_filepath
from pydantic.dataclasses import dataclass

from .type_notation_helper import PathOpt, PathOrStr, dictOrAny

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


_ContainerT = TypeVar("_ContainerT", bound="ContainerBase")
_ContainerSectionT = TypeVar("_ContainerSectionT", bound="ContainerSectionBase")


if sys.version_info >= (3, 10):
    from typing import TypeAlias

    ContainerOrContainerSection: TypeAlias = _ContainerT | _ContainerSectionT
else:
    from typing import Union

    from typing_extensions import TypeAlias

    ContainerOrContainerSection: TypeAlias = Union[_ContainerT, _ContainerSectionT]


@unique
class FileFormat(Enum):
    "File formats that are supported"
    TOML = "toml"
    JSON = "json"


ContainerTypeStr = Literal["Config", "Settings"]


@dataclass(frozen=True)
class ContainerSectionBase:
    """Base class for all ContainerSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class ContainerBase(ABC):
    """Base class for Config and Settings classes"""

    @classmethod
    @abstractmethod
    def kind_string(cls: type[_ContainerT]) -> ContainerTypeStr:
        "Return either 'Config' or 'Settings'"

    @classmethod
    @abstractmethod
    def default_file_format(cls: type[_ContainerT]) -> FileFormat:
        "Return the default file format"

    @classmethod
    def default_foldername(cls: type[_ContainerT]) -> str:
        """Return the class name without kind_string, lowercase, with a preceding dot and underscores to seperate words."""
        kind_str = cls.kind_string()
        return (
            "."
            + sub("(?<!^)(?=[A-Z])", "_", cls.__name__.replace(kind_str, "")).lower()
        )

    @classmethod
    def default_filename(cls: type[_ContainerT]) -> str:
        """Return the kind_string, lowercase, with the extension that fits the file_format."""
        return f"{cls.kind_string().lower()}.{cls.default_file_format().value}"

    @classmethod
    def default_filepath(cls: type[_ContainerT]) -> PathOpt:
        """Return the fully qualified path for the config/settingsfile: e.g. ~/.example/config.toml"""
        return Path.home() / cls.default_foldername() / cls.default_filename()

    @classmethod
    def set_filepath(
        cls: type[_ContainerT], file_path: PathOrStr = "", reload: bool = False
    ) -> None:
        """Set the path for the file (a singleton)."""

        path: PathOpt = None
        if isinstance(file_path, Path):
            path = file_path.resolve()
        elif file_path:
            if is_valid_filepath(file_path, platform="auto"):
                path = Path(file_path).resolve()
            else:
                raise ValueError(
                    f"Given path: '{file_path}' is not a valid path for this OS"
                )

        if path:
            _ALL_PATHS[id(cls)] = path
        else:
            _ALL_PATHS.pop(id(cls), None)

        if reload:
            cls.get(reload=True)
        else:
            if cls._get() is not None:
                print(
                    f"Warning: filepath has been set the but file is not loaded into the {cls.kind_string()}."
                )

    @classmethod
    def filepath(cls) -> PathOpt:
        """Return the path for the file that holds the config / settings."""
        return _ALL_PATHS.get(id(cls), cls.default_filepath())

    @classmethod
    def _get(cls: type[_ContainerT]) -> Optional[_ContainerT]:
        """Private getter for the singleton."""
        return _ALL_CONTAINERS.get(id(cls))

    @classmethod
    def get(cls: type[_ContainerT], reload: bool = False) -> _ContainerT:
        """Access method for the singleton."""

        if (_the_container_or_none := cls._get()) is None or reload:
            # no config has been made yet or it needs to be reloaded,
            # so let's instantiate one and keep it in the global store
            _the_config = cls._create_instance()
            _the_config._set()
        else:
            _the_config = _the_container_or_none
        return _the_config

    @classmethod
    def update(
        cls: type[_ContainerT], changes: dict[str, dict[str, Any]]
    ) -> _ContainerT:
        "Update and save the settings with data specified in changes; not meant for config"
        return cls.get()._update(changes)  # pylint: disable=protected-access

    def _update(self: _ContainerT, changes: dict[str, dict[str, Any]]) -> _ContainerT:
        "Update and save the settings with data specified in changes; not meant for config"
        # filter out fields that are both in changes and an attribute of the SettingsContainer
        _sections_to_update = {
            fld for fld in fields(self) if fld.init and fld.name in changes.keys()
        }

        # update the sections and keep them in a dict
        # actually sections: dict[str, _ContainerSectionT]
        # but MyPy doesn't swallow that
        updated_sections: dict[str, Any] = {
            fld.name: _update_section(getattr(self, fld.name), changes[fld.name])
            for fld in _sections_to_update
        }
        new_settings = replace(self, **updated_sections)
        new_settings._set()  # pylint: disable=protected-access
        new_settings._save()  # pylint: disable=protected-access
        return new_settings

    @classmethod
    def _create_instance(cls: type[_ContainerT]) -> _ContainerT:
        """Instantiate the Container."""

        # get whatever is stored in the config/settings file
        data_stored = cls._get_stored_data()
        # instantiate the Container with the stored data
        return _instantiate_dataclass(cls, data_stored)

    @classmethod
    def _get_stored_data(cls) -> dict[str, Any]:
        """Get the data stored in the toml file"""
        data_stored: dict[str, Any] = {}

        if path := cls.filepath():
            if (ext := path.suffix[1:].lower()) == str(FileFormat.TOML.value):
                with path.open(mode="rb") as fptr:
                    data_stored = tomllib.load(fptr)
            elif ext == str(FileFormat.JSON.value):
                with path.open(mode="r") as fptr:
                    data_stored = json.load(fptr)
            else:
                print(f"Unknown file format {ext} given in {path}.")
        else:
            # This situation can occur if no valid path was given as an argument, and
            # the default path is set to None.
            print(
                f"No path specified for {cls.kind_string().lower()} file; trying with defaults, but this may not work."
            )
        return data_stored

    def _set(self) -> None:
        """Private method to store the singleton."""
        _ALL_CONTAINERS[id(self.__class__)] = self

    def _save(self) -> None:
        """Private method to save the singleton to file."""
        if path := self.filepath():
            path.parent.mkdir(parents=True, exist_ok=True)
            if (ext := path.suffix[1:].lower()) == FileFormat.TOML.value:
                with path.open(mode="wb") as fptr:
                    tomli_w.dump(asdict(self), fptr)
            elif ext == FileFormat.JSON.value:
                with path.open(mode="w") as fptr:
                    json.dump(asdict(self), fptr)
            else:
                print(f"Unknown file format {ext} given in {path}.")
        else:
            # This situation can occur if no valid path was given as an argument, and
            # the default path is set to None.
            raise RuntimeError(
                f"No path specified for {self.kind_string().lower()} file, cannot be saved."
            )


_ALL_CONTAINERS: dict[int, ContainerBase] = {}
_ALL_PATHS: dict[int, PathOpt] = {}


def _instantiate_field(
    class_to_instantiate: Any,
    arg_dict_or_val: dictOrAny,
) -> object:
    """Return an instance of class_to_instantiate, properly initialized with arg_dict"""
    if issubclass(class_to_instantiate, ContainerSectionBase):
        assert isinstance(arg_dict_or_val, dict)
        return _instantiate_dataclass(class_to_instantiate, arg_dict_or_val)
    # expectation: isinstance(arg_dict_or_val, class_to_instantiate)
    # but type coercion can take place
    return arg_dict_or_val


if sys.version_info >= (3, 10):

    def _instantiate_dataclass(
        class_to_instantiate: type[_ContainerT] | type[_ContainerSectionT],
        arg_dict: dict[str, Any],
    ) -> _ContainerT | _ContainerSectionT:
        """Return an instance of class_to_instantiate, properly initialized"""
        # filter out fields that are both stored and an attribute of the ContainerSection
        _data_fields = {
            fld
            for fld in fields(class_to_instantiate)
            if fld.init and fld.name in arg_dict.keys()
        }
        # instantiate the fields of the dataclass and keep them in a dict
        stored_fields: dict[str, Any] = {
            fld.name: _instantiate_field(fld.type, arg_dict[fld.name])
            for fld in _data_fields
        }

        # instantiate the ContainerSection
        return class_to_instantiate(**stored_fields)

else:
    from typing import Union

    def _instantiate_dataclass(
        class_to_instantiate: Union[type[_ContainerT], type[_ContainerSectionT]],
        arg_dict: dict[str, Any],
    ) -> Union[_ContainerT, _ContainerSectionT]:
        """Return an instance of class_to_instantiate, properly initialized"""
        # filter out fields that are both stored and an attribute of the ContainerSection
        _data_fields = {
            fld
            for fld in fields(class_to_instantiate)
            if fld.init and fld.name in arg_dict.keys()
        }
        # instantiate the fields of the dataclass and keep them in a dict
        stored_fields: dict[str, Any] = {
            fld.name: _instantiate_field(fld.type, arg_dict[fld.name])
            for fld in _data_fields
        }

        # instantiate the ContainerSection
        return class_to_instantiate(**stored_fields)


def _update_section(
    section: _ContainerSectionT, changes: dict[str, Any]
) -> _ContainerSectionT:
    "Update the settings section with data specified in changes; not meant for config"
    # filter out fields that are both in changes and an attribute of the SettingsSection
    return replace(section, **changes)
