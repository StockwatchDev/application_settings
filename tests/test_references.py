"""Test the module application_settings._private.references"""

import logging
import os
from pathlib import Path

import pytest

from application_settings._private.references import (
    Reference,
    ReferenceContext,
    ReferenceResolutionError,
    ReferenceSyntaxError,
    ResolutionReport,
    Resolved,
    build_context,
    parse,
    resolve,
    resolve_references,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("${env:MY_VAR}", Reference("env", "MY_VAR", None)),
        ("${env:MY_VAR,fallback}", Reference("env", "MY_VAR", "fallback")),
        ("${secret:db_password}", Reference("secret", "db_password", None)),
        (
            "${secret:db-password.txt,fallback}",
            Reference("secret", "db-password.txt", "fallback"),
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
        ("$${secret:name}", "${secret:name}"),
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
        "${secret:..}",  # would point outside the secrets folder
        "${secret:.}",
        "${secret:..,default}",
        "${env:..}",  # names are validated the same way for every scheme
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


# --- resolve ---


def test_resolve_env() -> None:
    context = ReferenceContext(env={"X": "value"}, secrets_dir=None)
    assert resolve(Reference("env", "X"), context) == Resolved("value", False)


def test_resolve_env_ignores_default_if_set() -> None:
    context = ReferenceContext(env={"X": "value"}, secrets_dir=None)
    assert resolve(Reference("env", "X", "fallback"), context) == Resolved(
        "value", False
    )


def test_resolve_env_empty_value_counts_as_set() -> None:
    context = ReferenceContext(env={"X": ""}, secrets_dir=None)
    assert resolve(Reference("env", "X", "fallback"), context) == Resolved("", False)


def test_resolve_env_default() -> None:
    context = ReferenceContext(env={}, secrets_dir=None)
    assert resolve(Reference("env", "X", "fallback"), context) == Resolved(
        "fallback", True
    )
    assert resolve(Reference("env", "X", ""), context) == Resolved("", True)


def test_resolve_env_missing() -> None:
    context = ReferenceContext(env={}, secrets_dir=None)
    with pytest.raises(ReferenceResolutionError, match="X"):
        resolve(Reference("env", "X"), context)


def test_resolve_file(tmp_path: Path) -> None:
    (tmp_path / "pw").write_text("s3cret", encoding="utf-8")
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    assert resolve(Reference("secret", "pw"), context) == Resolved("s3cret", False)


@pytest.mark.parametrize("content", ["s3cret\n", "s3cret\r\n"])
def test_resolve_file_strips_trailing_newline(tmp_path: Path, content: str) -> None:
    (tmp_path / "pw").write_bytes(content.encode("utf-8"))
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    assert resolve(Reference("secret", "pw"), context).value == "s3cret"


def test_resolve_file_keeps_other_whitespace(tmp_path: Path) -> None:
    (tmp_path / "pw").write_text(" s3 cret ", encoding="utf-8")
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    assert resolve(Reference("secret", "pw"), context).value == " s3 cret "


def test_resolve_file_reads_utf8(tmp_path: Path) -> None:
    (tmp_path / "pw").write_bytes("wachtwoord-é".encode("utf-8"))
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    assert resolve(Reference("secret", "pw"), context).value == "wachtwoord-é"


def test_resolve_file_does_not_use_the_environment(tmp_path: Path) -> None:
    context = ReferenceContext(env={"pw": "from env"}, secrets_dir=tmp_path)
    with pytest.raises(ReferenceResolutionError):
        resolve(Reference("secret", "pw"), context)


def test_resolve_file_default_if_missing(tmp_path: Path) -> None:
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    assert resolve(Reference("secret", "pw", "fallback"), context) == Resolved(
        "fallback", True
    )


def test_resolve_file_missing(tmp_path: Path) -> None:
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    with pytest.raises(ReferenceResolutionError, match="pw"):
        resolve(Reference("secret", "pw"), context)


def test_resolve_file_is_a_directory(tmp_path: Path) -> None:
    (tmp_path / "pw").mkdir()
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    with pytest.raises(ReferenceResolutionError):
        resolve(Reference("secret", "pw"), context)


def test_resolve_file_no_secrets_dir() -> None:
    context = ReferenceContext(env={}, secrets_dir=None)
    with pytest.raises(ReferenceResolutionError, match="secrets_dir"):
        resolve(Reference("secret", "pw"), context)
    assert resolve(Reference("secret", "pw", "fallback"), context) == Resolved(
        "fallback", True
    )


def test_resolve_file_secrets_dir_does_not_exist(tmp_path: Path) -> None:
    context = ReferenceContext(env={}, secrets_dir=tmp_path / "nope")
    with pytest.raises(ReferenceResolutionError):
        resolve(Reference("secret", "pw"), context)


def test_resolve_file_unreadable_content_is_not_replaced_by_default(
    tmp_path: Path,
) -> None:
    (tmp_path / "pw").write_bytes(b"\xff\xfe\x00bad")
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    with pytest.raises(ReferenceResolutionError, match="pw"):
        resolve(Reference("secret", "pw", "fallback"), context)


@pytest.mark.parametrize(
    "name", ["..", ".", "../pw", "sub/pw", "sub\\pw", "/etc/passwd", "C:\\pw", ""]
)
def test_resolve_file_rejects_unsafe_names(tmp_path: Path, name: str) -> None:
    (tmp_path / "pw").write_text("s3cret", encoding="utf-8")
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    # a default must not hide an unsafe name, and must not end up in the message
    with pytest.raises(ReferenceSyntaxError) as excinfo:
        resolve(Reference("secret", name, "default-value"), context)
    assert "default-value" not in str(excinfo.value)


def test_resolve_file_follows_symlinks_in_secrets_dir(tmp_path: Path) -> None:
    # kubernetes mounts secrets as symlinks into a hidden, timestamped folder
    data_dir = tmp_path / "..data"
    data_dir.mkdir()
    (data_dir / "pw").write_text("s3cret", encoding="utf-8")
    try:
        (tmp_path / "pw").symlink_to(Path("..data") / "pw")
    except OSError:
        pytest.skip("symlinks are not available on this system")
    context = ReferenceContext(env={}, secrets_dir=tmp_path)
    assert resolve(Reference("secret", "pw"), context).value == "s3cret"


def test_resolution_errors_never_contain_the_default() -> None:
    context = ReferenceContext(env={}, secrets_dir=None)
    with pytest.raises(ReferenceResolutionError) as excinfo:
        resolve(Reference("secret", "pw"), context)
    assert "s3cret" not in str(excinfo.value)
    assert issubclass(ReferenceResolutionError, ValueError)


# --- resolve_references ---


def _context(tmp_path: Path | None = None, **env: str) -> ReferenceContext:
    return ReferenceContext(env=env, secrets_dir=tmp_path)


def test_resolve_references_without_references() -> None:
    data = {"a": 1, "b": "text", "c": {"d": 2.5, "e": [1, "x"]}, "f": True}
    resolved, report = resolve_references(data, _context())
    assert resolved == data
    assert report == ResolutionReport()


def test_resolve_references_nested(tmp_path: Path) -> None:
    (tmp_path / "pw").write_text("s3cret", encoding="utf-8")
    data = {
        "name": "${env:APP_NAME}",
        "section": {"password": "${secret:pw}", "sub": {"port": "${env:PORT}"}},
    }
    resolved, _ = resolve_references(
        data, _context(tmp_path, APP_NAME="app", PORT="8080")
    )
    assert resolved == {
        "name": "app",
        "section": {"password": "s3cret", "sub": {"port": "8080"}},
    }


def test_resolve_references_in_lists() -> None:
    data = {"hosts": ["${env:A}", "fixed", {"name": "${env:B}"}]}
    resolved, report = resolve_references(data, _context(A="a", B="b"))
    assert resolved == {"hosts": ["a", "fixed", {"name": "b"}]}
    assert report.from_reference == {"hosts[0]", "hosts[2].name"}


def test_resolve_references_keeps_other_types_and_keys() -> None:
    data = {"${env:A}": "x", "n": 3, "flag": False, "nothing": None}
    resolved, report = resolve_references(data, _context(A="a"))
    assert resolved == data  # keys are never resolved
    assert report == ResolutionReport()


def test_resolve_references_does_not_modify_its_input() -> None:
    data = {"a": {"b": "${env:X}"}, "c": ["${env:X}"]}
    resolve_references(data, _context(X="x"))
    assert data == {"a": {"b": "${env:X}"}, "c": ["${env:X}"]}


def test_resolve_references_report() -> None:
    data = {
        "from_env": "${env:SET}",
        "from_default": "${env:UNSET,fallback}",
        "section": {"also_default": "${env:UNSET,}", "literal": "plain", "number": 1},
    }
    resolved, report = resolve_references(data, _context(SET="value"))
    assert resolved["from_default"] == "fallback"
    assert report.from_reference == {"from_env"}
    assert report.from_default == {"from_default", "section.also_default"}


def test_resolve_references_escaped_value_is_a_literal() -> None:
    resolved, report = resolve_references({"a": "$${env:X}"}, _context(X="x"))
    assert resolved == {"a": "${env:X}"}
    assert report == ResolutionReport()


def test_resolve_references_collects_all_problems(tmp_path: Path) -> None:
    (tmp_path / "ok").write_text("s3cret", encoding="utf-8")
    data = {
        "good": "${secret:ok}",
        "missing_env": "${env:NOPE}",
        "section": {"missing_file": "${secret:nope}", "bad": "${unknown:X}"},
        "items": ["${env:NOPE2}"],
    }
    with pytest.raises(ReferenceResolutionError) as excinfo:
        resolve_references(data, _context(tmp_path))
    message = str(excinfo.value)
    for path in ("missing_env", "section.missing_file", "section.bad", "items[0]"):
        assert path in message
    assert "good" not in message
    assert "NOPE" in message and "nope" in message
    assert "s3cret" not in message  # values of references that did resolve


def test_resolve_references_problems_never_show_defaults() -> None:
    data = {"a": "${secret:../x,hunter2}", "b": "${secret:missing}"}
    with pytest.raises(ReferenceResolutionError) as excinfo:
        resolve_references(data, _context())
    assert "hunter2" not in str(excinfo.value)


# --- build_context ---


def test_build_context_uses_the_environment_by_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("APPSET_TEST_VAR", "from environment")
    context = build_context("", "", tmp_path)
    assert context.env["APPSET_TEST_VAR"] == "from environment"


def test_build_context_nothing_configured(tmp_path: Path) -> None:
    context = build_context("", "", tmp_path, environ={"A": "a"})
    assert dict(context.env) == {"A": "a"}
    assert context.secrets_dir is None


def test_build_context_reads_dotenv(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("A=from dotenv\nB=b\n", encoding="utf-8")
    context = build_context(".env", "", tmp_path, environ={"C": "c"})
    assert dict(context.env) == {"A": "from dotenv", "B": "b", "C": "c"}


def test_build_context_real_environment_wins(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("A=from dotenv\nB=b\n", encoding="utf-8")
    context = build_context(".env", "", tmp_path, environ={"A": "real"})
    assert context.env["A"] == "real"
    assert context.env["B"] == "b"


def test_build_context_does_not_touch_os_environ(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("APPSET_ONLY_IN_DOTENV", raising=False)
    (tmp_path / ".env").write_text("APPSET_ONLY_IN_DOTENV=x\n", encoding="utf-8")
    before = dict(os.environ)
    context = build_context(".env", "", tmp_path)
    assert context.env["APPSET_ONLY_IN_DOTENV"] == "x"
    assert dict(os.environ) == before
    assert "APPSET_ONLY_IN_DOTENV" not in os.environ


def test_build_context_is_a_snapshot(tmp_path: Path) -> None:
    environ = {"A": "a"}
    context = build_context("", "", tmp_path, environ=environ)
    environ["A"] = "changed"
    environ["B"] = "new"
    assert dict(context.env) == {"A": "a"}


def test_build_context_dotenv_path_relative_to_config_dir(tmp_path: Path) -> None:
    (tmp_path / "conf").mkdir()
    (tmp_path / "conf" / "my.env").write_text("A=a\n", encoding="utf-8")
    context = build_context("my.env", "", tmp_path / "conf", environ={})
    assert context.env["A"] == "a"


def test_build_context_dotenv_absolute_path(tmp_path: Path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    (other / "x.env").write_text("A=a\n", encoding="utf-8")
    context = build_context(
        str(other / "x.env"), "", tmp_path / "unrelated", environ={}
    )
    assert context.env["A"] == "a"


def test_build_context_dotenv_syntax(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text(
        "# comment\n\nexport A=exported\nB='single quoted'\nC=\"double quoted\"\n"
        "NO_VALUE\nD=a${A}c\n",
        encoding="utf-8",
    )
    context = build_context(".env", "", tmp_path, environ={})
    assert context.env["A"] == "exported"
    assert context.env["B"] == "single quoted"
    assert context.env["C"] == "double quoted"
    assert "NO_VALUE" not in context.env  # a key without a value is not a value
    assert context.env["D"] == "a${A}c"  # no interpolation, the text is kept as is


@pytest.mark.parametrize("kind", ["missing", "directory"])
def test_build_context_unusable_dotenv_warns_and_continues(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, kind: str
) -> None:
    if kind == "directory":
        (tmp_path / ".env").mkdir()
    with caplog.at_level(logging.WARNING):
        context = build_context(".env", "", tmp_path, environ={"A": "a"})
    assert dict(context.env) == {"A": "a"}
    assert any(
        record.levelno == logging.WARNING and ".env" in record.getMessage()
        for record in caplog.records
    )


def test_build_context_secrets_dir(tmp_path: Path) -> None:
    context = build_context("", "secrets", tmp_path, environ={})
    assert context.secrets_dir == tmp_path / "secrets"
    absolute = tmp_path / "elsewhere"
    context = build_context("", str(absolute), tmp_path / "conf", environ={})
    assert context.secrets_dir == absolute


def test_build_context_secrets_dir_does_not_have_to_exist(tmp_path: Path) -> None:
    # it only matters when a file reference needs it
    context = build_context("", "nope", tmp_path, environ={})
    assert context.secrets_dir == tmp_path / "nope"


def test_build_context_end_to_end(tmp_path: Path) -> None:
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "pw").write_text("s3cret\n", encoding="utf-8")
    (tmp_path / ".env").write_text("USER_NAME=from dotenv\nPORT=1\n", encoding="utf-8")
    context = build_context(".env", "secrets", tmp_path, environ={"PORT": "2"})
    data = {"user": "${env:USER_NAME}", "port": "${env:PORT}", "pw": "${secret:pw}"}
    resolved, _ = resolve_references(data, context)
    assert resolved == {"user": "from dotenv", "port": "2", "pw": "s3cret"}
