"""Checks on parameters that are declared as Secret."""

import dataclasses
import logging
from collections.abc import Mapping
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from pydantic import Secret, ValidationError

from application_settings._private.references import ResolutionReport

logger = logging.getLogger(__name__)

REDACTED = "**********"

# Optional[X] is a typing.Union, X | None a types.UnionType (the same from python 3.14)
_UNION_ORIGINS = (Union, UnionType)  # pylint: disable=consider-alternative-union-syntax


class SecretsError(ValueError):
    """Raised, in strict mode, when a secret parameter does not come from a secrets store.

    Messages name the parameters but never their values.
    """


def secret_field_paths(cls: type) -> list[str]:
    """Return the dotted paths, like 'section.password', of the Secret parameters of a dataclass.

    These are the parameters declared as Secret[...] or Secret[...] | None, also in
    nested sections; their origin can be checked.
    """
    return _paths(cls, deep=False, seen={cls})


def sensitive_field_paths(cls: type) -> list[str]:
    """Return the dotted paths of all parameters that hold a Secret, wholly or in part.

    Besides the paths of secret_field_paths, this includes parameters in which a Secret
    is nested deeper, like list[Secret[int]] or list[SectionWithSecret].
    """
    return _paths(cls, deep=True, seen={cls})


def _is_secret(hint: Any) -> bool:
    return hint is Secret or get_origin(hint) is Secret


def _without_none(hint: Any) -> Any:
    """Return X for X | None (or Optional[X]), otherwise hint."""
    if get_origin(hint) in _UNION_ORIGINS:
        others = [arg for arg in get_args(hint) if arg is not NoneType]
        if len(others) == 1:
            return others[0]
    return hint


def _contains_secret(hint: Any, seen: set[type]) -> bool:
    if _is_secret(hint):
        return True
    if isinstance(hint, type) and dataclasses.is_dataclass(hint):
        return hint not in seen and bool(_paths(hint, deep=True, seen=seen | {hint}))
    return any(_contains_secret(arg, seen) for arg in get_args(hint))


def _paths(cls: type, deep: bool, seen: set[type]) -> list[str]:
    # seen guards against sections that contain themselves
    if not dataclasses.is_dataclass(cls):
        return []
    hints = get_type_hints(cls)
    paths: list[str] = []
    for fld in dataclasses.fields(cls):
        hint = hints[fld.name]
        if _is_secret(_without_none(hint)):
            paths.append(fld.name)
        elif isinstance(hint, type):
            if hint not in seen:
                paths.extend(
                    f"{fld.name}.{path}" for path in _paths(hint, deep, seen | {hint})
                )
        elif deep and _contains_secret(hint, seen):
            paths.append(fld.name)
    return paths


def forbid_secrets(instance: object) -> None:
    """Raise a TypeError if a Settings instance has Secret parameters.

    Settings are written back to file, secrets must never end up there.
    """
    if paths := sensitive_field_paths(type(instance)):
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
        if (value := _get_path(instance, path)) is None:
            continue  # an optional secret that is not given: nothing to protect
        if not isinstance(value, Secret):
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


def redact_validation_error(error: ValidationError, cls: type) -> ValidationError:
    """Return the error with the input hidden where it may contain a secret value.

    Pydantic includes the offending input in its errors. That is a secret for a Secret
    parameter, and pydantic also reports the whole set of arguments (and so all secrets)
    as the input of an error such as a missing parameter. The error is returned as is
    if cls has no secret parameters.
    """
    if not (
        secret_paths := [tuple(path.split(".")) for path in sensitive_field_paths(cls)]
    ):
        return error

    def is_sensitive(loc: tuple[Any, ...], value: Any) -> bool:
        if not isinstance(value, (str, int, float, bool, type(None))):
            return True  # e.g. all arguments, or a table: may hold any of the secrets
        # the error is for a secret, or for a section that holds a secret
        return any(
            loc[: len(path)] == path or path[: len(loc)] == loc for path in secret_paths
        )

    details = error.errors(include_url=False)
    # entries are pydantic_core.InitErrorDetails; that is not imported, because it is
    # not a direct dependency of this package
    init_errors: list[Any] = []
    for detail in details:
        init_error: dict[str, Any] = {
            "type": detail["type"],
            "loc": detail["loc"],
            "input": (
                REDACTED
                if is_sensitive(detail["loc"], detail["input"])
                else detail["input"]
            ),
        }
        if "ctx" in detail:
            init_error["ctx"] = detail["ctx"]
        init_errors.append(init_error)
    try:
        return ValidationError.from_exception_data(error.title, init_errors)
    except (TypeError, ValueError, KeyError):
        # better to show less than to risk showing a secret
        locs = ", ".join(".".join(str(part) for part in d["loc"]) for d in details)
        raise ValueError(
            f"{error.title}: invalid value for {locs}. Details are not shown "
            "because there are secret parameters."
        ) from None


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
