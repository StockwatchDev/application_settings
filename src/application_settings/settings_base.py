"""Module for handling settings."""
from typing import TypeVar

from pydantic.dataclasses import dataclass

from .container_base import ContainerBase, ContainerSectionBase, ContainerTypeStr

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
