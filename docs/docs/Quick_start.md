# Quick start

## Install the package

`pip install -U application_settings`

## Define dataclasses for configuration / settings parameters

`Config` is for read-only parameters read from file, `Settings` are read-write parameters
stored to file for persistancy over sessions. During definition, they differ only in
terms of the base classes that are used. Example:

=== "Configuration"
    ```python
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

    ```

=== "Settings"
    ```python
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

    ```

## Write (or generate) the file

By default, the following files are expected for the dataclasses defined above:

=== "`~/.my_example/config.toml`"
    ```toml
    # Config for an example

    # Use this file to set the config that you prefer by editing the file

    # The next element is refering to the Config container class that
    # defines the config parameters of the application.
    # It is used when loading from command line
    Config_container_class = "config.MyExampleConfig"


    # With this parameter you can configure the name; defaults to 'nice example'
    name = "the real thing"

    # Holds the configuration parameters for the first section
    [section1]

    # The first field; defaults to 0.5
    field1 = -0.5

    # The second field; defaults to 2
    field2 = 22

    ```

=== "`~/.my_example/settings.json`"
    ```json
    {
        "Settings_container_class": "settings.MyExampleSettings",
        "name": "the stored name",
        "basics": {
                "totals": 3
        }
    }

    ```

## Use parameters in your code

=== "Configuration"
    ```python
    """example how to use the module application_settings"""
    # You can access parameters via get()
    # If you get() MyExampleConfig before load(), it will be loaded automatically
    # using the filepath that has been set via the command line
    a_variable = MyExampleConfig.get().section1.field1
    print(f"{a_variable =}")  # a_variable = -0.5
    # You can also directly get() a section; but remember that the config should
    # be loaded already then (get() on a section does not automatically load())
    another_variable = MyExampleConfigSection.get().field2
    print(f"{another_variable =}")  # another_variable = 22

    # The only way to modify a config parameter is by editing the config file
    # or by changing the default value in the definition
    # Suppose that we edited the config file, changed the value for name to "new name"
    # and removed field2

    # You can reload a config
    MyExampleConfig.load()
    new_variable = MyExampleConfig.get().name
    print(f"new_variable = '{new_variable}'")  # new_variable == 'new name'
    another_new_variable = MyExampleConfigSection.get().field2
    print(f"{another_new_variable =}")  # another_new_variable = 2

    ```

=== "Settings"
    ```python
    """example how to use the module application_settings"""
    # You can access parameters via get()
    # If you get() MyExampleSettings before load(), it will be loaded automatically
    a_variable = MyExampleSettings.get().name
    print(f"a_variable = '{a_variable}'")  # a_variable = 'the stored name'
    # You can also directly get() a section; but remember that the settings should
    # be loaded already then (get() on a section does not automatically load())
    another_variable = BasicSettingsSection.get().totals
    print(f"{another_variable = }")  # another_variable = 3

    # You can update the settings:
    MyExampleSettings.update({"basics": {"totals": 33}})
    # The updated values will be written to the settings file automatically and the
    # singleton is replaced by a new instance of MyExampleSettings with the updated values
    refreshed_totals = BasicSettingsSection.get().totals
    print(f"{refreshed_totals = }")  # refreshed_totals = 33

    # You can also edit the settings file. Suppose that we changed the value for name to
    # "updated name"

    # You can reload a setting
    MyExampleSettings.load()
    refreshed_name = MyExampleSettings.get().name
    print(f"refreshed_name == '{refreshed_name}'")  # refreshed_name == 'updated name'
    ```

These are the basics; a more detailed description is found in the next section (Usage)
or you can take a look at the API (Reference).
