"""Base classes for containers and sections for configuration and settings."""
import sys
from abc import ABC, abstractmethod
from dataclasses import fields
from pathlib import Path
from re import sub
from typing import Any, TypeVar

from pathvalidate import is_valid_filepath
from pydantic.dataclasses import dataclass

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


_ContainerT = TypeVar("_ContainerT", bound="ContainerBase")
_ContainerSectionT = TypeVar("_ContainerSectionT", bound="ContainerSectionBase")


_ALL_CONTAINERS: dict[int, Any] = {}
_ALL_PATHS: dict[int, Path | None] = {}


@dataclass(frozen=True)
class ContainerSectionBase:
    """Base class for all ContainerSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class ContainerBase(ABC):
    """Base class for Config and Settings classes"""

    @classmethod
    @abstractmethod
    def kind_string(cls: type[_ContainerT]) -> str:
        "Return either Config or Settings"

    @classmethod
    def default_foldername(cls: type[_ContainerT]) -> str:
        """Return the class name without kind_string, lowercase, with a preceding dot and underscores to seperate words."""
        kind_str = cls.kind_string()
        return (
            "."
            + sub("(?<!^)(?=[A-Z])", "_", cls.__name__.replace(kind_str, "")).lower()
        )

    @classmethod
    def default_filepath(cls: type[_ContainerT]) -> Path | None:
        """Return the fully qualified path for the config/settingsfile: e.g. ~/.example/config.toml"""
        return (
            Path.home()
            / f"{cls.default_foldername()}"
            / f"{cls.kind_string().lower()}.toml"
        )

    @classmethod
    def set_filepath(cls: type[_ContainerT], file_path: str | Path = "") -> None:
        """Set the path for the file (a singleton)."""

        path: Path | None = None
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

    @classmethod
    def filepath(cls) -> Path | None:
        """Return the path for the file that holds the config / settings."""
        return _ALL_PATHS.get(id(cls), cls.default_filepath())

    @classmethod
    def get(cls: type[_ContainerT], reload: bool = False) -> _ContainerT:
        """Access method for the singleton."""

        if ((_the_container_or_none := _ALL_CONTAINERS.get(id(cls))) is None) or reload:
            # no config has been made yet or it needs to be reloaded,
            # so let's instantiate one and keep it in the global store
            _the_config = cls._create_instance()
            _ALL_CONTAINERS[id(cls)] = _the_config
        else:
            _the_config = _the_container_or_none
        return _the_config

    @classmethod
    def _create_instance(cls: type[_ContainerT]) -> _ContainerT:
        """Instantiate the Container."""

        # get whatever is stored in the config/settings file
        data_stored = cls._get_stored_data()
        # filter out fields that are both stored and an attribute of the Container
        _data_fields = {
            fld for fld in fields(cls) if fld.init and fld.name in data_stored.keys()
        }
        # instantiate the sections and keep them in a dict
        # actually sections: dict[str, _ContainerSectionT]
        # but MyPy doesn't swallow that
        sections: dict[str, Any] = {
            fld.name: cls._instantiate_section(fld.type, data_stored[fld.name])
            for fld in _data_fields
        }

        # instantiate the Container with the sections
        return cls(**sections)

    @classmethod
    def _get_stored_data(cls) -> dict[str, Any]:
        """Get the data stored in the toml file"""
        data_stored: dict[str, Any] = {}

        if path := cls.filepath():
            with path.open(mode="rb") as fptr:
                data_stored = tomllib.load(fptr)
        else:
            # This situation can occur if no valid path was given as an argument, and
            # the default path is set to None.
            print(
                f"No path specified for {cls.kind_string().lower()}file; trying with defaults, but this may not work."
            )
        return data_stored

    @classmethod
    def _instantiate_section(
        cls: type[_ContainerT],
        class_to_instantiate: type[_ContainerSectionT],
        arg_dict: dict[str, Any],
    ) -> _ContainerSectionT:
        """Return an instance of class_to_instantiate, properly initialized"""
        # pre-condition: class_to_instantiate is the class of an initializable field of cls
        assert (
            len([f for f in fields(cls) if f.init and f.type == class_to_instantiate])
            > 0
        )

        field_set = {f.name for f in fields(class_to_instantiate) if f.init}
        filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
        return class_to_instantiate(**filtered_arg_dict)
