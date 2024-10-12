"""Configuration parameter definition"""

from application_settings import (
    ConfigBase,
    ConfigSectionBase,
    attributes_doc,
    config_filepath_from_cli,
    dataclass,
)


@attributes_doc
@dataclass(frozen=True)
class MyExampleConfigSection(ConfigSectionBase):
    """Config section for an example"""

    field1: float = 0.5
    """The first field; defaults to 0.5"""

    field2: int = 2
    """The second field; defaults to 2"""


@attributes_doc
@dataclass(frozen=True)
class MyExampleConfig(ConfigBase):
    """Config for an example"""

    name: str = "nice example"
    """Name of the application; defaults to 'nice example'"""

    section1: MyExampleConfigSection = MyExampleConfigSection()
    """Holds the configuration parameters for the first section"""


# It is good practice to set the filepath via the command line interface
# You can optionally set load=True
config_filepath_from_cli()
