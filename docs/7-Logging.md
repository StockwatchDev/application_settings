## Logging with Loguru

`application_settings` makes use of the [Loguru](https://github.com/Delgan/loguru) library
for logging. By default, logging is disabled, hence you need to enable it to get
logging output.

```python
from loguru import logger

logger.enable("application_settings")

```

The logical location for this statement is before `load` (or, if you do not `load`
explicitly, before the first invocation of `get`).

Note that by default `Loguru` logs to `stderr`.

## Logging with standard `logging`

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

The logical location for these statement is before `load` (or, if you do not `load`
explicitly, before the first invocation of `get`).
