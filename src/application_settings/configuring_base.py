"""Module for handling configuration."""

import sys

from attributes_doc import attributes_doc
from pydantic.dataclasses import dataclass

from application_settings._private.file_operations import FileFormat
from application_settings.container_base import ParameterContainerBase
from application_settings.container_section_base import ParameterContainerSectionBase
from application_settings.parameter_kind import ParameterKind
from application_settings.parametrization import ApplicationConfigSection

if sys.version_info >= (3, 10):
    from dataclasses import KW_ONLY


@dataclass(frozen=True)
class ConfigSectionBase(ParameterContainerSectionBase):
    """Base class for ConfigSection classes, implements the abstract methods of the base(s)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG


@attributes_doc
@dataclass(frozen=True)
class ConfigBase(ParameterContainerBase):
    """Base class for main Config class, implements the abstract methods of the base(s)"""

    if sys.version_info >= (3, 10):
        _: KW_ONLY
    application_config: ApplicationConfigSection = ApplicationConfigSection()
    """Holds the configuration parameters for application_settings"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG

    @staticmethod
    def default_file_format() -> FileFormat:
        """Return the default file format"""  # disable=duplicate-code
        return FileFormat.TOML
