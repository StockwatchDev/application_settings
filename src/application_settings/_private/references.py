"""Parsing of references to environment variables and files in parameter values.

A reference must be the whole value of a parameter:

- `${env:NAME}` or `${env:NAME,default}` refers to an environment variable;
- `${file:NAME}` or `${file:NAME,default}` refers to a file in the secrets folder.

A value that starts with `$${` is not a reference, the leading `$` is an escape
that is removed: `$${env:NAME}` becomes the literal `${env:NAME}`.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

Scheme = Literal["env", "file"]

_SCHEMES: tuple[Scheme, ...] = ("env", "file")
_REFERENCE = re.compile(r"\$\{(?P<body>.*)\}", re.DOTALL)
_NAME = re.compile(r"[\w.-]+")


def _is_valid_name(name: str) -> bool:
    # '.' and '..' match the pattern but are not names; they would escape the secrets folder
    return bool(_NAME.fullmatch(name)) and name not in (".", "..")


class ReferenceSyntaxError(ValueError):
    """Raised when a value has the shape of a reference but is malformed."""


class ReferenceResolutionError(ValueError):
    """Raised when a reference cannot be resolved and has no default.

    Messages name the reference but never a value or a default, these may be secrets.
    """


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
    if not _is_valid_name(name):
        # the default is deliberately left out of the message, it may be a secret
        raise ReferenceSyntaxError(
            f"Invalid reference: '{name}' is not a valid name for scheme '{scheme}'."
        )
    return Reference(scheme, name, default if has_default else None)


@dataclass(frozen=True)
class ReferenceContext:
    """Where references are resolved from; secrets_dir is None if not configured."""

    env: Mapping[str, str]
    secrets_dir: Path | None = None


@dataclass(frozen=True)
class Resolved:
    """The outcome of resolving a reference; from_default is True if the default was used."""

    value: str
    from_default: bool


def resolve(reference: Reference, context: ReferenceContext) -> Resolved:
    """Resolve a reference; fall back to its default if it cannot be found.

    Raises:
        ReferenceSyntaxError: if a file reference has an unsafe name
        ReferenceResolutionError: if the reference cannot be found and has no default,
            or if a secret file exists but cannot be read
    """
    if reference.scheme == "env":
        value = context.env.get(reference.name)
        problem = f"Environment variable '{reference.name}' is not set."
    else:
        value, problem = _read_secret_file(reference.name, context.secrets_dir)

    if value is not None:
        return Resolved(value, False)
    if reference.default is not None:
        return Resolved(reference.default, True)
    raise ReferenceResolutionError(problem)


def _read_secret_file(name: str, secrets_dir: Path | None) -> tuple[str | None, str]:
    """Return the content of the file and a problem description in case it is missing."""
    # Reference objects need not come from parse(), so do not rely on its name check;
    # this is what keeps the lookup inside the secrets folder.
    if not _is_valid_name(name):
        raise ReferenceSyntaxError(
            f"Invalid file reference: '{name}' is not a valid file name."
        )
    if secrets_dir is None:
        return None, f"File '{name}' cannot be found: no secrets_dir has been set."
    path = secrets_dir / name
    # symlinks are followed on purpose, kubernetes mounts secrets that way
    if not path.is_file():
        return None, f"File '{name}' not found in the secrets folder."
    try:
        content = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ReferenceResolutionError(
            f"File '{name}' in the secrets folder cannot be read ({type(error).__name__})."
        ) from None
    return content.rstrip("\r\n"), ""


@dataclass(frozen=True)
class ResolutionReport:
    """Where the values came from, as dotted paths like 'section.field' or 'hosts[0]'.

    A value that is in the data but in neither set is a literal.
    """

    from_reference: frozenset[str] = frozenset()
    from_default: frozenset[str] = frozenset()


def resolve_references(
    data: Mapping[str, Any], context: ReferenceContext
) -> tuple[dict[str, Any], ResolutionReport]:
    """Return a copy of data with all references resolved, and a report on the origin.

    Raises:
        ReferenceResolutionError: if one or more references are malformed or cannot be
            resolved; the message lists all of them, by path
    """
    from_reference: set[str] = set()
    from_default: set[str] = set()
    problems: list[str] = []

    def walk(value: Any, path: str) -> Any:
        if isinstance(value, str):
            return resolve_value(value, path)
        if isinstance(value, Mapping):
            prefix = f"{path}." if path else ""
            return {key: walk(item, f"{prefix}{key}") for key, item in value.items()}
        if isinstance(value, list):
            return [walk(item, f"{path}[{index}]") for index, item in enumerate(value)]
        return value

    def resolve_value(value: str, path: str) -> str:
        try:
            parsed = parse(value)
            if isinstance(parsed, str):
                return parsed
            resolved = resolve(parsed, context)
        except (ReferenceSyntaxError, ReferenceResolutionError) as error:
            problems.append(f"  {path}: {error}")
            return value
        (from_default if resolved.from_default else from_reference).add(path)
        return resolved.value

    result = walk(data, "")
    if problems:
        raise ReferenceResolutionError(
            "References that cannot be resolved:\n" + "\n".join(problems)
        )
    return result, ResolutionReport(frozenset(from_reference), frozenset(from_default))
