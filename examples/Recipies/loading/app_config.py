"""Configuration for configvar_is_set with proper loading of the config file via the cli in the Config module"""

from lib_config import MyLibConfigSection

from application_settings import ConfigBase, dataclass


@dataclass(frozen=True)
class MyAppConfig(ConfigBase):
    """Example of a Config for an application"""

    lib_config: MyLibConfigSection = MyLibConfigSection()
