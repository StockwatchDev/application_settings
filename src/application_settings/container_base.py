"""Base class for a container (= root section) for configuration and settings."""

import sys
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from re import sub
from typing import Any

from loguru import logger
from pathvalidate import is_valid_filepath

from application_settings.container_section_base import ContainerSectionBase
from application_settings.type_notation_helper import PathOpt, PathOrStr

from ._private.file_operations import FileFormat
from ._private.file_operations import load as _do_load
from ._private.file_operations import save as _do_save

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class ContainerBase(ContainerSectionBase, ABC):
    """Base class for Config and Settings container classes"""

    @classmethod
    @abstractmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""

    @classmethod
    def default_foldername(cls) -> str:
        """Return the class name without kind_string, lowercase, with a preceding dot and underscores to seperate words."""
        if (kind_str := cls.kind_string()) == cls.__name__:
            return f".{kind_str.lower()}"
        return (
            "."
            + sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__.replace(kind_str, "")).lower()
        )

    @classmethod
    def default_filename(cls) -> str:
        """Return the kind_string, lowercase, with the extension that fits the file_format."""
        return f"{cls.kind_string().lower()}.{cls.default_file_format().value}"

    @classmethod
    def default_filepath(cls) -> PathOpt:
        """Return the fully qualified default path for the config/settingsfile

        E.g. ~/.example/config.toml.
        If you prefer to not have a default path then overwrite this method and return None.
        """
        return Path.home() / cls.default_foldername() / cls.default_filename()

    @classmethod
    def set_filepath(cls, file_path: PathOrStr = "", load: bool = False) -> None:
        """Set the path for the file (a singleton).

        Raises:
            ValueError: if file_path is not a valid path for the OS running the code
        """

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

        if load:
            cls.load()
        else:
            if cls._get() is not None:
                logger.info(
                    f"Filepath has been set the but file is not loaded into the {cls.kind_string()}."
                )

    @classmethod
    def filepath(cls) -> PathOpt:
        """Return the path for the file that holds the config / settings."""
        return _ALL_PATHS.get(id(cls), cls.default_filepath())

    @classmethod
    def load(cls, throw_if_file_not_found: bool = False) -> Self:
        """Create a new singleton, try to load parameter values from file.

        Raises:
            FileNotFoundError: if throw_if_file_not_found == True and filepath() cannot be resolved
            TOMLDecodeError: if FileFormat == TOML and the file is not a valid toml document
            JSONDecodeError: if FileFormat == JSON and the file is not a valid json document
            ValidationError: if a parameter value in the file cannot be coerced into the specified parameter type
        """
        return cls._create_instance(throw_if_file_not_found)

    @classmethod
    def get_without_load(cls) -> None:
        """Get has been called on a section before a load was done; handle this."""
        logger.warning(
            f"{cls.kind_string()} {cls.__name__} accessed before data has been loaded; "
            f"will try implicit loading with {cls.filepath()}."
        )

    @classmethod
    def _create_instance(cls, throw_if_file_not_found: bool = False) -> Self:
        """Load stored data, instantiate the Container with it, store it in the singleton and return it."""

        # get whatever is stored in the config/settings file
        data_stored = cls._get_saved_data(throw_if_file_not_found)
        # instantiate and store the Container with the stored data
        return cls.set(data_stored)

    def _save(self) -> Self:
        """Private method to save the singleton to file."""
        if path := self.filepath():
            path.parent.mkdir(parents=True, exist_ok=True)
            # in self._set(), which normally is always executed, we ensured that
            # self is a dataclass instance
            _do_save(path, asdict(self))  # type: ignore[call-overload]
        else:
            # This situation can occur if no valid path was given as an argument, and
            # the default path is set to None.
            raise RuntimeError(
                f"No path specified for {self.kind_string().lower()} file, cannot be saved."
            )
        return self

    @classmethod
    def _get_saved_data(cls, throw_if_file_not_found: bool = False) -> dict[str, Any]:
        """Get the data stored in the parameter file"""
        return _do_load(cls.kind(), cls.filepath(), throw_if_file_not_found)


_ALL_PATHS: dict[int, PathOpt] = {}
