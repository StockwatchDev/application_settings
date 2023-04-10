# pylint: disable=consider-alternative-union-syntax
"""Base classes for containers and sections for configuration and settings."""
import sys
from dataclasses import fields, replace
from typing import Any, TypeVar

from pydantic.dataclasses import dataclass

from .type_notation_helper import PathOpt, PathOrStr, dictOrAny

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = TypeVar("Self", bound="ContainerSectionBase")


@dataclass(frozen=True)
class ContainerSectionBase:
    """Base class for all ContainerSection classes"""

    if sys.version_info >= (3, 11):

        @classmethod
        def _instantiate_dataclass(cls, arg_dict: dict[str, Any]) -> Self:
            """Return an instance of cls, properly initialized"""
            # filter out fields that are both stored and an attribute of the ContainerSection
            data_fields = {
                fld for fld in fields(cls) if fld.init and fld.name in arg_dict.keys()
            }
            # instantiate the fields of the dataclass and keep them in a dict
            stored_fields: dict[str, Any] = {
                fld.name: _instantiate_field(fld.type, arg_dict[fld.name])
                for fld in data_fields
            }

            # instantiate the ContainerSection
            return cls(**stored_fields)

        def _update(self, changes: dict[str, dict[str, Any]]) -> Self:
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

    else:
        from typing import Union

        def _instantiate_dataclass(
            class_to_instantiate: Union[type[_ContainerT], type[_ContainerSectionT]],
            arg_dict: dict[str, Any],
        ) -> Union[_ContainerT, _ContainerSectionT]:
            """Return an instance of class_to_instantiate, properly initialized"""
            # filter out fields that are both stored and an attribute of the ContainerSection
            _data_fields = {
                fld
                for fld in fields(class_to_instantiate)
                if fld.init and fld.name in arg_dict.keys()
            }
            # instantiate the fields of the dataclass and keep them in a dict
            stored_fields: dict[str, Any] = {
                fld.name: _instantiate_field(fld.type, arg_dict[fld.name])
                for fld in _data_fields
            }

            # instantiate the ContainerSection
            return class_to_instantiate(**stored_fields)


def _instantiate_field(
    class_to_instantiate: Any,
    arg_dict_or_val: dictOrAny,
) -> object:
    """Return an instance of class_to_instantiate, properly initialized with arg_dict"""
    if issubclass(class_to_instantiate, ContainerSectionBase):
        assert isinstance(arg_dict_or_val, dict)
        new_section = class_to_instantiate._instantiate_dataclass(  # pylint: disable=protected-access
            **arg_dict_or_val
        )
        return new_section
    # expectation: isinstance(arg_dict_or_val, class_to_instantiate)
    # but type coercion can take place
    return arg_dict_or_val
