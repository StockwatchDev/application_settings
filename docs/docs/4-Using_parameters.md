# Using parameters

## Use parameters in your code

Parameter sections and containers are meant to be instantiated just once and be available
globally for the application. Therefore, implementation has been done as follows:

- By in voking method `load()` on a parameter container class, the container and all
  contained (nested) sections are instantiated with data values read
  from the parameter file. The instances are stored for future access in a private module
  global (a dictionary with the class id as key);
- The instance of a parameter container or section is accessed via a class method `get()`;
- The parameter value is then obtained by chaining with (the section name(s) and) the
  parameter name;
- If a container has not been loaded, the first invocation of `get()` will do that
  automatically. This is not the case for a section - if `get()` is invoked on a section
  before any loading has been done, it will be instantiated with default values;
- A parameter container should not be instantiated directly by client code (although it
  is possible to do so, e.g. for testing purposes);
- If needed, you can set the path for the parameter file before the first invocation of
  `get()` (see [chapter on files](./3-Files.md)).

## Changing parameter values

Parameters are defined as fields of frozen dataclasses. Hence, changing parameter values
by means of straightforward assignment will raise an error.

Config parameters are meant to be read only. Changing values of such parameters has to be
done by editing the config file and restarting your application or reloading the config
container.

Obviously, settings parameters can also be changed by editing the settings file and
restarting the application or reloading the settings container. In addition to that,
settings can be changed programmatically by calling a class method
`update(changes: dict[str, dict[str, Any])`, where the argument `changes` is a dictionary
in which each key is the name of a parameter that is to be updated. For updating a nested
section, the key needs to hold the section name and the value should hold a dictionary
with str-type keys again, etc.

The method `update` will replace the stored settings
in the private module global with an updated instance and the settings file will be
updated as well. So the invocation of `get()` after `update` or application restart or
reloading will return the changed parameter values.

## Example

=== "Configuration"
    ```python
    import MyExampleConfig

    # If the config file is not in the default location, then set the path first
    MyExampleConfig.set_filepath(r"C:\ProgramData\MyApp\config.toml")

    # The next statement will create the config
    field1_var: str = MyExampleConfig.get().section1.field1  # field1_var == -0.5
    # The next statement just gets that same instance
    field2_var: int = MyExampleConfig.get().section1.field2  # field2_var == 22

    # After edited the config file, you can reload it (which will create a new instance)
    MyExampleConfig.load()
    field1_var = MyExampleConfig.get().section1.field1

    # you cannot programmatically change config parameters

    ```

=== "Settings"
    ```python
    import MyExampleSettings

    # If the settings file is not in the default location, then set the path first
    MyExampleSettings.set_filepath(r"C:\ProgramData\MyApp\settings.json")

    # The next statement will create the settings
    name_var: str = MyExampleSettings.get().name  # name_var == "the stored name"
    # The next statement just gets that same instance
    totals_var: int = MyExampleSettings.get().basics.totals  # totals_var == 3

    # After edited the settings file, you can reload it (which will create a new instance)
    MyExampleSettings.load()
    name_var = MyExampleSettings.get().name

    # change settings parameters programmatically using update
    MyExampleSettings.update({"name": "updated name", "basics": {"totals": 33}})
    print(MyExampleSettings.get().name)  # updated name
    print(MyExampleSettings.get().basics.totals)  # 33
    # the update has been written to file as well
    MyExampleSettings.load()
    print(MyExampleSettings.get().name)  # updated name

    ```
