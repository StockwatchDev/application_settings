"""Module for handling settings."""
from typing import TypeVar

from application_settings.container_base import ContainerBase, FileFormat
from application_settings.container_section_base import (
    ContainerSectionBase,
    SectionTypeStr,
)

SettingsT = TypeVar("SettingsT", bound="SettingsBase")
SettingsT.__doc__ = "Represents SettingsBase and all subclasses"


class SettingsSectionBase(ContainerSectionBase):
    """Base class for all SettingsSection classes (so that we can bound a TypeVar)"""

    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return 'Settings'"""
        return "Settings"


class SettingsBase(ContainerBase):
    """Base class for main Settings class"""

    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return 'Settings'"""
        return "Settings"

    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""
        return FileFormat.JSON
