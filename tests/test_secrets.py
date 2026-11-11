# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import logging
import traceback
from pathlib import Path
from typing import Literal

import pytest

from application_settings import (
    ConfigBase,
    ConfigSectionBase,
    ReferenceResolutionError,
    Secret,
    SecretsError,
    SettingsBase,
    SettingsSectionBase,
    ValidationError,
    dataclass,
)

HARDCODED = "hardcoded-value-1234"
STORE_WARNING = "does not come from a secrets store"


@dataclass(frozen=True)
class DbSection(ConfigSectionBase):
    """Section with a secret"""

    host: str = "localhost"
    password: Secret[str] = Secret(HARDCODED)  # a default: not from a store


@dataclass(frozen=True)
class StrictDbSection(ConfigSectionBase):
    """Section with a secret that is required"""

    password: Secret[str]


@dataclass(frozen=True)
class SecretConfig(ConfigBase):
    """Config with required secrets, so a secret can only come from the file"""

    api_key: Secret[int]
    name: str = "default name"
    db: StrictDbSection = StrictDbSection(password=Secret("x"))


@dataclass(frozen=True)
class DefaultSecretConfig(ConfigBase):
    """Config in which the secrets have defaults"""

    api_key: Secret[int] = Secret(7)
    db: DbSection = DbSection()


@dataclass(frozen=True)
class PlainDefaultConfig(ConfigBase):
    """Config with a default that is not a Secret"""

    api_key: Secret[int] = 5  # type: ignore[assignment]


@dataclass(frozen=True)
class SecretSettings(SettingsBase):
    """Settings must not have secrets"""

    api_key: Secret[int] = Secret(1)


@dataclass(frozen=True)
class SecretSettingsSection(SettingsSectionBase):
    """Settings section with a secret"""

    api_key: Secret[int] = Secret(1)


@dataclass(frozen=True)
class NestedSecretSettings(SettingsBase):
    """Settings with a secret in a section"""

    section: SecretSettingsSection = SecretSettingsSection()


def _write(tmp_path: Path, content: str) -> Path:
    file_path = tmp_path / "config.toml"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def _load(config_class: type[ConfigBase], tmp_path: Path, content: str) -> ConfigBase:
    config_class.set_filepath(_write(tmp_path, content))
    return config_class.load()


def _warnings(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]


def test_exports() -> None:
    assert issubclass(SecretsError, ValueError)
    assert issubclass(ReferenceResolutionError, ValueError)


def test_secret_from_env_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_KEY", "1234")
    config = _load(SecretConfig, tmp_path, 'api_key = "${env:APPSET_KEY}"\n')
    assert isinstance(config, SecretConfig)
    assert config.api_key.get_secret_value() == 1234  # coerced to int
    assert SecretConfig.get().api_key.get_secret_value() == 1234


def test_secret_is_masked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPSET_KEY", "1234")
    config = _load(SecretConfig, tmp_path, 'api_key = "${env:APPSET_KEY}"\n')
    assert isinstance(config, SecretConfig)
    assert "1234" not in repr(config)
    assert "1234" not in str(config.api_key)
    assert "1234" not in repr(config.api_key)


def test_secret_from_file_reference(tmp_path: Path) -> None:
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "key").write_text("42\n")
    config = _load(
        SecretConfig,
        tmp_path,
        'api_key = "${secret:key}"\n[application_config]\nsecrets_dir = "secrets"\n',
    )
    assert isinstance(config, SecretConfig)
    assert config.api_key.get_secret_value() == 42


def test_secret_in_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPSET_KEY", "1")
    monkeypatch.setenv("APPSET_PW", "pw-1234")
    config = _load(
        SecretConfig,
        tmp_path,
        'api_key = "${env:APPSET_KEY}"\n[db]\npassword = "${env:APPSET_PW}"\n',
    )
    assert isinstance(config, SecretConfig)
    assert config.db.password.get_secret_value() == "pw-1234"
    assert "pw-1234" not in repr(config)


def test_required_secret_missing(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="api_key"):
        _load(SecretConfig, tmp_path, 'name = "no key here"\n')


def test_unresolved_secret_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APPSET_UNSET", raising=False)
    with pytest.raises(ReferenceResolutionError, match="api_key"):
        _load(SecretConfig, tmp_path, 'api_key = "${env:APPSET_UNSET}"\n')


def test_secret_from_reference_gives_no_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("APPSET_KEY", "1")
    monkeypatch.setenv("APPSET_PW", "x")
    with caplog.at_level(logging.WARNING):
        _load(
            SecretConfig,
            tmp_path,
            'api_key = "${env:APPSET_KEY}"\n[db]\npassword = "${env:APPSET_PW}"\n',
        )
    assert not any(STORE_WARNING in message for message in _warnings(caplog))


