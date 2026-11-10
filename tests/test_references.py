"""Test the module application_settings._private.references"""

import pytest

from application_settings._private.references import (
    Reference,
    ReferenceSyntaxError,
    parse,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("${env:MY_VAR}", Reference("env", "MY_VAR", None)),
        ("${env:MY_VAR,fallback}", Reference("env", "MY_VAR", "fallback")),
        ("${file:db_password}", Reference("file", "db_password", None)),
        (
            "${file:db-password.txt,fallback}",
            Reference("file", "db-password.txt", "fallback"),
        ),
    ],
)
def test_parse_reference(value: str, expected: Reference) -> None:
    assert parse(value) == expected


@pytest.mark.parametrize(
    "value, expected_default",
    [
        ("${env:X,a,b,c}", "a,b,c"),  # the default is everything after the first comma
        ("${env:X,}", ""),  # an empty default is not the same as no default
        ("${env:X, padded }", " padded "),  # the default is taken as is
        ("${env:X,a}b}", "a}b"),  # the closing brace is the last character
        ("${env:X,${env:Y}}", "${env:Y}"),  # no nesting: the default is plain text
    ],
)
def test_parse_default(value: str, expected_default: str) -> None:
    result = parse(value)
    assert isinstance(result, Reference)
    assert result.name == "X"
    assert result.default == expected_default


@pytest.mark.parametrize(
    "value",
    [
        "",
        "plain text",
        "42",
        "env:MY_VAR",  # no braces
        "$MY_VAR",  # shell style is not supported
        "a-${env:MY_VAR}",  # a reference must be the whole value
        "${env:MY_VAR}-b",
        "${env:MY_VAR",  # not closed, so not a reference
        "{env:MY_VAR}",
    ],
)
def test_parse_literal(value: str) -> None:
    assert parse(value) == value


@pytest.mark.parametrize(
    "value, expected",
    [
        ("$${env:MY_VAR}", "${env:MY_VAR}"),
        ("$${env:MY_VAR,fallback}", "${env:MY_VAR,fallback}"),
        ("$${file:name}", "${file:name}"),
        ("$${anything}", "${anything}"),  # escaping does not depend on the content
        ("cost: $$5", "cost: $$5"),  # a double dollar elsewhere is left alone
    ],
)
def test_parse_escape(value: str, expected: str) -> None:
    assert parse(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "${}",
        "${env:}",  # empty name
        "${env:,default}",
        "${env}",  # no scheme separator
        "${unknown:NAME}",  # unknown scheme
        "${ENV:NAME}",  # schemes are case sensitive
        "${env: NAME}",  # no whitespace in names
        "${env:NAME }",
        "${env:A} and ${env:B}",  # looks like one reference but is not
        "${env:a/b}",  # no path separators in names
    ],
)
def test_parse_invalid_reference(value: str) -> None:
    with pytest.raises(ReferenceSyntaxError):
        parse(value)


def test_syntax_error_is_a_value_error() -> None:
    assert issubclass(ReferenceSyntaxError, ValueError)


def test_syntax_error_names_the_reference() -> None:
    with pytest.raises(ReferenceSyntaxError, match="unknown"):
        parse("${unknown:NAME}")


def test_reference_is_immutable() -> None:
    reference = Reference("env", "X", None)
    with pytest.raises(AttributeError):
        reference.name = "Y"  # type: ignore[misc]
