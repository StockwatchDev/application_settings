# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from dataclasses import dataclass
import pytest
from pathlib import Path
from application_config import (
    ConfigBase,
    ConfigSectionBase,
)
import sys
from typing import Any

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


def test_get_config_path() -> None:
    assert DummyConfig.get_configfile_path().parts[-1] == "config.toml"
    assert DummyConfig.get_configfile_path().parts[-2] == ".dummyconfig"


def test_get(test_config: DummyConfig) -> None:
    assert test_config.section1.field1 == "f1"
    assert DummyConfig.get().section1.field2 == 22


def test_get_defaults() -> None:
    assert DummyConfig.get(reload=True).section1.field2 == 2
