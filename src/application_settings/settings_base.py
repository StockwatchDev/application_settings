"""Module for handling settings."""
from typing import TypeVar

from pydantic.dataclasses import dataclass

from .container_base import ContainerBase, ContainerTypeStr, FileFormat
from .container_section_base import ContainerSectionBase

SettingsT = TypeVar("SettingsT", bound="SettingsBase")
SettingsSectionT = TypeVar("SettingsSectionT", bound="SettingsSectionBase")


@dataclass(frozen=True)
class SettingsSectionBase(ContainerSectionBase):
    """Base class for all SettingsSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class SettingsBase(ContainerBase):
    """Base class for main Settings class"""

    @classmethod
    def kind_string(cls: type[SettingsT]) -> ContainerTypeStr:
        "Return 'Settings'"
        return "Settings"

    @classmethod
    def default_file_format(cls: type[SettingsT]) -> FileFormat:
        "Return the default file format"
        return FileFormat.JSON
