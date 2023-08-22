# Code snippets and recipes

## Logging

### Using `Loguru`

`application_settings` makes use of the [Loguru](https://github.com/Delgan/loguru) library
for logging. By default, logging is disabled, hence you need to enable it to get
logging output.

```python
from loguru import logger

logger.enable("application_settings")

```

The logical location for this statement is before the first invocation of `load` (or, if
you do not `load` explicitly, before the first invocation of `get`).

Note that by default `Loguru` logs to `stderr`, not `stdout` (as the standard `logging`
library does). Have a look at the
[Loguru documentation](https://loguru.readthedocs.io/en/stable/index.html) if you want
to configure the logger in the way that you want to.

### Using standard `logging`

If you prefer to use the standard `logging` library, then you need to do two things.
By default, logging is disabled, hence you need to enable it to get logging output. In
addition to that, you need to propagate Loguru messages to standard logging.
`application_settings` provides a convenience function `use_standard_logging` for this
purpose. This function sets the propagation to the standard logger. The function has a
single argument `enable` that by default is set to `False`. If a parameter `True` is
provided, then the convenience function also enables logging.

```python
from application_settings import use_standard_logging

use_standard_logging(enable=True)

```

The logical location for this statement is before the first invocation of `load` (or, if
you do not `load` explicitly, before the first invocation of `get`).

## Having a test configuration during testing

During unit testing, you typically would like to have a specific test configuration and
it would be a hassle to provide a file for this purpose. this especially holds true
for the situation in which you have used `application_settings` to define a config
section for your library package, and hence have no config container in your package
that can do the file handling.

Fortunately, there is another way, namely by using classmethod `set`. As an example,
let's create a test config for `ExampleConfigSection`, (see
[Quick Start](Quick_start.md)):

```python
# Create a (nested) dictionary that holds the test values for the relevant fields
test_config = {
    "field1": 3.3,
    "field2": -2
}

# Invoke classmethod set on the Config(Section) with this dict as parameter;
# this will set the config singleton with the provided values
ExampleConfigSection.set(test_config)
```

The `test_config` dictionary only has to contain values for fields that have no default
and for fields for which the test value differs from the default one.

## Initialization needs to depend on configuration

### Application case

The situation may occur that your application imports a module that holds code that is
initialized during import and you want this initialization to be configurable. For
example, you might want a configurable initial value for a module global variable
or a class variable.

To make this work, you need to assure that the configuration is loaded before the
module of concern is imported. To make this robust, the following way of work is
suggested:

- Define your configuration class(es) in a separate module (or multiple separate
  modules);
- In the module that defines your configuration container, set `config_filepath_from_cli`
  and `load` the configuration (this ensures that the config is loaded during import of
  the configuration container, which will always be before usage of a config parameter);
- It might be that globals or class variables of a package that you import are configured
  via `<some>ConfigSection.get()`, i.e., without importing the config container. Hence,
  we must ensure that the config container for sure is imported before that moment.
  Therefore, we suggest to make the `import` of the config container the very first
  statement of your entry point file in such a situation;
- Start your application with the filepath to the config file as command line parameter.

Obviously, the same approach can be followed for settings.

To make this more clear, an example is provided in the folder
[`examples/Recipies/initialization`](https://github.com/StockwatchDev/application_settings/tree/examples/Recipies/initialization).
Two configurations are defined: one that is loaded as described in the second bullet
above, and one that is (wrongly) loaded with the entry point file `__main__` and not in
the Config module. When running the example, it will become apparent that loading in the
entry point file is too late.

As described [here](#having-a-test-configuration-during-testing), in a test setting it
is generally easier to use class method `set`. Unfortunately, there is no straightforward
way to invoke `set` with test values during `import`, which means that you will have to
fall back to creating a test config file and loading that in the way described in this
section. An example on how to do this can be found in the file
[`tests/test_initialization_import.py`](https://github.com/StockwatchDev/application_settings/blob/develop/tests/test__initialization_import.py)
(also part of the source distribution of this package).

### Library package case

It can be that you have defined a ConfigSection for your library package and that your
library also has module globals or class variables that need to be initialized with
fields defined in that ConfigSection.

The normal situation would be that your ConfigSection and the module with configurable
module globals are both imported in the `__init__.py` file of your package.
Unfortunately, this implies that there is no way to `set` or `load` values for your
ConfigSection before the configurable module globals are initialized.

The only way that we currently see to handle such a situation properly is the following:

- make a separate package for the ConfigSection (i.e., isolated from your libary package)
- `import` that config package first, `set` (or `load`) the config values and only then
  import your library package (which will also import the config package, but the
  singleton has been initialized now).
