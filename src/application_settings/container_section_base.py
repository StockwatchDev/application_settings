"""Base classes for containers and sections for configuration and settings."""
import sys
from dataclasses import fields, replace
from typing import Any, TypeVar

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
            # filter out fields that are in changes and an attribute of the Container
            fields_to_update = {
                fld for fld in fields(self) if fld.init and fld.name in changes.keys()
            }
            # # filter out fields that are a section
            # sections_to_update = {
            #     fld for fld in fields_to_update if isinstance(fld, ContainerSectionBase)
            # }

            # # update these sections and keep them in a dict
            # # actually sections: dict[str, _ContainerSectionT]
            # # but MyPy doesn't swallow that
            # updated_sections: dict[str, Self] = {
            #     fld.name: replace(getattr(self, fld.name), **changes[fld.name])
            #     for fld in sections_to_update
            # }

            # # filter out fields that are not a section
            # parameters_to_update: dict[str, Any] = {
            #     fld.name: fld
            #     for fld in fields_to_update
            #     if not isinstance(fld, ContainerSectionBase)
            # }
            # update_values = parameters_to_update | updated_sections

            # new_settings = replace(self, **update_values)
            new_settings = replace(self, **changes)
            return new_settings

    else:

        def _update(self: Self, changes: dict[str, dict[str, Any]]) -> Self:
            "Update parameters and sections with data specified in changes; not meant for config"
            # filter out fields that are in changes and an attribute of the Container
            fields_to_update = {
                fld for fld in fields(self) if fld.init and fld.name in changes.keys()
            }
            # filter out fields that are a section
            sections_to_update = {
                fld for fld in fields_to_update if isinstance(fld, ContainerSectionBase)
            }

            # update these sections and keep them in a dict
            # actually sections: dict[str, _ContainerSectionT]
            # but MyPy doesn't swallow that
            updated_sections: dict[str, Self] = {
                fld.name: replace(getattr(self, fld.name), **changes[fld.name])
                for fld in sections_to_update
            }

            # filter out fields that are not a section
            parameters_to_update: dict[str, Any] = {
                fld.name: fld
                for fld in fields_to_update
                if not isinstance(fld, ContainerSectionBase)
            }
            update_values = parameters_to_update | updated_sections

            new_settings = replace(self, **update_values)
            return new_settings
