"""Module for handling configuration."""
from typing import TypeVar

from pydantic.dataclasses import dataclass

from .container_base import ContainerBase, ContainerSectionBase

ConfigT = TypeVar("ConfigT", bound="ConfigBase")
ConfigSectionT = TypeVar("ConfigSectionT", bound="ConfigSectionBase")


@dataclass(frozen=True)
class ConfigSectionBase(ContainerSectionBase):
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class ConfigBase(ContainerBase):
    """Base class for main Config class"""

    @classmethod
    def kind_string(cls: type[ConfigT]) -> str:
        "Return Config"
        return "Config"
