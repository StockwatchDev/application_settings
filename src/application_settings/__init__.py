"""Module for loading and retrieving configuration."""

from importlib.metadata import version

from .configuring_base import ConfigBase, ConfigSectionBase, ConfigSectionT, ConfigT
from .settings_base import (
    SettingsBase,
    SettingsSectionBase,
    SettingsSectionT,
    SettingsT,
)
from .type_notation_helper import PathOpt, PathOrStr

__version__ = version("application_settings")

__all__ = [
    "ConfigSectionT",
    "ConfigT",
    "ConfigSectionBase",
    "ConfigBase",
    "PathOpt",
    "PathOrStr",
    "SettingsSectionT",
    "SettingsT",
    "SettingsSectionBase",
    "SettingsBase",
]
