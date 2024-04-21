"""Module for handling configuration."""

from application_settings.container_base import ContainerBase
from application_settings.container_section_base import (
    ContainerSectionBase,
)

from ._private.file_operations import FileFormat


class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""

    @classmethod
    def kind_string(cls):
        """Return 'Config'"""
        return "Config"


class ConfigBase(ContainerBase):
    """Base class for main Config class"""

    @classmethod
    def kind_string(cls):
        """Return 'Config'"""
        return "Config"

    @classmethod
    def default_file_format(cls):
        """Return the default file format"""
        return FileFormat.TOML
