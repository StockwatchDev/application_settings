# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from application_config import ConfigBase, ConfigSectionBase, __version__

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass(frozen=True)
class AnExample1ConfigSection(ConfigSectionBase):
    """Example 1 of a Config section"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class AnExample1Config(ConfigBase):
    """Example Config"""

    section1: AnExample1ConfigSection = AnExample1ConfigSection()

def test_version() -> None:
    assert __version__ == "0.1.0"

def test_defaults(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    def mock_default_config_filepath() -> Path | None:
        return None

    the_path = AnExample1Config.default_config_filepath()
    if the_path:
        assert the_path.parts[-1] == "config.toml"
        assert the_path.parts[-2] == ".an_example1"
    assert AnExample1Config.get().section1.field1 == "field1"
    assert AnExample1Config.get().section1.field2 == 2
    captured = capfd.readouterr()
    assert "not found; trying with defaults, but this may not work." in captured.out

    monkeypatch.setattr(
        AnExample1Config, "default_config_filepath", mock_default_config_filepath
    )


@pytest.fixture
def test_config(monkeypatch: pytest.MonkeyPatch) -> DummyConfig:
    # here do monkeypatching of get_app_basename and _get_stored_config
    assert AnExample1Config.get(reload=True).section1.field1 == "field1"
    captured = capfd.readouterr()
    assert "No path specified for configfile" in captured.out

    with pytest.raises(ValueError):
        _ = AnExample1Config.get(
            reload=True, configfile_path='fi:\0\\l*e/p"a?t>h|.t<xt'
        ).section1.field1


def test_get(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_default_config_filepath() -> Path | None:
        return Path(__file__)

    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {"section1": {"field1": "f1", "field2": 22}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    assert (
        AnExample1Config.get(
            reload=True, configfile_path=str(Path(__file__))
        ).section1.field1
        == "f1"
    )

    assert (
        AnExample1Config.get(
            reload=True, configfile_path=Path(__file__)
        ).section1.field2
        == 22
    )

    monkeypatch.setattr(
        AnExample1Config, "default_config_filepath", mock_default_config_filepath
    )

    assert AnExample1Config.get(reload=True).section1.field2 == 22


def test_type_coercion(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {"section1": {"field1": True, "field2": "22"}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    test_config = AnExample1Config.get(reload=True, configfile_path=str(Path(__file__)))
    assert isinstance(test_config.section1.field1, str)
    assert test_config.section1.field1 == "True"
    assert isinstance(test_config.section1.field2, int)
    assert test_config.section1.field2 == 22


def test_wrong_type(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, tuple[str, int] | None]]:
        return {"section1": {"field1": ("f1", 22), "field2": None}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    with pytest.raises(ValidationError) as excinfo:
        _ = AnExample1Config.get(reload=True, configfile_path=str(Path(__file__)))
    assert "2 validation errors" in str(excinfo.value)
    assert "str type expected" in str(excinfo.value)
    assert "none is not an allowed value" in str(excinfo.value)


def test_get_defaults() -> None:
    assert AnExample1Config.get(reload=True).section1.field2 == 2


def test_missing_extra_attributes(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {"section1": {"field1": "f1", "field3": 22}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    test_config = AnExample1Config.get(reload=True, configfile_path=str(Path(__file__)))
    assert test_config.section1.field2 == 2
    with pytest.raises(AttributeError):
        assert test_config.section1.field3 == 22  # type: ignore[attr-defined]


@dataclass(frozen=True)
class Example2aConfigSection(ConfigSectionBase):
    """Example 2a of a Config section"""

    field3: float
    field4: float = 0.5


@dataclass(frozen=True)
class Example2bConfigSection(ConfigSectionBase):
    """Example 2b of a Config section"""

    field1: str = "field1"
    field2: int = 2


@dataclass(frozen=True)
class Example2Config(ConfigBase):
    """Example Config"""

    section1: Example2aConfigSection
    section2: Example2bConfigSection = Example2bConfigSection()


def test_attributes_no_default(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_tomllib_load1(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {"section2": {"field1": "f1", "field2": 22}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load1)

    with pytest.raises(TypeError):
        _ = Example2Config.get(reload=True, configfile_path=str(Path(__file__)))

    def mock_tomllib_load2(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, float]]:
        return {"section1": {"field3": 1.1}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load2)

    test_config = Example2Config.get(reload=True, configfile_path=str(Path(__file__)))
    assert test_config.section1.field3 == 1.1
    assert test_config.section1.field4 == 0.5
    assert test_config.section2.field1 == "field1"
