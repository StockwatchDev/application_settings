### Use parameters in your code

Parameter containers are meant to be instantiated just once and be available globally for
the application. Therefore, implementation has been done as follows:

- The instance of a parameter container is accessed via a class method `get()`;
- The parameter value is then obtained by chaining with the section name and the
  the parameter name;
- The first invocation of `get()` will create the container instance, try to read values
  from file and store it for future access in a private module global (a dictionary with
  the class id as key);
- A parameter container should not be instantiated directly by client code (although it
  is possible to do so, e.g. for testing purposes);
- If needed, you can set the path for the parameter file before the first invocation of
  `get()`.

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

    ```
