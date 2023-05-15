"""Base class for sections to be added to containers and container sections for configuration and settings."""
import sys
from dataclasses import replace
from typing import Any, TypeVar

from pydantic.dataclasses import dataclass

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = TypeVar("Self", bound="ContainerSectionBase")


@dataclass(frozen=True)
class ContainerSectionBase:
    """Base class for all ContainerSection classes"""

    def _update(self: Self, changes: dict[str, dict[str, Any]]) -> Self:
        "Update parameters and sections with data specified in changes; not meant for config"
        return replace(self, **changes)
