"""Module for loading and retrieving configuration."""

from importlib.metadata import version

from .configuring_base import ConfigBase, ConfigSectionBase, TConfig, TConfigSection

__version__ = version("application_settings")

__all__ = [
    "TConfigSection",
    "TConfig",
    "ConfigSectionBase",
    "ConfigBase",
]
