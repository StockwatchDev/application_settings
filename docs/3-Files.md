### Write a config file

For the example, the config file `~/.my_example/config.toml` could be something like this:

```toml
[section1]
field1 = "my own version of field1"
field2 = 22
```

The section names in this file are equal to the fieldnames of your container class and the
entries in a section consist of the fieldnames of your ConfigSection class(es).
The order of sections and/or fields in the toml file does not have to adhere to the order
in which fields have been specified in the Config(Section) classes.

## Location of the config file

The path for the config file can be specified via the optional argument `configfile_path`
of the `get` method that creates the singleton. The path is not stored; if you `reload`
then you again have to pass the `configfile_path`.

You can specify the path either as a string or as a pathlib `Path`. In case of a string
spec, it is first validated for the platform that you are using; if the validation fails,
a `ValueError` is raised, otherwise a `Path` is constructed from the string.

If you do not specify a `configfile_path`, then a default location is fetched via
`default_filepath()`. Class `ConfigBase` provides a default implementation, being
a filename `config.toml` located in a subfolder of your home directory. The default name
of that subfolder is provided by `default_foldername()` and consists
of a dot, followed by a name derived from your container class: the word `Config` is
removed, underscores in front of capitals (except for the first letter) and all lower case.
See also the example above. If you do not like the default implementation, you can
override `default_filepath()` and/or `default_foldername()`. If you want to
enforce that a `configfile_path` is specified in `get()`, then let
`default_filepath()` return `None`.
