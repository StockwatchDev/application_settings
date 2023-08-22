"""Configuration for initial_value WITHOUT proper loading of the config file via the cli"""

from application_settings import ConfigBase, dataclass


@dataclass(frozen=True)
class WronglyInitializedConfig(ConfigBase):
    """Example of a Config that does not load the config in the module"""

    initial_value: float = 0.0
