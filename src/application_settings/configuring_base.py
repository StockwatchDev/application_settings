"""Module for handling configuration."""
import sys
from typing import TypeVar

from application_settings.container_base import ContainerBase
from application_settings.container_section_base import (
    ContainerSectionBase,
    SectionTypeStr,
)

from .private._file_operations import FileFormat

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


ConfigT = TypeVar("ConfigT", bound="ConfigBase")
ConfigT.__doc__ = "Represents ConfigBase and all subclasses"


class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""

    @override
    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return 'Config'"""
        return "Config"


class ConfigBase(ContainerBase):
    """Base class for main Config class"""

    @override
    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return 'Config'"""
        return "Config"

    @override
    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""
        return FileFormat.TOML
