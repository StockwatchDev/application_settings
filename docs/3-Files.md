# Files and file location

## Files for storing parameters

A Container class defines a root section and provides for behavior to load parameter
values from files and, in case of settings, store updated values to files.

Currently, two formats are supported for persistent storage of parameters:
[`toml`](https://toml.io/en/) and [`json`](https://www.json.org/).

The `toml` format is human-oriented, flexible, standardardized and not overly complex.
It supports comments, and hence parameters can be easily documented in a toml file.
However, when parameters are initialized by reading from a toml file, then changed
(because it concerns settings) and subsequently written to file again for persistance,
the comments will be lost. Therefore, it does not make much sense to add documenting
comments to a settings file. Because config parameters are read-only, comments in a
config file will not get lost and do make sense. Because of this, the default format for
storing config parameters is `toml`. The name of a config file equals `config.toml` by
default.

JSON is a standardized, lightweight data-interchange format that is easy for machines to
parse and generate. It is a bit less straightforward to document parameters in this
format, which makes it less human-oriented than `toml`, but it is used widely for data
interchange between automated systems. Because of this, the default format for storing
settings parameters is `json`. The name of a settings file equals `settings.json` by
default.

The examples introduced in the previous chapter can for example be initialized with the
following files.

=== "`config.toml` file for the configuration example"
    ```toml
    # Use this file to set the config that you prefer by editing the file
    name = "application specific name"
    [section1]
    # field1 has default value 0.5
    field1 = -0.5
    # field2 has default value 2
    field2 = 22

    ```

=== "`settings.json` file for the settings example"
    ```json
    {
        "name": "the stored name",
        "basics": {
            "totals": 3
        }
    }

    ```

The field names of a Container class are found as:

- the root parameter names and the section names in the `toml` file
- the member names of the root object in the `json` file

The field names of a Section class are found as:

- the parameter names inside the corresponding section in the `toml` file
- the member names of the object that is the value of the name that represents the
  section in the `json` file

The order of sections and/or fields in the file does not have to adhere to the order
in which fields have been specified in the Container - or Section classes.

Presence of sections and/or fields in the files that are not defined in the classes goes
by silently.

Fields or complete sections defined in the classes can be absent in the files as long as
default values have been specified for all fields that have been left out. For more info
on data validation [click here](./6-Handling_deviations.md)

## Location, name and type of the file

By default, the config and settings files are located in a subfolder of the home folder of
the user running the application. The default name of that subfolder is provided by the
`default_foldername()` method and consists of a dot, followed by a name derived from your
container class: the word `Config`/`Settings` is removed, underscores are put in front of
capitals (except for the first letter) and all letters are made lower case. For example,
the Container class `MyExampleConfig` by default will store its config in
`~/.my_example/config.toml`. And `MyExampleSettings` will default to a settings file
`~/.my_example/settings.json`.

If you want the files to be stored in a different location and/or have a different name
and/or change the format, then you can use the method `set_filepath`. If you invoke this
method but you have already instantiated the parameters via `load()` or `get()`, then you
most likely want to reload them. You can do so by setting an argument `load=True` in
`set_filepath`. If you invoke this function after parameters have been instantiated and
do not set `load=True`, then a warning is printed. Example:

```python
# the next statement sets the location, name and format of the settings file
# the argument can be eiter a string or a Path
MyExampleSettings.set_filepath(r"C:\ProgramData\testsettings.toml")
# the next statement loads the settings
MyExampleSettings.load()
# the next statement sets a new name for the settings file and reloads it
MyExampleSettings.set_filepath(r"C:\ProgramData\productionsettings.toml", load=True)
# the next statement resets the filepath to the default, doesn't load but generates a warning
MyExampleSettings.set_filepath("")
```

The extension of the file is used to select the format for parsing and hence has to be
either `json`, `JSON`, `toml` or `TOML`.

## Setting the filepath via command-line arguments

A quite common scenario is to launch an application from the command-line and to specify
the config file and/or settings file as argument(s). Convenience functions are available
to support this using the [argparse](https://docs.python.org/3/library/argparse.html)
module from the standard library:

- a function `config_filepath_from_cli` is available that will define a command-line
  argument that takes exactly one additional argument, namely the config filepath.
  You have to specify the Config class when calling this function, and you may
  pass a parser (default: the main argument parser) and your own short option
  (default: `"-c"`) and long option (default:  `"--config_filepath"`) and you may
  set `load=True` (default: `False`). If the option is
  indeed supplied when the application is launched, then the config filepath is set using
  `set_filepath` and the value for `load` is passed into this function.
- a function `settings_filepath_from_cli` is available that will define a command-line
  argument that takes exactly one additional argument, namely the
  settings filepath. You have to specify the Settings class when calling this function,
  and you may pass a parser (default: the main argument parser) and your own short option
  (default: `"-s"`) and long option (default:  `"--settings_filepath"`) and you may set
  `load=True` (default: `False`). If the option is
  indeed supplied when the application is launched, then the config filepath is set using
  `set_filepath` and the value for `load` is passed into this function.
- a function `parameters_folderpath_from_cli` is also available and comes in handy when
  you have a config file and a settings file in the same folder. This function will
  define a command-line argument that takes exactly one
  additional argument, namely the path of the _folder_ that holds both files. Note that
  this implies that the config- and settings file have to have the default filename. You
  have to specify both the Settings class and the Config class when calling this function,
  and you may pass a parser (default: the main argument parser) and your own short option
  (default: `"-p"`) and long option (default:  `"--parameters_folderpath"`) and you may
  set `load=True` (default: `False`). If the option is
  indeed supplied when the application is launched, then the config and the settings
  filepath are set using `set_filepath` and the value for `load` is passed into these
  functions.

=== "CLI for config filepath"
    ```python
    from application_settings import config_filepath_from_cli

    # The next line defines a cli argument "-c" and "--config_filepath"
    # and specifies that the config should be loaded when it is specified
    config_filepath_from_cli(MyExampleConfig, load=True)
    # the application launch with config file spec could be something like:
    # application_name -c C:\ProgramData\productionconfig.toml
    ```

=== "CLI for settings filepath"
    ```python
    from application_settings import settings_filepath_from_cli

    # The next line defines a cli argument "-s" and "--settings_filepath"
    # and specifies that the settings should be loaded when it is specified
    settings_filepath_from_cli(MyExampleSettings, load=True)
    # the application launch with settings file spec could be something like:
    # application_name -s C:\ProgramData\productionsettings.json
    ```

=== "CLI for common config and settings folder"
    ```python
    from application_settings import parameters_folderpath_from_cli

    # The next line defines a cli argument "-p" and "--parameters_folderpath"
    # and specifies that the config and settings should be loaded when it is specified
    parameters_folderpath_from_cli(MyExampleConfig, MyExampleSettings, load=True)
    # the application launch with folder spec could be something like:
    # application_name -p C:\ProgramData
    ```

It is good practice make a separate module that defines the container class and the
sections and to add both the convenience function for setting the filepath via the
cli and the `load` statement in that module.
[This may help to prevent initialization problems.](7-Recipes.md#initialization-needs-to-depend-on-configuration)

## Handling FileNotFoundError

When loading a parameter file, you have a choice what should happen when the parameter
file is not found in the location that has been specified:

- if you `load(throw_if_file_not_found = False)`, then the `FileNotFoundError` is
  catched by `application_settings`, an error message is generated and program flow is
  continued by trying to instantiate the config / settings using default values. If you
  have defined parameters without default values, a TypeError exception will be raised.
- if you `load(throw_if_file_not_found = True)`, then the `FileNotFoundError` exception
  is thrown and the application can decide how this situation should be handled.

The default value for `throw_if_file_not_found` is `False`, hence `load()` will not throw
an exception when the parameter file is not found. Note that if you do not explicitly
use `load` but rather implicitly call it via `get()` or `set_filepath()`, then this
default behavior will also be obtained.

## Sharing parameters over different configs via file inclusion with toml

Another common scenario is that you work with different configurations for your
application but these different configurations are partially the same. To prevent
inconsistencies and config duplication, it is desirable to be able to share the common
part. For this purpose, `application_settings` provides a file inclusion mechanism
for `toml` configuration files.

Above, an example of such a config file was given. Suppose now that you want to create
several configurations that have a varying `name` but they will share the parametrization
`section1`. Then we can put that part in a file `config_common.toml` and include that
file from the different configurations.

=== "`config.toml` file for the configuration example"
    ```toml
    # Use this file to set the config that you prefer by editing the file
    name = "application specific name"
    __include__ = "./config_common.toml"

    ```

=== "`config_common.toml` (in the same folder)"
    ```toml
    [section1]
    # field1 has default value 0.5
    field1 = -0.5
    # field2 has default value 2
    field2 = 22

    ```

The file inclusion mechanism has been kept simple; the following rules apply:

- The key to use for specifying a file to include is `__include__`; hence, this key is
  to be treated as a keyword and is not available as field name.
- The value can be either a single path string or an array of path strings.
- File inclusion can only be specified at the top level, not inside a section.
- File inclusion is only available for configuration, not for settings, and only for the
  `toml` format.
- File inclusion can be nested, i.e., in the included `toml` file one can again specify
  another file to include (albeit at the top level only).
- If the included file specifies a key that was already specified in the file that does
  the inclusion, then it is disregarded and the key-value pair of the latter file is
  kept.
