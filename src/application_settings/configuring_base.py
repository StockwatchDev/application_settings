"""Module for handling configuration."""
from typing import Any, TypeVar

from pydantic.dataclasses import dataclass

from application_settings.container_base import ContainerBase, FileFormat
from application_settings.container_section_base import (
    ContainerSectionBase,
    SectionTypeStr,
)

ConfigT = TypeVar("ConfigT", bound="ConfigBase")
ConfigT.__doc__ = "Represents ConfigBase and all subclasses"


@dataclass(frozen=True)
class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""

    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return 'Config'"""
        return "Config"


@dataclass(frozen=True)
class ConfigBase(ContainerBase):
    """Base class for main Config class"""

    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return 'Config'"""
        return "Config"

    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""
        return FileFormat.TOML

    @classmethod
    def update(
        cls: type["ConfigBase"], changes: dict[str, dict[str, Any]]
    ) -> "ConfigBase":
        """Update and save the settings with data specified in changes

        Raises:

        * TypeError: update not applicable for a Config class
        """

        raise TypeError(
            "Configs should not be updated runtime; consider converting to settings."
        )
