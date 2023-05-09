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

        def _update(self, changes: dict[str, dict[str, Any]]) -> Self:
            "Update parameters and sections with data specified in changes; not meant for config"
            return replace(self, **changes)

        def _set(self) -> Self:
            """Store the singleton."""
            _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
            subsections = [attr for attr in vars(self) if isinstance(attr, ContainerSectionBase)]
            for subsec in subsections:
                subsec._set()  # pylint: disable=protected-access
            return self

        @classmethod
        def _get(cls) -> Self | None:
            """Get the singleton."""
            if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
                return cast(Self, the_container)
            return None

    else:

        def _update(self: Self, changes: dict[str, dict[str, Any]]) -> Self:
            return replace(self, **changes)

        def _set(self: Self) -> Self:
            """Store the singleton."""
            _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
            return self

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


_ALL_CONTAINER_SECTION_SINGLETONS: dict[int, Any] = {}
