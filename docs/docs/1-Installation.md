# Install the package

`application_settings` is available for [pypi](https://pypi.org/project/application-settings/)
and can hence be installed with [pip](https://pypi.org/project/pip) or
[poetry](https://python-poetry.org). The package is not available on
[conda](https://docs.conda.io/en/latest/).

If you don't want to wait for a release and prefer to try the develop version, then you
can install from our repo.

=== "Windows"
    ```python
    # From pypi with pip:
    py -m pip install -U application_settings

    # From pypi with poetry:
    poetry add application_settings

    # From the repo with pip:
    py -m pip install git+https://github.com/StockwatchDev/application_settings#develop

    # From the repo with poetry:
    poetry add git+https://github.com/StockwatchDev/application_settings#develop
    ```

=== "Linux"
    ```python
    # From pypi:
    python -m pip install -U application_settings

    # From pypi with poetry:
    poetry add application_settings

    # From the repo with pip:
    python -m pip install git+https://github.com/StockwatchDev/application_settings#develop

    # From the repo with poetry:
    poetry add git+https://github.com/StockwatchDev/application_settings#develop
    ```

We have direct dependencies on the following packages:

- [attributes-doc](https://pypi.org/project/attributes-doc/)
- [loguru](https://pypi.org/project/loguru/)
- [pathvalidate](https://pypi.org/project/pathvalidate/)
- [pydantic](https://pypi.org/project/pydantic/)
- [tomlkit](https://pypi.org/project/tomlkit/)
- [typing-extensions](https://pypi.org/project/typing-extensions/) (for python versions below 3.12)
