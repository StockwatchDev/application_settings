"""Module for handling configuration."""

import sys
from typing import TypeVar

from application_settings.container_base import ContainerBase
from application_settings.container_section_base import ContainerSectionBase
from application_settings.parameter_kind import ParameterKind

from ._private.file_operations import FileFormat

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


ConfigT = TypeVar("ConfigT", bound="ConfigBase")
ConfigT.__doc__ = "Represents ConfigBase and all subclasses"


class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""

    @classmethod
    def kind(cls) -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG


class ConfigBase(ContainerBase):
    """Base class for main Config class"""

    @classmethod
    def kind(cls) -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG

    @override
    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""
        return FileFormat.TOML
