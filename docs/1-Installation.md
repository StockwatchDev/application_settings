## Install the package

`Application_settings` is available on [pypi](https://pypi.org/project/application-settings/)
and can hence be installed with `pip`:

- On Linux: `python -m pip install -U application_settings`
- On Windows: `py -m pip install -U application_settings`

We have a dependency on the following packages:

- [pathvalidate](https://pypi.org/project/pathvalidate/)
- [pydantic](https://pypi.org/project/pydantic/)
- [tomli](https://pypi.org/project/tomli/) (for python versions below 3.11)
- [tomli-w](https://pypi.org/project/tomli-w/)

This package is not available on [conda](https://docs.conda.io/en/latest/).

If you don't want to wait for a release and prefer to try the develop version, then you
can install from our repo:

- On Linux: `python -m pip install git+git://github.com/StockwatchDev/application_settings@develop#egg=application_settings`
- On Windows: `py -m pip install git+git://github.com/StockwatchDev/application_settings@develop#egg=application_settings`
