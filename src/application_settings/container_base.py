# pylint: disable=consider-alternative-union-syntax
"""Base class for a container (= root section) for configuration and settings."""
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict
from enum import Enum, unique
from pathlib import Path
from re import sub
from typing import Any, Literal, Optional, TypeVar, cast

import tomli_w
from pathvalidate import is_valid_filepath
from pydantic.dataclasses import dataclass

from .container_section_base import ContainerSectionBase
from .type_notation_helper import PathOpt, PathOrStr

if sys.version_info >= (3, 11):
    import tomllib
    from typing import Self
else:
    import tomli as tomllib

    Self = TypeVar("Self", bound="ContainerBase")


@unique
class FileFormat(Enum):
    "File formats that are supported by application_settings"
    TOML = "toml"
    JSON = "json"


ContainerTypeStr = Literal["Config", "Settings"]


@dataclass(frozen=True)
class ContainerBase(ContainerSectionBase, ABC):
    """Base class for Config and Settings container classes"""

    @classmethod
    @abstractmethod
    def kind_string(cls) -> ContainerTypeStr:
        "Return either 'Config' or 'Settings'"

    @classmethod
    @abstractmethod
    def default_file_format(cls) -> FileFormat:
        "Return the default file format"

    @classmethod
    def default_foldername(cls) -> str:
        """Return the class name without kind_string, lowercase, with a preceding dot and underscores to seperate words."""
        if (kind_str := cls.kind_string()) == cls.__name__:
            return f".{kind_str.lower()}"
        return (
            "."
            + sub("(?<!^)(?=[A-Z])", "_", cls.__name__.replace(kind_str, "")).lower()
        )

    @classmethod
    def default_filename(cls) -> str:
        """Return the kind_string, lowercase, with the extension that fits the file_format."""
        return f"{cls.kind_string().lower()}.{cls.default_file_format().value}"

    @classmethod
    def default_filepath(cls) -> PathOpt:
        """Return the fully qualified path for the config/settingsfile: e.g. ~/.example/config.toml"""
        return Path.home() / cls.default_foldername() / cls.default_filename()

    @classmethod
    def set_filepath(cls, file_path: PathOrStr = "", reload: bool = False) -> None:
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

    if sys.version_info >= (3, 11):

        @classmethod
        def get(cls, reload: bool = False) -> Self:
            """Get the singleton; if not existing, create it."""

            if (_the_container_or_none := cls._get()) is None or reload:
                # no config has been made yet or it needs to be reloaded,
                # so let's instantiate one and keep it in the global store
                return cls._create_instance()
            return _the_container_or_none

        @classmethod
        def update(cls, changes: dict[str, dict[str, Any]]) -> Self:
            "Update and save the settings with data specified in changes; not meant for config"
            return cls.get()._update(changes)  # pylint: disable=protected-access

        @classmethod
        def _get(cls) -> Self | None:
            """Get the singleton."""
            if the_container := _ALL_CONTAINERS.get(id(cls)):
                return cast(Self, the_container)
            return None

        def _update(self, changes: dict[str, dict[str, Any]]) -> Self:
            "Update and save the settings with data specified in changes; not meant for config"
            new_container = super()._update(changes)
            new_container._set()._save()  # pylint: disable=protected-access,no-member
            return new_container

        @classmethod
        def _create_instance(cls) -> Self:
            """Load stored data, instantiate the Container with it, store it in the singleton and return it."""

            # get whatever is stored in the config/settings file
            data_stored = cls._get_stored_data()
            # instantiate and store the Container with the stored data
            return cls(**data_stored)._set()

        def _set(self) -> Self:
            """Store the singleton."""
            _ALL_CONTAINERS[id(self.__class__)] = self
            return self

        def _save(self) -> Self:
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
            return self

    else:

        @classmethod
        def get(cls: type[Self], reload: bool = False) -> Self:
            """Get the singleton; if not existing, create it."""

            if (_the_container_or_none := cls._get()) is None or reload:
                # no config has been made yet or it needs to be reloaded,
                # so let's instantiate one and keep it in the global store
                return cls._create_instance()
            return _the_container_or_none

        @classmethod
        def update(cls: type[Self], changes: dict[str, dict[str, Any]]) -> Self:
            "Update and save the settings with data specified in changes; not meant for config"
            return cls.get()._update(changes)  # pylint: disable=protected-access

        @classmethod
        def _get(cls: type[Self]) -> Optional[Self]:
            """Get the singleton."""
            if the_container := _ALL_CONTAINERS.get(id(cls)):
                return cast(Self, the_container)
            return None

        def _update(self: Self, changes: dict[str, dict[str, Any]]) -> Self:
            "Update and save the settings with data specified in changes; not meant for config"
            new_container = super()._update(changes)
            new_container._set()._save()  # pylint: disable=protected-access,no-member
            return new_container

        @classmethod
        def _create_instance(cls: type[Self]) -> Self:
            """Load stored data, instantiate the Container with it, store it in the singleton and return it."""

            # get whatever is stored in the config/settings file
            data_stored = cls._get_stored_data()
            # instantiate and store the Container with the stored data
            return cls(**data_stored)._set()

        def _set(self: Self) -> Self:
            """Store the singleton."""
            _ALL_CONTAINERS[id(self.__class__)] = self
            return self

        def _save(self: Self) -> Self:
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
            return self

    @classmethod
    def _get_stored_data(cls) -> dict[str, Any]:
        """Get the data stored in the parameter file"""
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


_ALL_CONTAINERS: dict[int, Any] = {}
_ALL_PATHS: dict[int, PathOpt] = {}