@pytest.mark.parametrize(
    "content, offender",
    [
        ("api_key = 1234\n", "api_key"),  # a literal in the file
        ('api_key = "${env:APPSET_UNSET,1234}"\n', "api_key"),  # an inline default
        ('[db]\npassword = "literal-pw"\n', "db.password"),
    ],
)
def test_secret_not_from_a_store_warns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    content: str,
    offender: str,
) -> None:
    monkeypatch.delenv("APPSET_UNSET", raising=False)
    monkeypatch.setenv("APPSET_OTHER", "1")
    if "api_key" not in content:
        content = 'api_key = "${env:APPSET_OTHER}"\n' + content
    with caplog.at_level(logging.WARNING):
        config = _load(SecretConfig, tmp_path, content)  # still loads
    assert isinstance(config, SecretConfig)
    messages = [m for m in _warnings(caplog) if offender in m and STORE_WARNING in m]
    assert len(messages) == 1
    assert "1234" not in messages[0] and "literal-pw" not in messages[0]


def test_secret_default_in_code_warns(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING):
        config = _load(DefaultSecretConfig, tmp_path, 'api_key = "${env:A,7}"\n')
    assert isinstance(config, DefaultSecretConfig)
    messages = " ".join(_warnings(caplog))
    assert "api_key" in messages  # inline default
    assert "db.password" in messages  # default in the code
    assert HARDCODED not in messages


def test_secret_not_from_a_store_in_strict_mode_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_OTHER", "1")
    good = _load(SecretConfig, tmp_path, 'api_key = "${env:APPSET_OTHER}"\n')
    content = (
        'api_key = 1234\n[db]\npassword = "literal-pw"\n'
        "[application_config]\nstrict_mode = true\n"
    )
    with pytest.raises(SecretsError) as excinfo:
        _load(SecretConfig, tmp_path, content)
    message = str(excinfo.value)
    assert "api_key" in message and "db.password" in message  # all offenders
    assert "1234" not in message and "literal-pw" not in message
    assert SecretConfig.get() is good  # the failed load did not replace the config


def test_secret_from_reference_in_strict_mode_is_fine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_OTHER", "1")
    content = (
        'api_key = "${env:APPSET_OTHER}"\n[db]\npassword = "${env:APPSET_OTHER}"\n'
        "[application_config]\nstrict_mode = true\n"
    )
    config = _load(SecretConfig, tmp_path, content)
    assert isinstance(config, SecretConfig)


def test_default_that_is_not_a_secret_raises(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="api_key"):
        _load(PlainDefaultConfig, tmp_path, "")


@pytest.mark.parametrize("settings_class", [SecretSettings, NestedSecretSettings])
def test_secret_in_settings_raises(
    tmp_path: Path, settings_class: type[SettingsBase]
) -> None:
    file_path = tmp_path / "settings.json"
    file_path.write_text("{}", encoding="utf-8")
    settings_class.set_filepath(file_path)
    with pytest.raises(TypeError, match="Config"):
        settings_class.load()


def test_non_secret_literals_are_not_flagged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("APPSET_OTHER", "1")
    content = (
        'api_key = "${env:APPSET_OTHER}"\nname = "literal name"\n'
        '[db]\npassword = "${env:APPSET_OTHER}"\n'
        "[application_config]\nstrict_mode = true\n"
    )
    with caplog.at_level(logging.WARNING):
        config = _load(SecretConfig, tmp_path, content)
    assert isinstance(config, SecretConfig)
    assert not any(STORE_WARNING in message for message in _warnings(caplog))


# --- secret values must not end up in validation errors ---

REDACTED = "**********"


@dataclass(frozen=True)
class PinSection(ConfigSectionBase):
    """Section with a secret that is coerced"""

    pin: Secret[int]


@dataclass(frozen=True)
class LeakConfig(ConfigBase):
    """Config with a required parameter that is not a secret"""

    needed: str
    api_key: Secret[int]
    pins: PinSection
    name: str = "default name"


@dataclass(frozen=True)
class PlainConfig(ConfigBase):
    """Config without secrets"""

    ratio: float = 1.0


def _full_text(error: BaseException) -> str:
    """Everything that would be shown: the message and the whole traceback chain"""
    return str(error) + "".join(traceback.format_exception(error))


