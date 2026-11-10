"""Parsing of references to environment variables and files in parameter values.

A reference must be the whole value of a parameter:

- `${env:NAME}` or `${env:NAME,default}` refers to an environment variable;
- `${file:NAME}` or `${file:NAME,default}` refers to a file in the secrets folder.

A value that starts with `$${` is not a reference, the leading `$` is an escape
that is removed: `$${env:NAME}` becomes the literal `${env:NAME}`.
"""

import re
from dataclasses import dataclass
from typing import Literal

Scheme = Literal["env", "file"]

_SCHEMES: tuple[Scheme, ...] = ("env", "file")
_REFERENCE = re.compile(r"\$\{(?P<body>.*)\}", re.DOTALL)
_NAME = re.compile(r"[\w.-]+")


class ReferenceSyntaxError(ValueError):
    """Raised when a value has the shape of a reference but is malformed."""


@dataclass(frozen=True)
class Reference:
    """A parsed reference; default is None if the reference does not specify one."""

    scheme: Scheme
    name: str
    default: str | None = None


def parse(value: str) -> Reference | str:
    """Return a Reference if value is one, otherwise the literal value.

    Raises:
        ReferenceSyntaxError: if value is of the form '${...}' but malformed
    """
    if value.startswith("$${"):
        return value[1:]
    if not (match := _REFERENCE.fullmatch(value)):
        return value

    scheme, separator, rest = match.group("body").partition(":")
    if not separator:
        raise ReferenceSyntaxError(
            "Invalid reference: expected '${env:NAME}' or '${file:NAME}'."
        )
    if scheme not in _SCHEMES:
        raise ReferenceSyntaxError(
            f"Invalid reference: unknown scheme '{scheme}', use one of {_SCHEMES}."
        )
    name, has_default, default = rest.partition(",")
    if not _NAME.fullmatch(name):
        # the default is deliberately left out of the message, it may be a secret
        raise ReferenceSyntaxError(
            f"Invalid reference: '{name}' is not a valid name for scheme '{scheme}'."
        )
    return Reference(scheme, name, default if has_default else None)
