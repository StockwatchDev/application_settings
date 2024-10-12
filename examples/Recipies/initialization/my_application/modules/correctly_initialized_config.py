"""Configuration for configvar_is_set with proper loading of the config file via the cli in the Config module"""

from application_settings import ConfigBase, config_filepath_from_cli, dataclass


@dataclass(frozen=True)
class CorrectlyInitializedConfig(ConfigBase):
    """Example of a Config that does not load the config in the module"""

    configvar_is_set: bool = False


print("Now setting filepath for CorrectlyInitializedConfig")
config_filepath_from_cli(CorrectlyInitializedConfig)