@pytest.mark.parametrize("source", ["env", "literal"])
def test_failed_coercion_does_not_show_the_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str
) -> None:
    monkeypatch.setenv("APPSET_BAD", "not-a-number-s3cret")
    value = '"${env:APPSET_BAD}"' if source == "env" else '"not-a-number-s3cret"'
    content = f'needed = "n"\napi_key = {value}\n[pins]\npin = 1\n'
    with pytest.raises(ValidationError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    assert "s3cret" not in _full_text(excinfo.value)
    assert "api_key" in str(excinfo.value)
    assert "valid integer" in str(excinfo.value)  # what is wrong is still reported
    assert excinfo.value.title == "LeakConfig"
    (error,) = excinfo.value.errors()
    assert error["loc"] == ("api_key",)
    assert error["type"] == "int_parsing"
    assert error["input"] == REDACTED


def test_failed_coercion_in_a_section_does_not_show_the_value(
    tmp_path: Path,
) -> None:
    content = 'needed = "n"\napi_key = 1\n[pins]\npin = "not-a-pin-s3cret"\n'
    with pytest.raises(ValidationError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    assert "s3cret" not in _full_text(excinfo.value)
    (error,) = excinfo.value.errors()
    assert error["loc"] == ("pins", "pin")
    assert error["input"] == REDACTED


def test_error_in_another_parameter_does_not_show_secrets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pydantic reports a missing parameter with all arguments as its input
    monkeypatch.setenv("APPSET_KEY", "987654")
    monkeypatch.setenv("APPSET_PIN", "246810")
    content = 'api_key = "${env:APPSET_KEY}"\n[pins]\npin = "${env:APPSET_PIN}"\n'
    with pytest.raises(ValidationError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    text = _full_text(excinfo.value)
    assert "987654" not in text and "246810" not in text
    assert "needed" in text
    assert [e["loc"] for e in excinfo.value.errors()] == [("needed",)]


def test_all_errors_are_kept(tmp_path: Path) -> None:
    content = (
        'api_key = "bad-s3cret"\n[pins]\npin = "bad-s3cret"\n'  # and needed is missing
    )
    with pytest.raises(ValidationError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    assert excinfo.value.error_count() == 3
    assert "s3cret" not in _full_text(excinfo.value)


def test_input_of_non_secret_parameters_is_still_shown(tmp_path: Path) -> None:
    content = 'needed = "n"\napi_key = 1\nname = 12345\n[pins]\npin = 1\n'
    with pytest.raises(ValidationError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    (error,) = excinfo.value.errors()
    assert error["loc"] == ("name",)
    assert error["input"] == 12345
    assert "12345" in str(excinfo.value)


def test_input_that_is_not_a_plain_value_is_hidden(tmp_path: Path) -> None:
    # a list or table could hold a secret, so only plain values are ever shown
    content = 'needed = "n"\napi_key = 1\nname = [1, 2]\n[pins]\npin = 1\n'
    with pytest.raises(ValidationError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    (error,) = excinfo.value.errors()
    assert error["loc"] == ("name",)
    assert error["input"] == REDACTED


def test_config_without_secrets_is_not_changed(tmp_path: Path) -> None:
    with pytest.raises(ValidationError) as excinfo:
        _load(PlainConfig, tmp_path, 'ratio = "not-a-float"\n')
    assert "not-a-float" in str(excinfo.value)


def test_set_redacts_as_well() -> None:
    # not a literal in the source line, because a traceback shows source lines
    bad_value = "bad-" + "s3" + "cret"
    with pytest.raises(ValidationError) as excinfo:
        LeakConfig.set({"needed": "n", "api_key": bad_value, "pins": {"pin": 1}})
    assert bad_value not in _full_text(excinfo.value)


def test_if_the_error_cannot_be_rebuilt_nothing_is_shown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class CannotRebuild:  # ValidationError is a built-in type: it cannot be patched
        @staticmethod
        def from_exception_data(*args: object, **kwargs: object) -> ValidationError:
            raise TypeError("cannot rebuild")

    monkeypatch.setattr(
        "application_settings._private.secret_checks.ValidationError", CannotRebuild
    )
    content = 'needed = "n"\napi_key = "bad-s3cret"\n[pins]\npin = 1\n'
    with pytest.raises(ValueError) as excinfo:
        _load(LeakConfig, tmp_path, content)
    text = _full_text(excinfo.value)
    assert "s3cret" not in text
    assert "api_key" in text


@dataclass(frozen=True)
class ModeConfig(ConfigBase):
    """Config with a secret that can only have a few values"""

    mode: Secret[Literal["a", "b"]]


def test_errors_with_context_are_kept(tmp_path: Path) -> None:
    # a literal error has context (the expected values); that is kept, the input is not
    content = 'mode = "zzz-s3cret"\n'
    with pytest.raises(ValidationError) as excinfo:
        _load(ModeConfig, tmp_path, content)
    assert "s3cret" not in _full_text(excinfo.value)
    assert "'a' or 'b'" in str(excinfo.value)
    (error,) = excinfo.value.errors()
    assert error["type"] == "literal_error"
    assert error["input"] == REDACTED
