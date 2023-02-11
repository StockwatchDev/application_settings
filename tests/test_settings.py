# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import sys
from pathlib import Path
from typing import Any

import pytest
from pydantic.dataclasses import dataclass

from application_config import SettingsBase, SettingsSectionBase

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass(frozen=True)
class AnExample1SettingsSection(SettingsSectionBase):
    """Example 1 of a Settings section"""

    setting1: str = "setting1"
    setting2: int = 2


@dataclass(frozen=True)
class AnExample1Settings(SettingsBase):
    """Example Settings"""

    section1: AnExample1SettingsSection = AnExample1SettingsSection()


def test_paths() -> None:
    # default_filepath:
    the_path = AnExample1Settings.default_filepath()
    if the_path:
        assert the_path.parts[-1] == "settings.toml"
        assert the_path.parts[-2] == ".an_example1"
    else:
        assert False


def test_update(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str | int]]:
        return {"section1": {"setting1": "s1", "setting2": 22}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    AnExample1Settings.set_filepath(Path(__file__))
    assert AnExample1Settings.get(reload=True).section1.setting1 == "s1"
    assert AnExample1Settings.get().section1.setting2 == 22

    new_settings = AnExample1Settings.get().update(
        {"section1": {"setting1": "new s1", "setting2": 222}}
    )
    assert new_settings.section1.setting1 == "new s1"
    assert AnExample1Settings.get().section1.setting2 == 222
