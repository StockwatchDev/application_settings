# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from pathlib import Path

import pytest
from pydantic.dataclasses import dataclass

from application_settings import SettingsBase, SettingsSectionBase


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
    if the_path := AnExample1Settings.default_filepath():
        assert the_path.parts[-1] == "settings.toml"
        assert the_path.parts[-2] == ".an_example1"
    else:
        assert False


def test_update(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def mock_default_filepath() -> Path | None:
        return None

    monkeypatch.setattr(AnExample1Settings, "default_filepath", mock_default_filepath)
    AnExample1Settings.set_filepath("")
    assert AnExample1Settings.get(reload=True).section1.setting1 == "setting1"
    assert AnExample1Settings.get().section1.setting2 == 2
    with pytest.raises(RuntimeError):
        new_settings = AnExample1Settings.get().update(
            {"section1": {"setting1": "new s1", "setting2": 222}}
        )
    tmp_filepath = (
        tmp_path
        / AnExample1Settings.default_foldername()
        / AnExample1Settings.default_filename()
    )
    AnExample1Settings.set_filepath(tmp_filepath)
    new_settings = AnExample1Settings.get().update(
        {"section1": {"setting1": "new s1", "setting2": 222}}
    )

    assert new_settings.section1.setting1 == "new s1"
    assert AnExample1Settings.get().section1.setting2 == 222
