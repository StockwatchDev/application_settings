"""Base class for sections to be added to containers and container sections for configuration and settings."""
import sys
from dataclasses import replace
from typing import Any, TypeVar, cast

from pydantic.dataclasses import dataclass

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = TypeVar("Self", bound="ContainerSectionBase")


@dataclass(frozen=True)
class ContainerSectionBase:
    """Base class for all ContainerSection classes"""

    if sys.version_info >= (3, 11):

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
        def update(cls, changes: dict[str, dict[str, Any]]) -> Self:
            "Update the settings with data specified in changes; not meant for config"
            return cls.get()._update(changes)._set()  # pylint: disable=protected-access

        @classmethod
        def _get(cls) -> Self | None:
            """Get the singleton."""
            if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
                return cast(Self, the_container)
            return None

        @classmethod
        def _create_instance(cls) -> Self:
            """Instantiate the ContainerSection, store it in the singleton and return it. Likely that this is wrong."""

            # instantiate and store the ContainerSection with default values
            return cls()._set()

        def _set(self) -> Self:
            """Store the singleton."""
            _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
            subsections = [
                attr for attr in vars(self) if isinstance(attr, ContainerSectionBase)
            ]
            for subsec in subsections:
                subsec._set()  # pylint: disable=protected-access
            return self

        def _update(self, changes: dict[str, dict[str, Any]]) -> Self:
            "Update parameters and sections with data specified in changes; not meant for config"
            return replace(self, **changes)

    else:

        @classmethod
        def get(cls: type[Self]) -> Self:
            """Get the singleton; if not existing, create it. Reloading only useful for a container."""

            if (_the_container_or_none := cls._get()) is None:
                # no config section has been made yet,
                # so let's instantiate one and keep it in the global store
                return cls._create_instance()
            return _the_container_or_none

        @classmethod
        def set(cls: type[Self], data: dict[str, Any]) -> Self:
            """Create a new dataclass instance using data and set the singleton."""
            return cls(**data)._set()

        @classmethod
        def update(cls: type[Self], changes: dict[str, dict[str, Any]]) -> Self:
            "Update the settings with data specified in changes; not meant for config"
            return cls.get()._update(changes)._set()  # pylint: disable=protected-access

        if sys.version_info < (3, 10):
            from typing import Union  # pylint: disable=import-outside-toplevel

            @classmethod
            def _get(cls: type[Self]) -> Union[Self, None]:
                """Get the singleton."""
                if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
                    return cast(Self, the_container)
                return None

        else:

            @classmethod
            def _get(cls: type[Self]) -> Self | None:
                """Get the singleton."""
                if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
                    return cast(Self, the_container)
                return None

        @classmethod
        def _create_instance(cls: type[Self]) -> Self:
            """Instantiate the ContainerSection, store it in the singleton and return it. Likely that this is wrong."""

            # instantiate and store the ContainerSection with default values
            return cls()._set()

        def _set(self: Self) -> Self:
            """Store the singleton."""
            _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
            subsections = [
                attr for attr in vars(self) if isinstance(attr, ContainerSectionBase)
            ]
            for subsec in subsections:
                subsec._set()  # pylint: disable=protected-access
            return self

        def _update(self: Self, changes: dict[str, dict[str, Any]]) -> Self:
            "Update parameters and sections with data specified in changes; not meant for config"
            return replace(self, **changes)


_ALL_CONTAINER_SECTION_SINGLETONS: dict[int, Any] = {}
