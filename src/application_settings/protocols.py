"""Defines protocol classes for containers and sections for configuration and settings."""

import sys
from typing import Any, Protocol

from application_settings.parameter_kind import ParameterKind, ParameterKindStr
from application_settings.type_notation_helper import PathOpt, PathOrStr

from ._private.file_operations import FileFormat

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class ContainerSection(Protocol):
    """Protocol for a ContainerSection"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return either ParameterKind.CONFIG or ParameterKind.SETTINGS"""

    @classmethod
    def kind_string(cls) -> ParameterKindStr:
        """Return either 'Config' or 'Settings'"""

    @classmethod
    def get(cls) -> Self:
        """Get the singleton; if not existing, create it. Loading from file only done for a container."""

    @classmethod
    def get_without_load(cls) -> None:
        """Get has been called on a section before a load was done; handle this."""

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        """Create a new dataclass instance using data and set the singleton."""


class Container(ContainerSection, Protocol):
    """Protocol for a container"""

    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""

    @classmethod
    def default_foldername(cls) -> str:
        """Return the class name without kind_string, lowercase, with a preceding dot
        and underscores to seperate words."""

    @classmethod
    def default_filename(cls) -> str:
        """Return the kind_string, lowercase, with the extension that fits the file_format."""

    @classmethod
    def default_filepath(cls) -> PathOpt:
        """Return the fully qualified default path for the config/settingsfile

        E.g. ~/.example/config.toml.
        If you prefer to not have a default path then overwrite this method and return None.
        """

    @classmethod
    def set_filepath(cls, file_path: PathOrStr = "", load: bool = False) -> None:
        """Set the path for the file (a singleton).

        Raises:
            ValueError: if file_path is not a valid path for the OS running the code
        """

    @classmethod
    def filepath(cls) -> PathOpt:
        """Return the path for the file that holds the config / settings."""

    @classmethod
    def load(cls, throw_if_file_not_found: bool = False) -> Self:
        """Create a new singleton, try to load parameter values from file.

        Raises:
            FileNotFoundError: if throw_if_file_not_found == True and filepath() cannot be resolved
            TOMLDecodeError: if FileFormat == TOML and the file is not a valid toml document
            JSONDecodeError: if FileFormat == JSON and the file is not a valid json document
            ValidationError: if a parameter value in the file cannot be coerced into the specified parameter type
        """

    @classmethod
    def get_without_load(cls) -> None:
        """Get has been called on a section before a load was done; handle this."""
