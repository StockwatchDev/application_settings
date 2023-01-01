# Application_config

[![Build Status](https://github.com/StockwatchDev/application_config/actions/workflows/application_config-tests.yml/badge.svg?branch=develop)](https://github.com/StockwatchDev/application_config/actions)
[![codecov](https://codecov.io/gh/StockwatchDev/application_config/branch/develop/graph/badge.svg)](https://app.codecov.io/gh/StockwatchDev/application_config)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## What and why

Application_config is a module for configuring a python application. It uses toml 
configuration files that are parsed into data classes.
This brings some benefits:

- Configuration parameters are typed
- IDEs will provide helpful hints and completion when using configuration parameters
- More control over what happens when a config file contains erroneous or malicious text

## How

### Define config section(s) and the container with application info

Example:

```
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
        """Return the string that describes the application base name"""
        return "example"

```