### Use parameters in your code

```python
# the first invocation of get() will create the singleton instance of MyExampleConfig
a_variable: str = MyExampleConfig.get().section1.field1  # a_variable == "my own version of field1"
another_variable: int = MyExampleConfig.get().section1.field2  # another_variable == 22

# you can reload a config and / or set a non-default path
another_config = MyExampleConfig.get(reload=True, configfile_path="./my_config.tml")

```
