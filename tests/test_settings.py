# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=consider-alternative-union-syntax
import sys
from pathlib import Path

import pytest
from pydantic.dataclasses import dataclass

from application_settings import (
    SettingsBase,
    SettingsSectionBase,
    settings_filepath_from_commandline_option,
)

if sys.version_info < (3, 10):
    from typing import Union


@dataclass(frozen=True)
class AnExample1SettingsSubSection(SettingsSectionBase):
    """Example 1 of a Settings section"""

    setting3: float = 3.3


@dataclass(frozen=True)
class AnExample1SettingsSection(SettingsSectionBase):
    """Example 1 of a Settings section"""

    setting1: str = "setting1"
    setting2: int = 2
    subsec: AnExample1SettingsSubSection = AnExample1SettingsSubSection()


@dataclass(frozen=True)
class AnExample1Settings(SettingsBase):
    """Example Settings"""

    section1: AnExample1SettingsSection = AnExample1SettingsSection()


def test_kind_string() -> None:
    assert AnExample1SettingsSection.kind_string() == "Settings"


def test_paths() -> None:
    # default_filepath:
    if the_path := AnExample1Settings.default_filepath():
        assert the_path.parts[-1] == "settings.json"
        assert the_path.parts[-2] == ".an_example1"
    else:
        assert False


def test_settings_cmdline(monkeypatch: pytest.MonkeyPatch) -> None:
    some_path = Path.home() / "ProgramData" / "test" / "config.toml"
    monkeypatch.setattr(sys, "argv", ["bla", "-g", str(some_path)])
    settings_filepath_from_commandline_option(AnExample1Settings, short_option="-g")
    assert str(AnExample1Settings.filepath()) == str(some_path)


def test_update(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if sys.version_info >= (3, 10):

        def mock_default_filepath() -> Path | None:
            return None

    else:

        def mock_default_filepath() -> Union[Path, None]:
            return None

    monkeypatch.setattr(AnExample1Settings, "default_filepath", mock_default_filepath)
    AnExample1Settings.set_filepath("")
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.setting1 == "setting1"
    assert AnExample1Settings.get().section1.setting2 == 2
    with pytest.raises(RuntimeError):
        # no path specified and attempting to save, that will raise a runtime error
        new_settings = AnExample1Settings.update(
            {"section1": {"setting1": "new s1", "setting2": 222}}
        )
    tmp_filepath = (
        tmp_path
        / AnExample1Settings.default_foldername()
        / AnExample1Settings.default_filename()
    )
    AnExample1Settings.set_filepath(tmp_filepath)
    new_settings = AnExample1Settings.update(
        {"section1": {"setting1": "new s1", "setting2": 222}}
    )

    assert new_settings.section1.setting1 == "new s1"
    assert AnExample1Settings.get().section1.setting2 == 222


def test_update_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if sys.version_info >= (3, 10):

        def mock_default_filepath() -> Path | None:
            return None

    else:

        def mock_default_filepath() -> Union[Path, None]:
            return None

    monkeypatch.setattr(AnExample1Settings, "default_filepath", mock_default_filepath)
    AnExample1Settings.set_filepath("")
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.setting1 == "setting1"
    assert AnExample1Settings.get().section1.setting2 == 2
    tmp_filepath = (
        tmp_path
        / AnExample1Settings.default_foldername()
        / AnExample1Settings.default_filename()
    )
    AnExample1Settings.set_filepath(tmp_filepath)
    new_settings = AnExample1Settings.update(
        {"section1": {"setting1": "new s1a", "setting2": 333}}
    )

    assert new_settings.section1.setting1 == "new s1a"
    assert AnExample1Settings.get().section1.setting2 == 333
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.setting1 == "new s1a"
    assert AnExample1Settings.get().section1.setting2 == 333


def test_update_toml(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if sys.version_info >= (3, 10):

        def mock_default_filepath() -> Path | None:
            return None

    else:

        def mock_default_filepath() -> Union[Path, None]:
            return None

    monkeypatch.setattr(AnExample1Settings, "default_filepath", mock_default_filepath)
    AnExample1Settings.set_filepath("")
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.setting1 == "setting1"
    assert AnExample1Settings.get().section1.setting2 == 2
    tmp_filepath = (
        tmp_path
        / AnExample1Settings.default_foldername()
        / AnExample1Settings.default_filename().replace("json", "toml")
    )
    AnExample1Settings.set_filepath(tmp_filepath)
    new_settings = AnExample1Settings.update(
        {"section1": {"subsec": {"setting3": 4.44, "extra thing": True}}}
    )

    assert new_settings.section1.subsec.setting3 == 4.44
    assert AnExample1Settings.get().section1.subsec.setting3 == 4.44
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.subsec.setting3 == 4.44
    assert AnExample1Settings.get().section1.subsec.setting3 == 4.44


def test_update_ini(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    if sys.version_info >= (3, 10):

        def mock_default_filepath() -> Path | None:
            return None

    else:

        def mock_default_filepath() -> Union[Path, None]:
            return None

    monkeypatch.setattr(AnExample1Settings, "default_filepath", mock_default_filepath)
    AnExample1Settings.set_filepath("")
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.setting1 == "setting1"
    assert AnExample1Settings.get().section1.setting2 == 2
    tmp_filepath = (
        tmp_path
        / AnExample1Settings.default_foldername()
        / AnExample1Settings.default_filename().replace("json", "ini")
    )
    AnExample1Settings.set_filepath(tmp_filepath)
    new_settings = AnExample1Settings.update(
        {"section1": {"setting1": "new s1a", "setting2": 333}}
    )

    # new settings have been applied but not stored to file
    assert new_settings.section1.setting1 == "new s1a"
    assert AnExample1Settings.get().section1.setting2 == 333
    captured = capfd.readouterr()
    assert "Unknown file format ini given in" in captured.out
    AnExample1Settings.load()
    assert AnExample1Settings.get().section1.setting1 == "setting1"
    assert AnExample1Settings.get().section1.setting2 == 2
