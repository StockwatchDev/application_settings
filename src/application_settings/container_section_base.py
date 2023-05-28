"""Base class for sections to be added to containers and container sections for configuration and settings."""
import sys
from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Any, Literal, Optional, cast

from pydantic.dataclasses import dataclass

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


SectionTypeStr = Literal["Config", "Settings"]


@dataclass(frozen=True)
class ContainerSectionBase(ABC):
    """Base class for all ContainerSection classes"""

    @classmethod
    @abstractmethod
    def kind_string(cls) -> SectionTypeStr:
        "Return either 'Config' or 'Settings'"

    @classmethod
    def get(cls) -> Self:
        """Get the singleton; if not existing, create it. Reloading only useful for a container."""

        if (_the_container_or_none := cls._get()) is None:
            # no config section has been made yet,
            # so let's instantiate one and keep it in the global store
            return cls._create_instance()
        return _the_container_or_none

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        """Create a new dataclass instance using data and set the singleton."""
        return cls(**data)._set()

    @classmethod
    def update(cls, changes: dict[str, Any]) -> Self:
        "Update the settings with data specified in changes; not meant for config"
        return cls.get()._update(changes)._set()  # pylint: disable=protected-access

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
        # This situation can occur if get() is called on a Section but the application
        # has not yet created or loaded a config.
        print(
            f"Section {cls.__name__} accessed before data has been set by the application."
        )
        return cls().set({})

    def _set(self) -> Self:
        """Store the singleton."""
        _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
        subsections = [
            attr
            for attr in vars(self).values()
            if isinstance(attr, ContainerSectionBase)
        ]
        for subsec in subsections:
            subsec._set()  # pylint: disable=protected-access
        return self

    def _update(self, changes: dict[str, Any]) -> Self:
        "Update parameters and sections with data specified in changes; not meant for config"
        return replace(self, **changes)


_ALL_CONTAINER_SECTION_SINGLETONS: dict[int, ContainerSectionBase] = {}
