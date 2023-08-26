# Quick start

### Install the package

`pip install -U application_settings`

### Define dataclasses for configuration / settings parameters

`Config` is for read-only parameters read from file, `Settings` are read-write parameters
stored to file for persistancy over sessions. During definition, they differ only in
terms of the base classes that are used. Example:

=== "Configuration"
    ```python
    from application_settings import ConfigBase, ConfigSectionBase, dataclass


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
    from application_settings import SettingsBase, SettingsSectionBase, dataclass


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
    # Use this file to set the config that you prefer by editing the file
    name = "the real thing"
    [section1]
    # field1 has default value 0.5
    field1 = -0.5
    # field2 has default value 2
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
    # One of the first things to do in an application is loading the parameters
    MyExampleConfig.load()
    # Now you can access parameters via get()
    # If you get() MyExampleConfig before load(), it will be loaded automatically
    a_variable = MyExampleConfig.get().section1.field1
    print(f"a_variable == {a_variable}")  # a_variable == -0.5
    # You can also directly get() a section; but remember that the config should
    # be loaded already then (get() on a section does not automatically load())
    another_variable = MyExampleConfigSection.get().field2
    print(f"another_variable == {another_variable}")  # another_variable == 22

    # The only way to modify a config parameter is by editing the config file
    # or by changing the default value in the definition
    # Suppose that we edited the config file, changed the value for name to "new name"
    # and removed field2

    # You can reload a config
    MyExampleConfig.load()
    new_variable = MyExampleConfig.get().name
    print(f"new_variable == {new_variable}")  # new_variable == "new name"
    another_new_variable = MyExampleConfigSection.get().field2
    print(
        f"another_new_variable == {another_new_variable}"
    )  # another_new_variable == 2

    ```

=== "Settings"
    ```python
    # One of the first things to do in an application is loading the parameters
    MyExampleSettings.load()
    # Now you can access parameters via get()
    # If you get() MyExampleSettings before load(), it will be loaded automatically
    a_variable = MyExampleSettings.get().name
    print(f"a_variable == '{a_variable}'")  # a_variable == 'the stored name'
    # You can also directly get() a section; but remember that the settings should
    # be loaded already then (get() on a section does not automatically load())
    another_variable = BasicSettingsSection.get().totals
    print(f"another_variable == {another_variable}")  # another_variable == 3

    # You can update the settings:
    MyExampleSettings.update({"basics": {"totals": 33}})
    # The updated values will be written to the settings file automatically and the
    # singleton is replaced by a new instance of MyExampleSettings with the updated values
    refreshed_totals = BasicSettingsSection.get().totals
    print(f"refreshed_totals == {refreshed_totals}")  # refreshed_totals == 33

    # You can also edit the settings file. Suppose that we changed the value for name to
    # "updated name"

    # You can reload a setting
    MyExampleSettings.load()
    refreshed_name = MyExampleSettings.get().name
    print(f"refreshed_name == '{refreshed_name}'")  # refreshed_name == 'updated name'
    ```

These are the basics; a more detailed description is found in the next section (Usage)
or you can take a look at the API (Reference).