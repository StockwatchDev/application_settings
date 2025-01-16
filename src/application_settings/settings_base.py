"""Module for handling settings."""

import sys
from dataclasses import replace
from typing import Any, TypeVar

from application_settings.container_base import ParameterContainerBase
from application_settings.container_section_base import ParameterContainerSectionBase
from application_settings.parameter_kind import ParameterKind
from application_settings.parametrization import ApplicationSettingsSection
from application_settings.protocols import UpdateableParameterContainerProtocol

from ._private.file_operations import FileFormat

if sys.version_info >= (3, 10):
    from dataclasses import KW_ONLY

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

UpdateableParameterContainerT = TypeVar(
    "UpdateableParameterContainerT", bound=UpdateableParameterContainerProtocol
)


class SettingsSectionBase(ParameterContainerSectionBase):
    """Base class for SettingsSection classes, implements the abstract methods of the base(s)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.SETTINGS"""
        return ParameterKind.SETTINGS


class SettingsBase(ParameterContainerBase):
    """Base class for main Settings class, implements the abstract methods of the base(s)"""

    if sys.version_info >= (3, 10):
        _: KW_ONLY
    application_settings: ApplicationSettingsSection = ApplicationSettingsSection()
    """Holds the settings parameters for application_settings"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.SETTINGS"""
        return ParameterKind.SETTINGS

    @classmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""
        return FileFormat.JSON

    @classmethod
    def update(cls, changes: dict[str, Any]) -> Self:
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
    the_settings_container: UpdateableParameterContainerT,
    changes: dict[str, Any],
) -> UpdateableParameterContainerT:
    "Update parameters and sections with data specified in changes"
    # in the_section._set(), which normally is always executed, we ensured that
    # the_section is a dataclass instance and hence we can ignore type errors
    return replace(the_settings_container, **changes)  # type: ignore[type-var]
