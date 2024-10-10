"""Module for loading and retrieving parameters for configuration and settings."""

from importlib.metadata import version

from attributes_doc import attributes_doc
from loguru import logger
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from application_settings.configuring_base import ConfigBase, ConfigSectionBase, ConfigT
from application_settings.convenience import (
    config_filepath_from_cli,
    parameters_folderpath_from_cli,
    settings_filepath_from_cli,
    use_standard_logging,
)
from application_settings.parameter_kind import ParameterKind, ParameterKindStr
from application_settings.settings_base import (
    SettingsBase,
    SettingsSectionBase,
    SettingsT,
)
from application_settings.type_notation_helper import PathOpt, PathOrStr

LOGGER_NAME = "application-settings"
logger.disable(LOGGER_NAME)

__version__ = version("application-settings")


__all__ = [
    "ConfigSectionBase",
    "ConfigBase",
    "ConfigT",
    "ParameterKind",
    "PathOpt",
    "PathOrStr",
    "ParameterKindStr",
    "SettingsSectionBase",
    "SettingsBase",
    "SettingsT",
    "ValidationError",
    "attributes_doc",
    "config_filepath_from_cli",
    "dataclass",
    "settings_filepath_from_cli",
    "parameters_folderpath_from_cli",
    "use_standard_logging",
]
