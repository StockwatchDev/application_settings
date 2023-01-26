# Application_config

[![Build Status](https://github.com/StockwatchDev/application_config/actions/workflows/application_config-tests.yml/badge.svg?branch=develop)](https://github.com/StockwatchDev/application_config/actions)
[![codecov](https://codecov.io/gh/StockwatchDev/application_config/branch/develop/graph/badge.svg)](https://app.codecov.io/gh/StockwatchDev/application_config)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## What and why

Application_config is a module for configuring a python application. It uses 
[toml](https://toml.io/en/) configuration files that are parsed into dataclasses.
This brings some benefits:

- Configuration parameters are typed, which allows for improved static code analyses.
- IDEs will provide helpful hints and completion when using configuration parameters.
- More control over what happens when a config file contains mistakes
  (by leveraging the power of [pydantic](https://docs.pydantic.dev/)).
- Possibility to specify defaults when no config file is found or entries are missing.
- Configuration described in a human-usable, flexible, standardardized and not overly 
  complex format.

Parsing is done once during first access and the resulting configuration is stored
as a singleton.

## How

### Define config section(s) and the config container

Example:

```python
from application_config import (
    ConfigBase,
    ConfigSectionBase,
)
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Example1ConfigSection(ConfigSectionBase):
    """Config section for an example"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class ExampleConfig(ConfigBase):
    """Config for an example"""

    section1: Example1ConfigSection = Example1ConfigSection()

```

Note: a `pydantic.dataclasses.dataclass` is a drop-in replacement for the standard 
`dataclasses.dataclass`, with validation, see 
[pydantic dataclasses](https://docs.pydantic.dev/usage/dataclasses/).

### Write a config file

For the example, the config file `~/.example/config.toml` could be something like this:

```toml
[section1]
field1 = "my own version of field1"
field2 = 22
```

The order of sections and/or fields in the toml file does not have to adhere to the order
in which attributes have been specified in the Config(Section) classes.

### Use config parameters in your code

```python
# the first invocation of get() will create the singleton instance of ExampleConfig
the_config = ExampleConfig.get()
a_variable: str = the_config.section1.field1  # a_variable == "my own version of field1"
another_variable: int = the_config.section1.field2  # another_variable == 22

# you can reload a config and / or set a non-default path
another_config = ExampleConfig.get(reload=True, configfile_path="./my_config.tml")

```

## Location of the config file on your file system

To do

## Handling deviations in the config file

### When your config file does not adhere to the specified types

When loading the config file, the values specified are coerced into the appropriate type
where possible. If type coercion is not possible, then a `pydantic.ValidationError`
is raised. Consider the case where you would use the following config file for 
the `ExampleConfig` defined above:

```toml
[section1]
field1 = true
field2 = "22"
```

The `bool` specified for `field1` will be coerced into a `str` value of `"true"`.
The `str` specified for `field2` will be coerced into an `int` value of `22`.

### When your config file does not contain all specified attributes

If your Config has one of more sections with attributes that do not have a default
value, then a config file must be loaded and these sections and attributes must be 
present in the loaded config file. If this is not the case, a `TypeError` is raised.
Attributes that have default values can be omitted
from the config file without problems.

Note that in the dataclass definitions, attributes without default value have to come
before attributes with default values.

### When your config file contains additional, unspecified attributes

Entries in a config file that are not defined in the Config(Section) classes will simply
be ignored silently.

## More advanced typing and validation with pydantic

- Non-standard types useful for configuration, such as network adresses, are offered, see 
  [pydantic types](https://docs.pydantic.dev/usage/types/#pydantic-types)
- The value of numerous common types can be restricted using 
  [pydantic constrained types](https://docs.pydantic.dev/usage/types/#constrained-types)
