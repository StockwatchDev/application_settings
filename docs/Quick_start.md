# Quick start

### Install the package

`pip install -U application_settings`

### Define dataclasses for configuration / settings parameters

`Config` is for read-only parameters read from file, `Settings` are read-write parameters
stored to file for persistancy over sessions. During definition, they differ only in
terms of the base classes that are used. Example:

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

        field1: float = 0.5
        field2: int = 2


    @dataclass(frozen=True)
    class MyExampleConfig(ConfigBase):
        """Config for an example"""

        name: str = "nice example"
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

        totals: int = 2


    @dataclass(frozen=True)
    class MyExampleSettings(SettingsBase):
        """Settings for an example"""

        name: str = "nice name"
        basics: BasicSettingsSection = BasicSettingsSection()

    ```




### Write (or generate) the file

By default, the following files are expected for the dataclasses defined above:

=== "`~/.my_example/config.toml`"
    ```toml
    # The nice thing about toml is that you can add comments for explanation
    # A config is read-only, so they will not be overwritten by your application
    # (unlike for settings)

    name = "the real thing"

    [section1]
    field1 = -0.5
    field2 = 22
    ```

=== "`~/.my_example/settings.json`"
    ```json
    {
        "name": "the stored name",
        "basics": {
            "totals": 3
        }
    }
    ```

### Use parameters in your code

=== "Configuration"
    ```python
    # the first invocation of get() will create the singleton instance of MyExampleConfig
    a_variable = MyExampleConfig.get().section1.field1  # a_variable == -0.5
    another_variable = MyExampleConfig.get().section1.field2  # another_variable == 22

    # The only way to modify a config parameter is by editing the config file
    # or by changing the default value in the definition
    # Suppose that we edited the config file, changed name to "new name" and removed field2

    # you can reload a config
    new_variable = MyExampleConfig.get().name  # new_variable == "new name"
    another_new_variable = MyExampleConfig.get().section1.field2  # another_new_variable == 2
    ```

=== "Settings"
    ```python
    # the first invocation of get() will create the singleton instance of MyExampleSettings
    a_variable: str = MyExampleSettings.get().name  # a_variable == "the stored name"
    another_variable: int = MyExampleConfig.get().basics.totals  # another_variable == 3

    # You can update the settings:
    MyExampleSettings.update({"basics": {"totals": 33}})
    # The updated values will be written to the settings file automatically and the
    # singleton is replaced by a new instance of MyExampleSettings with the updated values

    # you can also edit the settings file and reload:
    refreshed_name = MyExampleSettings.get().name

    ```

These are the basics; a more detailed description is found in the next section (Usage)
or you can take a look at the API (Reference).