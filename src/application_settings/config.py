"""Defines config parameters for application_settings"""

# pylint: disable=duplicate-code

import sys
from typing import Any, Optional, cast

from attributes_doc import attributes_doc
from loguru import logger
from pydantic.dataclasses import dataclass

from application_settings.parameter_kind import ParameterKind, ParameterKindStr
from application_settings.protocols import ContainerSection

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# This is not an example how to implement a ConfigSection
# because class ApplicationSettingsConfigSection (re-)implements all methods of ConfigSectionBase.
# This is done so that this class will meet the ConfigSection protocol
# yet does not inherit from ConfigSectionBase and therewith prevents circular imports
# (because ConfigSectionBase imports ApplicationSettingsConfig).


@attributes_doc
@dataclass(frozen=True)
class ApplicationSettingsConfigSection:
    """Config parameters for the application_settings library package"""

    default_fileformat_config: str = "toml"
    """File format to use for config files when no filepath is specified; either 'toml' or 'json'"""

    default_fileformat_settings: str = "json"
    """File format to use for settings files when no filepath is specified; either 'toml' or 'json'"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return either ParameterKind.CONFIG"""
        return ParameterKind.CONFIG

    @classmethod
    def kind_string(cls) -> ParameterKindStr:
        """Return either 'Config' or 'Settings'"""
        return cls.kind().value

    @classmethod
    def get(cls) -> Self:
        """Get the singleton; if not existing, create it. Loading from file only done for a container."""

        if (_the_container_or_none := cls._get()) is None:
            # no config section has been made yet
            cls.get_without_load()
            # so let's instantiate one and keep it in the global store
            return cls._create_instance()
        return _the_container_or_none

    @classmethod
    def get_without_load(cls) -> None:
        """Get has been called on a section before a load was done; handle this."""
        # get() is called on a Section but the application
        # has not yet created or loaded a config.
        logger.warning(
            f"{cls.kind_string()} section {cls.__name__} accessed before data has been loaded; "
            f"will try to load via command line parameter '--{cls.__name__}_file'"
        )

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        """Create a new dataclass instance using data and set the singleton."""
        return cls(**data)._set()

    @classmethod
    def _get(
        cls,
    ) -> Optional[Self]:  # pylint: disable=consider-alternative-union-syntax
        """Get the singleton."""
        if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
            return cast(Self, the_container)
        return None

    @classmethod
    def _create_instance(
        cls, throw_if_file_not_found: bool = False  # pylint: disable=unused-argument
    ) -> Self:
        """Create a new ContainerSection with default values. Likely that this is wrong."""
        return cls.set({})

    def _set(self) -> Self:
        """Store the singleton."""
        # no need to do the check on dataclass decorator, I have it :)
        _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
        # ApplicationSettingsConfigSection does not have subsections
        return self


_ALL_CONTAINER_SECTION_SINGLETONS: dict[int, ContainerSection] = {}


# TODO:
# - create module _singleton that holds the singleton stores
# - convert ConfigT and ConfigSectionT etc to protocols
# - adapt tests
# - silence logging until application settings config has been loaded
