"""Module for loading and retrieving configuration."""

from importlib.metadata import version

from .configuring_base import ConfigBase, ConfigSectionBase, ConfigSectionT, ConfigT

__version__ = version("application_config")

__all__ = [
    "ConfigSectionT",
    "ConfigT",
    "ConfigSectionBase",
    "ConfigBase",
]
