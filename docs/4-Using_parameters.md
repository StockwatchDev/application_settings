## Use parameters in your code

Parameter containers are meant to be instantiated just once and be available globally for
the application. Therefore, implementation has been done as follows:

- The instance of a parameter container is accessed via a class method `get()`;
- The parameter value is then obtained by chaining with the section name and the
  parameter name;
- The first invocation of `get()` will create the container instance, try to read values
  from file and store it for future access in a private module global (a dictionary with
  the class id as key);
- A parameter container should not be instantiated directly by client code (although it
  is possible to do so, e.g. for testing purposes);
- If needed, you can set the path for the parameter file before the first invocation of
  `get()`.

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
of dictionaries that specifies the sections (keys of the outer dict) and fields (keys of
the inner dicts) that are changed. The method `update` will replace the stored settings
in the private module global with an updated instance and the settings file will be
updated as well. So the invocation of `get()` after `update` or application restart or
reloading will return the changed parameter values.

## Example

=== "Configuration"
    ```python
    import MyExampleConfig

    # if the config file is not in the default location, then set the path first
    MyExampleConfig.set_filepath(r"C:\ProgramData\MyApp\config.toml")

    # the next statement will create the config
    field1_var: str = MyExampleConfig.get().section1.field1  # field1_var == "my own version of the first field"
    # the next statement just gets that same instance
    field2_var: int = MyExampleConfig.get().section1.field2  # field2_var == 22

    # if you have edited the config file, you can reload it (which will create a new instance)
    field1_var = MyExampleConfig.get(reload=True).section1.field1

    # you cannot programmatically change config parameters

    ```

=== "Settings"
    ```python
    import MyExampleSettings

    # if the settings file is not in the default location, then set the path first
    MyExampleSettings.set_filepath(r"C:\ProgramData\MyApp\settings.json")

    # the next statement will create the settings
    name_var: str = MyExampleSettings.get().basics.name  # name_var == "the name"
    # the next statement just gets that same instance
    totals_var: int = MyExampleSettings.get().basics.totals  # totals_var == 2

    # if you have edited the settings file, you can reload it (which will create a new instance)
    name_var = MyExampleSettings.get(reload=True).basics.name

    # change settings parameters programmatically using update
    MyExampleSettings.update({"basics": {"name": "new and shiny name", "totals": 222}})
    print(MyExampleSettings.get().basics.totals)  # 222
    print(MyExampleSettings.get(reload=True).basics.name)  # new and shiny name

    ```
