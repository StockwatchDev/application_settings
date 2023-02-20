# Quick start

### Install the package

`pip install -U application_settings`

=== "Tab 1"
    Markdown **content**.

    Multiple paragraphs.

=== "Tab 2"
    More Markdown **content**.

    - list item a
    - list item b

### Define dataclasses for configuration / settings parameters

`Config` is for read-only parameters read from file, `Settings` are read-write parameters
stored to file for persistancy over sessions. Example:

```python
from application_settings import (
    ConfigBase,
    ConfigSectionBase,
)
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class MyExample1ConfigSection(ConfigSectionBase):
    """Config section for an example"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class MyExampleConfig(ConfigBase):
    """Config for an example"""

    section1: MyExample1ConfigSection = MyExample1ConfigSection()

```

### Write a config file

For the example, the config file `~/.my_example/config.toml` could be something like this:

```toml
[section1]
field1 = "my own version of field1"
field2 = 22
```

### Use parameters in your code

```python
# the first invocation of get() will create the singleton instance of MyExampleConfig
a_variable: str = MyExampleConfig.get().section1.field1  # a_variable == "my own version of field1"
another_variable: int = MyExampleConfig.get().section1.field2  # another_variable == 22

# you can reload a config and / or set a non-default path
another_config = MyExampleConfig.get(reload=True, configfile_path="./my_config.tml")

```
