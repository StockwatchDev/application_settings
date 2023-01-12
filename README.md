# Application_config

[![Build Status](https://github.com/StockwatchDev/application_config/actions/workflows/application_config-tests.yml/badge.svg?branch=develop)](https://github.com/StockwatchDev/application_config/actions)
[![codecov](https://codecov.io/gh/StockwatchDev/application_config/branch/develop/graph/badge.svg)](https://app.codecov.io/gh/StockwatchDev/application_config)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## What and why

Application_config is a module for configuring a python application. It uses toml 
configuration files that are parsed into dataclasses.
This brings some benefits:

- Configuration parameters are typed;
- IDEs will provide helpful hints and completion when using configuration parameters
- More control over what happens when a config file contains incorrect or malicious text
  (by leveraging the power of [pydantic](https://docs.pydantic.dev/))
- Possibility to specify defaults when no config file is found

Parsing is done once during first access and the resulting configuration is stored
as a singleton.

## How

### Define config section(s) and the container with application info

Example:

```python
from application_config import (
    ConfigBase,
    ConfigSectionBase,
)
from dataclasses import dataclass


@dataclass(frozen=True)
class ExampleConfigSection(ConfigSectionBase):
    """Config section for an example"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class ExampleConfig(ConfigBase):
    """Config for an example"""

    section1: ExampleConfigSection = ExampleConfigSection()

    @staticmethod
    def get_app_basename() -> str:
        """Return the application base name.

        This name, with a preceding dot, will also be the folder name in the home directory
        that will store the config. I.e., for the case here: ~/.example
        """
        return "example"

```

The method `get_app_basename()` is abstract in `ConfigBase` and hence has to be defined
for the container.

### Write a config file

For the example, the config file `~/.example/config.toml` could be something like this:

```toml
[section1]
field1 = "my own version of field1"
field2 = 22
```

### Use config parameters in your code

```python
# the first invocation of get() will create the singleton instance of ExampleConfig
the_config = ExampleConfig.get()
a_variable: str = the_config.section1.field1  # a_variable == "my own version of field1"
another_variable: int = the_config.section1.field2  # another_variable == 22
```

### When your config file does not adhere to the specified types

When loading the config file, the values specified are coerced into the appropriate type
where possible. If type coercion is not possible, then a `pydantic.ValidationError`
is raised. Consider the case where you would use the following config file for 
the `ExampleConfig` defined above:

```toml
[section1]
field1 = "my own version of field1"
field2 = "22"
```

The `bool` specified for `field1` will be coerced into a `str` value of `"True"`.
The `str` specified for `field2` will be coerced into an `int` value of `22`.

