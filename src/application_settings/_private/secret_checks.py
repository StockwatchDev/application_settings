"""Checks on parameters that are declared as Secret."""

import dataclasses
import logging
from collections.abc import Mapping
from typing import Any, get_origin, get_type_hints

from pydantic import Secret

from application_settings._private.references import ResolutionReport

logger = logging.getLogger(__name__)


class SecretsError(ValueError):
    """Raised, in strict mode, when a secret parameter does not come from a secrets store.

    Messages name the parameters but never their values.
    """


def secret_field_paths(cls: type) -> list[str]:
    """Return the dotted paths, like 'section.password', of all Secret parameters of a dataclass."""
    if not dataclasses.is_dataclass(cls):
        return []
    hints = get_type_hints(cls)
    paths: list[str] = []
    for fld in dataclasses.fields(cls):
        hint = hints[fld.name]
        if hint is Secret or get_origin(hint) is Secret:
            paths.append(fld.name)
        elif isinstance(hint, type):
            paths.extend(f"{fld.name}.{path}" for path in secret_field_paths(hint))
    return paths


def forbid_secrets(instance: object) -> None:
    """Raise a TypeError if a Settings instance has Secret parameters.

    Settings are written back to file, secrets must never end up there.
    """
    if paths := secret_field_paths(type(instance)):
        raise TypeError(
            f"{type(instance).__name__} has Secret parameter(s) {', '.join(paths)}; "
            "Secret is only supported in Config, not in Settings."
        )


def check_secrets(
    instance: object,
    data: Mapping[str, Any],
    report: ResolutionReport,
    strict: bool,
) -> None:
    """Check that the secrets of a Config instance are Secrets that came from a store.

    A secret that was set by a default (in the code or in a reference) or by a literal
    in the file is logged as a warning, or, if strict, raised as a SecretsError.

    Raises:
        TypeError: if a secret parameter has a value that is not a Secret
        SecretsError: if strict and a secret does not come from a store
    """
    offenders: list[str] = []
    for path in secret_field_paths(type(instance)):
        if not isinstance(_get_path(instance, path), Secret):
            raise TypeError(
                f"Parameter '{path}' is declared as Secret but its value is not; "
                "use Secret(...) for its default value."
            )
        if path in report.from_reference:
            continue
        if path in report.from_default:
            origin = "the default in its reference"
        elif _has_path(data, path):
            origin = "a literal value in the file"
        else:
            origin = "its default in the code"
        offenders.append(
            f"Secret parameter '{path}' does not come from a secrets store, "
            f"its value is set by {origin}."
        )
    if offenders and strict:
        raise SecretsError("\n".join(offenders))
    for offender in offenders:
        logger.warning(offender)


def _get_path(instance: object, path: str) -> Any:
    for name in path.split("."):
        instance = getattr(instance, name)
    return instance


def _has_path(data: Mapping[str, Any], path: str) -> bool:
    current: Any = data
    for name in path.split("."):
        if not isinstance(current, Mapping) or name not in current:
            return False
        current = current[name]
    return True
