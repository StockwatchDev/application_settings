# application_settings

[![pypi](https://img.shields.io/pypi/v/application-settings.svg)](https://pypi.python.org/pypi/application-settings)
[![versions](https://img.shields.io/pypi/pyversions/application-settings.svg)](https://github.com/StockwatchDev/application_settings)
[![Build Status](https://github.com/StockwatchDev/application_settings/actions/workflows/application_settings-tests.yml/badge.svg?branch=develop)](https://github.com/StockwatchDev/application_settings/actions)
[![codecov](https://codecov.io/gh/StockwatchDev/application_settings/branch/develop/graph/badge.svg)](https://app.codecov.io/gh/StockwatchDev/application_settings)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

"You write the dataclasses to define parameters for configuration and settings, 
application\_settings takes care of the logic."

## What and why

Application\_settings is a package for providing a python application with parameters for
configuration and settings. It uses [toml](https://toml.io/en/) or 
[json](https://docs.python.org/3/library/json.html) files that are parsed
into dataclasses. This brings some benefits:

- Parameters are typed, which allows for improved static code analyses.
- IDEs will provide helpful hints and completion when using the parameters.
- More control over what happens when a file contains mistakes
  (by leveraging the power of [pydantic](https://docs.pydantic.dev/)).
- Possibility to specify defaults when no file is found or entries are missing.
- Configuration parameters are read-only (i.e., changed by editing the config file); we
  recommend (and support) the use of `toml` for this, which is a human-orineted,
  flexible, standardardized and not overly complex format.
- Settings parameters are read-write (i.e., mostly changed via the UI of the
  application); we recommend (and support) use `json` for this, an established
  standardized machine-oriented format.

Parsing is done once during first access and the resulting set of parameters is stored
as a singleton.

Interested? Then have a look at our
[quick start](https://github.com/StockwatchDev/application_settings).

[//]: # (Change link to published quick start)

## License

This project is licensed under the terms of the MIT license.
