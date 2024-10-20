"""Module for handling settings."""

import sys
from dataclasses import replace
from typing import Any, TypeVar

from loguru import logger

from application_settings.config import ApplicationSettingsConfigSection
from application_settings.container_base import ContainerBase
from application_settings.container_section_base import ContainerSectionBase
from application_settings.parameter_kind import ParameterKind

from ._private.file_operations import FileFormat

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


SettingsT = TypeVar("SettingsT", bound="SettingsBase")
SettingsT.__doc__ = "Represents SettingsBase and all subclasses"


class SettingsSectionBase(ContainerSectionBase):
    """Base class for all SettingsSection classes (so that we can bound a TypeVar)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.SETTINGS"""
        return ParameterKind.SETTINGS


class SettingsBase(ContainerBase):
    """Base class for main Settings class"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.SETTINGS"""
        return ParameterKind.SETTINGS

    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""
        if (
            fmt := ApplicationSettingsConfigSection.get().default_fileformat_settings
        ) == FileFormat.TOML.value:
            return FileFormat.TOML
        if fmt == FileFormat.JSON.value:
            return FileFormat.JSON
        logger.error(
            f"Unknown file format specified in ApplicationSettingsConfig; will assume {FileFormat.JSON} format."
        )
        return FileFormat.JSON

    @classmethod
    def update(cls, changes: dict[str, Any]) -> Self:
        """Update the settings with data specified in changes and save.

        Raises:
            RuntimeError: if filepath() == None
        """
        return (
            _update_settings_section(  # pylint: disable=protected-access
                cls.get(), changes
            )
            ._set()
            ._save()
        )


def _update_settings_section(
    the_section: SettingsT, changes: dict[str, Any]
) -> SettingsT:
    "Update parameters and sections with data specified in changes"
    # in the_section._set(), which normally is always executed, we ensured that
    # the_section is a dataclass instance and hence we can ignore type errors
    return replace(the_section, **changes)  # type: ignore[type-var]
