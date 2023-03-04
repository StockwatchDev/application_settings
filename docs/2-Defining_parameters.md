The expected way of work is that parameters are defined in section classes and sections
are gathered in a container.

## Defining section(s)

A section is defined by subclassing the relevant base class (ConfigSectionBase for
config, SettingsSectionBase for settings) and decorating it with
`@dataclass(frozen=True)`. Parameters are defined as fields of the dataclass. For a 
dataclass, it is mandatory to add a type hint for each field. These type hints are used
also to validate the data that is read from the parameter file (because we are
using [pydantic dataclasses](https://docs.pydantic.dev/usage/dataclasses/)). If you
specify a default value as well, then you prevent the occurance of an exception if the
value for the parameter of concern is not found in the parameter file.

## Defining the container

Likewise, the container is defined by subclassing the relevant base class (ConfigBase for
config, SettingsBase for settings) and decorating it with `@dataclass(frozen=True)`.
Sections are now defined as fields of this dataclass, type hinted with the appropriate
section class and instantiated (possible only when all parameters of the section have
default values).

Note that albeit settings can be changed programmatically, we still set `frozen=True` for
the settings container and -sections (see also the section below).

## Example

=== "Configuration"
    ```python
    from application_settings import (
        ConfigBase,
        ConfigSectionBase,
    )
    from pydantic.dataclasses import dataclass


    @dataclass(frozen=True)
    class MyExampleConfigSection(ConfigSectionBase):
        """Config section for an example"""

        field1: str = "field1"
        field2: int = 2


    @dataclass(frozen=True)
    class MyExampleConfig(ConfigBase):
        """Config for an example"""

        section1: MyExampleConfigSection = MyExampleConfigSection()

    ```

=== "Settings"
    ```python
    from application_settings import (
        SettingsBase,
        SettingsSectionBase,
    )
    from pydantic.dataclasses import dataclass


    @dataclass(frozen=True)
    class BasicSettingsSection(SettingsSectionBase):
        """Settings section for the basics"""

        name: str = "the name"
        totals: int = 2


    @dataclass(frozen=True)
    class MyExampleSettings(SettingsBase):
        """Settings for an example"""

        basics: BasicSettingsSection = BasicSettingsSection()

    ```
