### Define config section(s) and the container with application info

Example:

```python
from application_settings import (
    ConfigBase,
    ConfigSectionBase,
)
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class MyExample1ConfigSection(ConfigSectionBase):
    """Config section for an example"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class MyExampleConfig(ConfigBase):
    """Config for an example"""

    section1: MyExample1ConfigSection = MyExample1ConfigSection()

```

Note: a `pydantic.dataclasses.dataclass` is a drop-in replacement for the standard
`dataclasses.dataclass`, with validation, see
[pydantic dataclasses](https://docs.pydantic.dev/usage/dataclasses/).
