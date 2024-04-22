"""Module for handling settings."""
# from dataclasses import replace
from pydantic import BaseModel

from application_settings.container_base import ContainerBase
from application_settings.container_section_base import (
    ContainerSectionBase,
)

from ._private.file_operations import FileFormat


class SettingsSectionBase(ContainerSectionBase):
    """Base class for all SettingsSection classes (so that we can bound a TypeVar)"""

    @classmethod
    def kind_string(cls):
        """Return 'Settings'"""
        return "Settings"


class SettingsBase(ContainerBase):
    """Base class for main Settings class"""

    @classmethod
    def kind_string(cls):
        """Return 'Settings'"""
        return "Settings"

    @classmethod
    def default_file_format(cls):
        """Return the default file format"""
        return FileFormat.JSON

    @classmethod
    def update(cls, changes):
        """Update the settings with data specified in changes and save.

        Raises:
            RuntimeError: if filepath() == None
        """
        return (
            _update_settings_section(  # pylint: disable=protected-access
                cls.get(), changes
            )
            ._set()
            ._save()
        )


def _update_settings_section(
    the_section: BaseModel, changes
):
    "Update parameters and sections with data specified in changes"
    # in the_section._set(), which normally is always executed, we ensured that
    # the_section is a dataclass instance and hence we can ignore type errors
    print(the_section)
    updated = the_section.copy(update=changes)
    print(updated)
    return the_section.copy(update=changes)  # type: ignore[type-var]
