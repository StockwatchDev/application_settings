"""Settings definitions"""

from application_settings import (
    SettingsBase,
    SettingsSectionBase,
    attributes_doc,
    dataclass,
    settings_filepath_from_cli,
)


@attributes_doc
@dataclass(frozen=True)
class BasicSettingsSection(SettingsSectionBase):
    """Settings section for the basics"""

    totals: int = 2
    """The totals value; defaults to 2"""


@attributes_doc
@dataclass(frozen=True)
class MyExampleSettings(SettingsBase):
    """Settings for an example"""

    name: str = "nice name"
    """This parameter holds the name setting; defaults to 'nice name'"""

    basics: BasicSettingsSection = BasicSettingsSection()
    """Holds the setting parameters for the basic section"""


# It is good practice to set the filepath via the command line interface
settings_filepath_from_cli()
