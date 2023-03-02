## Handling deviations in the config file

### When your config file does not adhere to the specified types

When loading the config file, the values specified are coerced into the appropriate type
where possible. If type coercion is not possible, then a `pydantic.ValidationError`
is raised. Consider the case where you would use the following config file for
the `MyExampleConfig` defined above:

```toml
[section1]
field1 = true
field2 = "22"
```

The `bool` specified for `field1` will be coerced into a `str` value of `"true"`.
The `str` specified for `field2` will be coerced into an `int` value of `22`.

### When your config file does not contain all specified attributes

If your Config has one of more sections with attributes that do not have a default
value, then a config file must be loaded and these sections and attributes must be
present in the loaded config file. If this is not the case, a `TypeError` is raised.
Attributes that have default values can be omitted
from the config file without problems.

Note that in the dataclass definitions, attributes without default value have to come
before attributes with default values.

### When your config file contains additional, unspecified attributes

Entries in a config file that are not defined in the Config(Section) classes will simply
be ignored silently.

## More advanced typing and validation with pydantic

- Non-standard types useful for configuration, such as network addresses, are offered, see
  [pydantic types](https://docs.pydantic.dev/usage/types/#pydantic-types)
- The value of numerous common types can be restricted using
  [pydantic constrained types](https://docs.pydantic.dev/usage/types/#constrained-types)
