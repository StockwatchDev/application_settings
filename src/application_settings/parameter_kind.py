"""Module that defines the ParameterKind enum and a type for the collected values."""

from enum import Enum, unique
from typing import Literal


@unique
class ParameterKind(Enum):
    """The two kinds of parameters that are supported by application_settings"""

    CONFIG = "Config"
    SETTINGS = "Settings"


ParameterKindStr = Literal["Config", "Settings"]
