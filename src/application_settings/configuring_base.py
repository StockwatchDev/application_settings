"""Module for handling configuration."""
from typing import Any, TypeVar

from pydantic.dataclasses import dataclass

from .container_base import ContainerBase, ContainerTypeStr, FileFormat
from .container_section_base import ContainerSectionBase

ConfigT = TypeVar("ConfigT", bound="ConfigBase")
ConfigSectionT = TypeVar("ConfigSectionT", bound="ConfigSectionBase")


@dataclass(frozen=True)
class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class ConfigBase(ContainerBase):
    """Base class for main Config class"""

    @classmethod
    def kind_string(cls: type[ConfigT]) -> ContainerTypeStr:
        "Return 'Config'"
        return "Config"

    @classmethod
    def default_file_format(cls: type[ConfigT]) -> FileFormat:
        "Return the default file format"
        return FileFormat.TOML

    @classmethod
    def update(
        cls: type["ConfigBase"], changes: dict[str, dict[str, Any]]
    ) -> "ConfigBase":
        "Update and save the settings with data specified in changes; not meant for config"
        raise TypeError(
            "Configs should not be updated runtime; consider converting to settings."
        )
