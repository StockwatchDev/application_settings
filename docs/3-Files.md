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
