"""Abstract base class for sections to be added to containers and container sections for configuration and settings."""
import sys
from abc import ABC, abstractmethod
from dataclasses import is_dataclass
from typing import Any, Literal, Optional, cast

from loguru import logger

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


SectionTypeStr = Literal["Config", "Settings"]


class ContainerSectionBase(ABC):
    """Base class for all ContainerSection classes"""

    @classmethod
    @abstractmethod
    def kind_string(cls) -> SectionTypeStr:
        """Return either 'Config' or 'Settings'"""

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
        _check_dataclass_decorator(self)
        _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
        subsections = [
            attr
            for attr in vars(self).values()
            if isinstance(attr, ContainerSectionBase)
        ]
        for subsec in subsections:
            subsec._set()  # pylint: disable=protected-access
        return self


def _check_dataclass_decorator(obj: Any) -> None:
    if not (is_dataclass(obj)):
        raise TypeError(
            f"{obj} is not a dataclass instance; did you forget to add "
            f"'@dataclass(frozen=True)' when you defined {obj.__class__}?."
        )
    if not obj.__class__.__dataclass_params__.frozen:
        raise TypeError(
            f"{obj} is not a frozen dataclass instance; did you forget "
            f"to add '(frozen=True)' when you defined {obj.__class__}?."
        )


_ALL_CONTAINER_SECTION_SINGLETONS: dict[int, ContainerSectionBase] = {}
