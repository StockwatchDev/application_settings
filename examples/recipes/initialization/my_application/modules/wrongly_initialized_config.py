"""Configuration for configvar_is_set WITHOUT proper loading of the config file via the cli

Have a look at file 'correctly_initialized_config.py' to see an example with proper loading
"""

from application_settings import ConfigBase, dataclass


@dataclass(frozen=True)
class WronglyInitializedConfig(ConfigBase):
    """Example of a Config that does not load the config in the module"""

    configvar_is_set: bool = False
