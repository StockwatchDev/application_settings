# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import sys
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from application_config import ConfigBase, ConfigSectionBase

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass(frozen=True)
class DummyConfigSection(ConfigSectionBase):
    """Config section for testing"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class DummyConfig(ConfigBase):
    """Config for testing"""

    section1: DummyConfigSection = DummyConfigSection()

    @staticmethod
    def get_app_basename() -> str:
        """Return the string that describes the application base name"""
        return "dummyconfig"


@pytest.fixture
def test_config(monkeypatch: pytest.MonkeyPatch) -> DummyConfig:
    # here do monkeypatching of get_app_basename and _get_stored_config

    def mock_get_configfile_path() -> Path:
        return Path(__file__)

    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {
            "section1": {
                "field1": "f1",
                "field2": 22,
            }
        }

    monkeypatch.setattr(DummyConfig, "get_configfile_path", mock_get_configfile_path)
    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    return DummyConfig.get()


@pytest.fixture
def test_config2(monkeypatch: pytest.MonkeyPatch) -> DummyConfig:
    # here do monkeypatching of get_app_basename and _get_stored_config

    def mock_get_configfile_path() -> Path:
        return Path(__file__)

    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {
            "section1": {
                "field1": True,
                "field2": "22",
            }
        }

    monkeypatch.setattr(DummyConfig, "get_configfile_path", mock_get_configfile_path)
    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    return DummyConfig.get(reload=True)


@pytest.fixture
def test_config3(monkeypatch: pytest.MonkeyPatch) -> DummyConfig:
    # here do monkeypatching of get_app_basename and _get_stored_config

    def mock_get_configfile_path() -> Path:
        return Path(__file__)

    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, tuple[str, int] | int]]:
        return {
            "section1": {
                "field1": ("f1", 22),
                "field2": 22,
            }
        }

    monkeypatch.setattr(DummyConfig, "get_configfile_path", mock_get_configfile_path)
    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    return DummyConfig.get(reload=True)


def test_get_config_path() -> None:
    assert DummyConfig.get_configfile_path().parts[-1] == "config.toml"
    assert DummyConfig.get_configfile_path().parts[-2] == ".dummyconfig"


def test_get(test_config: DummyConfig) -> None:
    assert test_config.section1.field1 == "f1"
    assert DummyConfig.get().section1.field2 == 22


def test_type_coercion(test_config2: DummyConfig) -> None:
    assert isinstance(test_config2.section1.field1, str)
    assert test_config2.section1.field1 == "True"
    assert isinstance(test_config2.section1.field2, int)
    assert test_config2.section1.field2 == 22


def test_wrong_type(monkeypatch: pytest.MonkeyPatch) -> None:

    # here do monkeypatching of get_app_basename and _get_stored_config

    def mock_get_configfile_path() -> Path:
        return Path(__file__)

    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, tuple[str, int] | None]]:
        return {
            "section1": {
                "field1": ("f1", 22),
                "field2": None,
            }
        }

    monkeypatch.setattr(DummyConfig, "get_configfile_path", mock_get_configfile_path)
    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    with pytest.raises(ValidationError) as excinfo:
        _ = DummyConfig.get(reload=True)
    # assert len(e.) == 2
    assert "2 validation errors" in str(excinfo.value)
    assert "str type expected" in str(excinfo.value)
    assert "none is not an allowed value" in str(excinfo.value)


def test_get_defaults() -> None:
    assert DummyConfig.get(reload=True).section1.field2 == 2
