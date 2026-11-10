# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import json
import os
from pathlib import Path

import pytest

from application_settings import (
    ApplicationConfigSection,
    ConfigBase,
    ConfigSectionBase,
    SettingsBase,
    ValidationError,
    dataclass,
)
from application_settings._private.references import ReferenceResolutionError


@dataclass(frozen=True)
class RefSection(ConfigSectionBase):
    """Section of an example config"""

    port: int = 80
    label: str = "section"


@dataclass(frozen=True)
class RefConfig(ConfigBase):
    """Example config that is used to test references"""

    name: str = "default name"
    ratio: float = 0.5
    section: RefSection = RefSection()


@dataclass(frozen=True)
class RefSettings(SettingsBase):
    """Example settings, in which references must not be resolved"""

    name: str = "default name"


def _load(tmp_path: Path, content: str) -> RefConfig:
    file_path = tmp_path / "config.toml"
    file_path.write_text(content, encoding="utf-8")
    RefConfig.set_filepath(file_path)
    return RefConfig.load()


def test_application_config_section_defaults() -> None:
    section = ApplicationConfigSection()
    assert section.dotenv_file == ""
    assert section.secrets_dir == ""


def test_env_reference(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPSET_NAME", "from environment")
    config = _load(tmp_path, 'name = "${env:APPSET_NAME}"\n')
    assert config.name == "from environment"
    assert RefConfig.get().name == "from environment"


def test_reference_is_coerced_to_the_field_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_RATIO", "0.25")
    monkeypatch.setenv("APPSET_PORT", "8080")
    config = _load(
        tmp_path,
        'ratio = "${env:APPSET_RATIO}"\n[section]\nport = "${env:APPSET_PORT}"\n',
    )
    assert config.ratio == 0.25
    assert config.section.port == 8080
    assert RefSection.get().port == 8080


def test_reference_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPSET_UNSET", raising=False)
    config = _load(tmp_path, 'ratio = "${env:APPSET_UNSET,7.5}"\n')
    assert config.ratio == 7.5


def test_unresolved_reference_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APPSET_UNSET", raising=False)
    with pytest.raises(ReferenceResolutionError, match="APPSET_UNSET"):
        _load(tmp_path, 'name = "${env:APPSET_UNSET}"\n')


def test_escaped_reference_is_a_literal(tmp_path: Path) -> None:
    config = _load(tmp_path, 'name = "$${env:APPSET_NAME}"\n')
    assert config.name == "${env:APPSET_NAME}"


def test_dotenv_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPSET_FROM_DOTENV", raising=False)
    (tmp_path / "my.env").write_text("APPSET_FROM_DOTENV=dotenv value\n")
    config = _load(
        tmp_path,
        'name = "${env:APPSET_FROM_DOTENV}"\n'
        '[application_config]\ndotenv_file = "my.env"\n',
    )
    assert config.name == "dotenv value"
    assert "APPSET_FROM_DOTENV" not in os.environ


def test_real_environment_wins_over_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_BOTH", "real")
    (tmp_path / "my.env").write_text("APPSET_BOTH=dotenv\n")
    config = _load(
        tmp_path,
        'name = "${env:APPSET_BOTH}"\n[application_config]\ndotenv_file = "my.env"\n',
    )
    assert config.name == "real"


def test_secrets_dir(tmp_path: Path) -> None:
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "the_name").write_text("secret name\n")
    config = _load(
        tmp_path,
        'name = "${file:the_name}"\n[application_config]\nsecrets_dir = "secrets"\n',
    )
    assert config.name == "secret name"


def test_file_reference_without_secrets_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(ReferenceResolutionError, match="secrets_dir"):
        _load(tmp_path, 'name = "${file:the_name}"\n')


def test_file_reference_default_without_secrets_dir(tmp_path: Path) -> None:
    config = _load(tmp_path, 'name = "${file:the_name,fallback}"\n')
    assert config.name == "fallback"


def test_application_config_section_is_not_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_WHERE", "elsewhere.env")
    config = _load(
        tmp_path, '[application_config]\ndotenv_file = "${env:APPSET_WHERE}"\n'
    )
    assert config.application_config.dotenv_file == "${env:APPSET_WHERE}"


def test_references_in_included_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_PORT", "81")
    (tmp_path / "included.toml").write_text('[section]\nport = "${env:APPSET_PORT}"\n')
    config = _load(tmp_path, 'name = "main"\n__include__ = "./included.toml"\n')
    assert config.name == "main"
    assert config.section.port == 81


def test_config_without_references_is_unchanged(tmp_path: Path) -> None:
    config = _load(tmp_path, 'name = "plain"\nratio = 2.5\n[section]\nport = 5\n')
    assert (config.name, config.ratio, config.section.port) == ("plain", 2.5, 5)


def test_settings_are_not_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPSET_NAME", "from environment")
    file_path = tmp_path / "settings.json"
    file_path.write_text(json.dumps({"name": "${env:APPSET_NAME}"}), encoding="utf-8")
    RefSettings.set_filepath(file_path)
    assert RefSettings.load().name == "${env:APPSET_NAME}"


def test_wrongly_typed_application_config_is_a_validation_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValidationError, match="dotenv_file"):
        _load(tmp_path, "[application_config]\ndotenv_file = 5\n")
