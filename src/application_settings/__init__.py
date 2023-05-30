"""Module for loading and retrieving parameters for configuration and settings."""

from importlib.metadata import version

from application_settings.configuring_base import ConfigBase, ConfigSectionBase
from application_settings.container_section_base import SectionTypeStr
from application_settings.settings_base import SettingsBase, SettingsSectionBase
from application_settings.type_notation_helper import PathOpt, PathOrStr

__version__ = version("application_settings")

__all__ = [
    "ConfigSectionBase",
    "ConfigBase",
    "PathOpt",
    "PathOrStr",
    "SettingsSectionBase",
    "SettingsBase",
    "SectionTypeStr",
]
