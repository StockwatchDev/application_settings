# Handling deviations

## Handling deviations in the parameter file

### When your parameter file does not adhere to the specified types

When loading the parameter file, the values specified are coerced into the appropriate
type where possible. The details of the coersion are specified in this
[conversion table](https://docs.pydantic.dev/2.0/usage/conversion_table/) If type
coercion is not possible, then a `ValidationError` is raised (which is actually a
[`pydantic.ValidationError`](https://docs.pydantic.dev/latest/usage/validation_errors/)
that has been exported from our namespace). Consider the case where you would use the
following config file for the `MyExampleConfig` defined before:

```toml
[section1]
field1 = 4
field2 = "22"
```

The `int` specified for `field1` will be coerced into a `float` value of `4.0`.
The `str` specified for `field2` will be coerced into an `int` value of `22`.

### When your parameter file does not contain all specified attributes

If your Config or Settings has one of more sections with one or more attributes that do
not have a default value, then a parameter file must be loaded and these sections and
attributes must be present in the loaded parameter file. If this is not the case, a
`TypeError` is raised. Attributes that have default values can be omitted
from the parameter file without problems. Likewise, sections of which all attributes
have default values can also be omitted without problems.

Note that in the dataclass definitions, attributes without default value have to come
before attributes with default values.

### When your parameter file contains additional, unspecified attributes

Entries in a parameter file that are not defined in the Container or Section classes
will simply be ignored silently.

## More advanced typing and validation with pydantic

- Non-standard types useful for configuration or settings, such as FilePath,
  are offered, see [pydantic types](https://docs.pydantic.dev/latest/api/types/)
- In addition, a [network module](https://docs.pydantic.dev/latest/api/networks/) is
  provided by pydantic that contains types for common network-related fields
- The value of numeric types can be restricted using
  [pydantic constrained types](https://docs.pydantic.dev/latest/usage/types/number_types/#constrained-types)
