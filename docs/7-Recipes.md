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
`application_settings` provides a convenience function for this purpose.

```python
from application_settings import use_standard_logging
from loguru import logger

use_standard_logging()
logger.enable("application_settings")

```

The logical location for this statement is before the first invocation of `load` (or, if
you do not `load` explicitly, before the first invocation of `get`).

## Having a test configuration during testing

During unit testing, you typically would like to have a specific test configuration and
it would be a hassle to provide a file for this purpose. Fortunately, there is another
way. As an example, let's create a test config for `ExampleConfigSection` (see 
[Quick Start](Quick_start.md)):

```python
# Create a (nested) dictionary that holds the test values for the relevant fields
test_config = {
    "field1": 3.3,
    "field2": -2
}

# Invoke class method set on the Config(Section) with this dict as parameter;
# this will set the config singleton with the provided values
ExampleConfigSection.set(test_config)
```

The `test_config` dictionary only has to contain values for fields that have no default
and for fields for which the test value differs from the default one.

## Initialization needs to depend on configuration

The situation may occur that your application imports a module that holds code that is
initialized during import and you want this initialization to be configurable. For
example, you might want a configurable initial value for a module global variable.

To make this work, you need to assure that the configuration is loaded before the
module of concern is imported. To make this robust, the following way of work is
suggested:

- Define your configuration class(es) in a (number of) separate module(s);
- Make a small module `_config_loader.py` that imports your configuration container,
  possibly sets logging and loads the configuration;
- In the file that is the entry point of your application (i.e., typically
  `__main__.py`), make sure that `_config_loader` is the first module that you `import`.

Obviously, the same approach can be followed for settings.
