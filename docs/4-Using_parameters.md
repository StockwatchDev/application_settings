### Use parameters in your code

Let's see if this works!

```python
# the first invocation of get() will create the singleton instance of MyExampleConfig
a_variable: str = MyExampleConfig.get().section1.field1  # a_variable == "my own version of the first field"
another_variable: int = MyExampleConfig.get().section1.field2  # another_variable == 22

# you can reload a config
another_config = MyExampleConfig.get(reload=True)

```
=== "Configuration"
    ```python
    # import MyExampleConfig

    # the first invocation of get() will create the singleton instance of MyExampleConfig
    a_variable: str = MyExampleConfig.get().section1.field1  # a_variable == "my own version of the first field"
    another_variable: int = MyExampleConfig.get().section1.field2  # another_variable == 22

    # if you have edited the config file, you can reload it
    a_new_variable = MyExampleConfig.get(reload=True).section1.field1

    ```

=== "Settings"
    ```python
    # import MyExampleSettings

    # the first invocation of get() will create the singleton instance of MyExampleSettings
    a_variable: str = MyExampleSettings.get().section1.field1  # a_variable == "my own version of the first field"
    another_variable: int = MyExampleSettings.get().section1.field2  # another_variable == 22

    # if you have edited the config file, you can reload it
    a_new_variable = MyExampleSettings.get(reload=True).section1.field1

    ```
