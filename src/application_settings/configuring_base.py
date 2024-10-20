"""Module for handling configuration."""

from typing import TypeVar

from loguru import logger

from application_settings.config import ApplicationSettingsConfigSection
from application_settings.container_base import ContainerBase
from application_settings.container_section_base import ContainerSectionBase
from application_settings.parameter_kind import ParameterKind

from ._private.file_operations import FileFormat

ConfigT = TypeVar("ConfigT", bound="ConfigBase")
ConfigT.__doc__ = "Represents ConfigBase and all subclasses"


class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes, implements the abstract methods of the base(s)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG


class ConfigBase(ContainerBase):
    """Base class for main Config class, implements the abstract methods of the base(s)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG

    @staticmethod
    def default_file_format() -> FileFormat:
        """Return the default file format"""  # disable=duplicate-code
        if (
            fmt := ApplicationSettingsConfigSection.get().default_fileformat_config
        ) == FileFormat.TOML.value:
            return FileFormat.TOML
        if fmt == FileFormat.JSON.value:
            return FileFormat.JSON
        logger.error(
            f"Unknown file format specified in ApplicationSettingsConfig; will assume {FileFormat.TOML} format."
        )
        return FileFormat.TOML
