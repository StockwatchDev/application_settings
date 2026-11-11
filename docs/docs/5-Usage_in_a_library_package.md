# Usage in a library package

You can use `application_settings` also to parametrize a library package:

- Define parameters in one or more Section classes (i.e., not in a Container) - best
  practice is to have a single main section with possibly nested sub-sections;
- Use parameters in the code of your library by invoking class method `get()` on your
  Section class(es) (see [chapter on using parameters](./4-Using_parameters.md));
- The application that uses your library has to take care of loading stored values into
  your parameters. This can be done in two ways:
  - If the application also uses `application_settings`, it's simple; the main Section
      of your library package just needs to be contained in the Container of the
      application;
  - If the application does not use `application_settings`, then the application
      should invoke class method `set(data: dict[str, Any])` on your main Section, where
      `data` holds key-value-pairs with the name of the parameter and the value.
      Subsections can be set by the name of the section as key and a nested dictionary
      for the subsection parameters. Note that `set()` should be invoked before any
      `get()` is done.

## Example

The library defines a Section and uses it where it needs a parameter:

```python
# lib_config.py, in the library package
from application_settings import ConfigSectionBase, attributes_doc, dataclass


@attributes_doc
@dataclass(frozen=True)
class MyLibConfigSection(ConfigSectionBase):
    """Config of my library"""

    timeout: int = 10
    """Timeout in seconds for a request"""


# anywhere in the library
timeout = MyLibConfigSection.get().timeout
```

The application includes the Section in its Container, under a name of its own choice,
and loads the config:

```python
# app_config.py, in the application
from lib_config import MyLibConfigSection

from application_settings import ConfigBase, config_filepath_from_cli, dataclass


@dataclass(frozen=True)
class MyAppConfig(ConfigBase):
    """Config of my application"""

    lib_config: MyLibConfigSection = MyLibConfigSection()


config_filepath_from_cli(MyAppConfig, load=True)
```

Whoever deploys the application sets the parameter of the library in the config file of
the application, next to the parameters of the application itself:

```toml
[lib_config]
timeout = 30
```

The library did not choose a file format or a location, and without a file it still works
with its defaults. References such as `${env:NAME}` and `${secret:NAME}` can be used in
`[lib_config]` as well, because the file belongs to the application.

A runnable version of this example is in the folder
[`examples/Recipies/loading`](https://github.com/StockwatchDev/application_settings/tree/develop/examples/Recipies/loading).
A real library that is built this way is
[loguru_configurable](https://github.com/StockwatchDev/loguru_configurable), which adds a
Section to [loguru](https://github.com/Delgan/loguru): the application includes it in its
Container as `loguru_config`, and the deployer sets the handlers and levels of the logging
in the `[loguru_config]` part of the config file.

## Limits

- There is one instance per Section class. Hence, a library cannot be used with two
  different sets of parameters in the same process, and a Section class that occurs
  twice in a Container is not supported: `get()` returns the one that was stored last.
- Section and Container have to be of the same kind: a config Section belongs in a
  config Container, a settings Section in a settings Container. This is not checked
  yet.

## Settings in a library

A library can also define settings, with a settings Section. Then keep in mind that:

- the application has to include the Section in its settings Container, and changes are
  saved through that Container with `update()`; a Section has no `update()`, so a
  library cannot change and save its own settings;
- values can change after loading, so call `get()` every time you need a value and do not
  keep the result;
- the library is not notified of a change;
- settings can not hold a `Secret`;
- if the application does not use `application_settings` and calls `set()`, the values
  are only kept in memory and the application has to save them itself.
