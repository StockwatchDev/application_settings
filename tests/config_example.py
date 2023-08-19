# pylint: disable=missing-module-docstring
from application_settings import ConfigBase, config_filepath_from_cli, dataclass


@dataclass(frozen=True)
class ExampleInitConfig(ConfigBase):
    """Example Config"""

    field0: float = 1.0


# need to use non-standard options here because of multiple tests
config_filepath_from_cli(
    ExampleInitConfig, short_option="-a", long_option="--a_config_filepath"
)
ExampleInitConfig.load()
