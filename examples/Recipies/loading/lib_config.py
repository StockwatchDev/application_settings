"""Configuration for configvar_is_set with proper loading of the config file via the cli in the Config module"""

from application_settings import ConfigSectionBase, attributes_doc, dataclass


@attributes_doc
@dataclass(frozen=True)
class MyLibConfigSection(ConfigSectionBase):
    """Example of a ConfigSection from a library module"""

    configvar_with_default_zero: int = 0
    """Config parameter that has default value of 0"""
