"""Module for loading and retrieving parameters for configuration and settings."""

from loguru import logger
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from application_settings.configuring_base import ConfigBase, ConfigSectionBase
from application_settings.convenience import (
    config_filepath_from_cli,
    parameters_folderpath_from_cli,
    settings_filepath_from_cli,
    use_standard_logging,
)
from application_settings.settings_base import (
    SettingsBase,
    SettingsSectionBase,
)

LOGGER_NAME = "application-settings"
logger.disable(LOGGER_NAME)

__version__ = "0.5.0.dev0"

__all__ = [
    "ConfigSectionBase",
    "ConfigBase",
    # "ConfigT",
    # "PathOpt",
    # "PathOrStr",
    # "SectionTypeStr",
    "SettingsSectionBase",
    "SettingsBase",
    # "SettingsT",
    "ValidationError",
    # "attributes_doc",
    "config_filepath_from_cli",
    "dataclass",
    "settings_filepath_from_cli",
    "parameters_folderpath_from_cli",
    "use_standard_logging",
]
