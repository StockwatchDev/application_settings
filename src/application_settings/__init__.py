"""Module for loading and retrieving parameters for configuration and settings."""

from importlib.metadata import version

from .configuring_base import ConfigBase, ConfigSectionBase
from .container_section_base import SectionTypeStr
from .settings_base import SettingsBase, SettingsSectionBase
from .type_notation_helper import PathOpt, PathOrStr

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
