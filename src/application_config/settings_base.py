"""Module for handling settings."""
from dataclasses import fields, replace
from typing import Any, TypeVar

from pydantic.dataclasses import dataclass

from .container_base import ContainerBase, ContainerSectionBase

SettingsT = TypeVar("SettingsT", bound="SettingsBase")
SettingsSectionT = TypeVar("SettingsSectionT", bound="SettingsSectionBase")


@dataclass(frozen=True)
class SettingsSectionBase(ContainerSectionBase):
    """Base class for all SettingsSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class SettingsBase(ContainerBase):
    """Base class for main Settings class"""

    @classmethod
    def kind_string(cls: type[SettingsT]) -> str:
        "Return Settings"
        return "Settings"

    def update(self, changes: dict[str, dict[str, Any]]) -> None:
        "Update and save the settings with data specified in changes"
        # filter out fields that are both in changes and an attribute of the SettingsContainer
        _sections_to_update = {
            fld for fld in fields(self) if fld.init and fld.name in changes.keys()
        }

        # update the sections and keep them in a dict
        # actually sections: dict[str, _ContainerSectionT]
        # but MyPy doesn't swallow that
        updated_sections: dict[str, Any] = {
            fld.name: self._update_section(getattr(self, fld.name), changes[fld.name])
            for fld in _sections_to_update
        }
        new_settings = replace(self, **updated_sections)
        # store new settings in _ALL_CONTAINERS
        # save to file

    def _update_section(
        self, section: SettingsSectionT, changes: dict[str, Any]
    ) -> SettingsSectionT:
        "Update the settings section fieldname with data specified in changes"
        # filter out fields that are both in changes and an attribute of the SettingsSection
        assert isinstance(section, SettingsSectionBase)
        return replace(section, **changes)
