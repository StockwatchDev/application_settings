# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import tomli_w

from application_settings import (
    ConfigBase,
    ConfigSectionBase,
    PathOpt,
    ValidationError,
    __version__,
    config_filepath_from_cli,
    dataclass,
)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass(frozen=True)
class AnExampleConfigSubSection(ConfigSectionBase):
    """Example of a Config subsection"""

    field3: tuple[int, str] = (3, "yes")


@dataclass(frozen=True)
class AnExample1ConfigSection(ConfigSectionBase):
    """Example 1 of a Config section"""

    field1: str = "field1"
    field2: int = 2
    subsec: AnExampleConfigSubSection = AnExampleConfigSubSection()


@dataclass(frozen=True)
class AnExample1Config(ConfigBase):
    """Example Config"""

    field0: float = 2.2
    section1: AnExample1ConfigSection = AnExample1ConfigSection()


@dataclass(frozen=True)
class Config(ConfigBase):
    """Config class def"""


class ConfigNoDataclass(ConfigBase):
    """Config class def, without dataclass decorator"""


@dataclass
class ConfigUnfrozenDataclass(ConfigBase):
    """Config class def, without dataclass decorator"""


@pytest.fixture(scope="session")
def toml_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    file_path = (
        tmp_path_factory.mktemp(AnExample1Config.default_foldername())
        / AnExample1Config.default_filename()
    )
    with file_path.open(mode="wb") as fptr:
        tomli_w.dump(
            {
                "field0": 33.33,
                "section1": {
                    "field1": "f1",
                    "field2": 22,
                    "subsec": {"field3": (-3, "no")},
                },
            },
            fptr,
        )
    return file_path


@pytest.fixture(scope="session")
def json_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    file_path = tmp_path_factory.mktemp(
        AnExample1Config.default_foldername()
    ) / AnExample1Config.default_filename().replace("toml", "json")
    with file_path.open(mode="w") as fptr:
        json.dump(
            {
                "section1": {
                    "field1": "f2",
                    "field2": 33,
                    "subsec": {"field3": (-4, "maybe")},
                }
            },
            fptr,
        )
    return file_path


@pytest.fixture(scope="session")
def ini_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    file_path = tmp_path_factory.mktemp(
        AnExample1Config.default_foldername()
    ) / AnExample1Config.default_filename().replace("toml", "ini")
    with file_path.open(mode="w") as fptr:
        fptr.write("inifile")
    return file_path


def test_kind_string() -> None:
    assert AnExample1ConfigSection.kind_string() == "Config"


def test_section_singleton(capfd: pytest.CaptureFixture[str]) -> None:
    assert AnExample1ConfigSection.get().field1 == "field1"
    captured = capfd.readouterr()
    assert " accessed before data has been set by the application." in captured.out


def test_paths(toml_file: Path) -> None:
    # default_filepath:
    if the_path := Config.default_filepath():
        assert the_path.parts[-2] == ".config"
    else:
        assert False

    if the_path := AnExample1Config.default_filepath():
        assert the_path.parts[-1] == "config.toml"
        assert the_path.parts[-2] == ".an_example1"
    else:
        assert False

    # filepath:
    # if not set, then equal to default_filepath
    assert AnExample1Config.filepath() == the_path
    # check set_filepath with a Path
    AnExample1Config.set_filepath(toml_file)
    assert AnExample1Config.filepath() == toml_file
    # check set_filepath with a str
    AnExample1Config.set_filepath(".")
    assert AnExample1Config.filepath() == Path.cwd()

    # reset to default:
    AnExample1Config.set_filepath("")
    assert AnExample1Config.filepath() == the_path

    # raising of FileNotFoundError:
    with pytest.raises(FileNotFoundError):
        AnExample1Config.load(throw_if_file_not_found=True)

    AnExample1Config.set_filepath(
        str(Path.home() / "ProgramData" / "test" / "config.toml")
    )
    # raising in case of invalid path:
    with pytest.raises(ValueError):
        AnExample1Config.set_filepath('fi:\0\\l*e/p"a?t>h|.t<xt')


def test_decorator() -> None:
    # raising of TypeError:
    with pytest.raises(TypeError):
        ConfigNoDataclass.load()
    with pytest.raises(TypeError):
        ConfigUnfrozenDataclass.load()


def test_config_cmdline(monkeypatch: pytest.MonkeyPatch) -> None:
    # test without commandline arguments
    # - this works, but not together with the last 4 lines
    # monkeypatch.setattr(sys, "argv", ["bla"])
    # config_filepath_from_cli(Config, short_option="-k")
    # assert Config.filepath() == Config.default_filepath()
    some_path = Path.home() / "ProgramData" / "test" / "config.toml"
    monkeypatch.setattr(sys, "argv", ["bla", "-k", str(some_path)])
    config_filepath_from_cli(AnExample1Config, short_option="-k")
    assert str(AnExample1Config.filepath()) == str(some_path)


def test_get_defaults(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    def mock_default_filepath() -> PathOpt:
        return None

    monkeypatch.setattr(AnExample1Config, "default_filepath", mock_default_filepath)
    AnExample1Config.set_filepath("", load=True)
    assert AnExample1Config.get().section1.field1 == "field1"
    AnExample1Config.set_filepath("", load=True)
    assert AnExample1Config.get().section1.field2 == 2
    assert AnExample1Config.get().section1.subsec.field3[1] == "yes"
    captured = capfd.readouterr()
    assert (
        "Path None not valid for config file. Trying with defaults, but this may not work."
        in captured.out
    )
    # raising of FileNotFoundError:
    with pytest.raises(FileNotFoundError):
        AnExample1Config.load(throw_if_file_not_found=True)


def test_set_filepath_after_get(
    toml_file: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    AnExample1Config.set_filepath(toml_file, load=True)
    assert AnExample1Config.get().section1.field1 == "f1"
    assert AnExample1Config.get().section1.subsec.field3[1] == "no"
    # test if the subsection singleton is properly registered
    assert AnExampleConfigSubSection.get().field3[1] == "no"
    AnExample1Config.set_filepath("", load=False)
    captured = capfd.readouterr()
    assert "file is not loaded into the Config." in captured.out


def test_get(monkeypatch: pytest.MonkeyPatch, toml_file: Path) -> None:
    AnExample1Config.set_filepath(toml_file)
    AnExample1Config.load()
    assert AnExample1Config.get().field0 == 33.33
    assert AnExample1Config.get().section1.field1 == "f1"
    assert AnExample1Config.get().section1.field2 == 22

    # test that by default it is not reloaded
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, Any]]:
        return {"section1": {"field1": "f1", "field2": 222}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    assert AnExample1Config.get().section1.field2 == 22

    # and now test reload
    AnExample1Config.load()
    assert AnExample1Config.get().field0 == 2.2
    assert AnExample1Config.get().section1.field2 == 222


def test_get_json(json_file: Path) -> None:
    AnExample1Config.set_filepath(json_file)
    AnExample1Config.load()
    assert AnExample1Config.get().section1.field1 == "f2"
    assert AnExample1Config.get().section1.field2 == 33


def test_get_ini(ini_file: Path, capfd: pytest.CaptureFixture[str]) -> None:
    AnExample1Config.set_filepath(ini_file)
    AnExample1Config.load()
    assert AnExample1Config.get().section1.field1 == "field1"
    assert AnExample1Config.get().section1.field2 == 2
    captured = capfd.readouterr()
    assert "Unknown file format ini given in" in captured.out


def test_type_coercion(monkeypatch: pytest.MonkeyPatch, toml_file: Path) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, Any]]:
        return {"section1": {"field1": True, "field2": "22"}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    AnExample1Config.set_filepath(toml_file)
    AnExample1Config.load()
    test_config = AnExample1Config.get()
    assert isinstance(test_config.section1.field1, str)
    assert test_config.section1.field1 == "True"
    assert isinstance(test_config.section1.field2, int)
    assert test_config.section1.field2 == 22


def test_wrong_type(monkeypatch: pytest.MonkeyPatch, toml_file: Path) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, Any]]:
        return {"section1": {"field1": ("f1", 22), "field2": None}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    AnExample1Config.set_filepath(toml_file)
    with pytest.raises(ValidationError) as excinfo:
        AnExample1Config.load()
        _ = AnExample1Config.get()
    assert "2 validation errors" in str(excinfo.value)
    assert "str type expected" in str(excinfo.value)
    assert "none is not an allowed value" in str(excinfo.value)


def test_missing_extra_attributes(
    monkeypatch: pytest.MonkeyPatch, toml_file: Path
) -> None:
    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, Any]]:
        return {"section1": {"field1": "f1", "field3": 22}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)

    AnExample1Config.set_filepath(toml_file)
    AnExample1Config.load()
    test_config = AnExample1Config.get()
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


def test_attributes_no_default(
    monkeypatch: pytest.MonkeyPatch, toml_file: Path
) -> None:
    Example2Config.set_filepath(toml_file)
    with pytest.raises(ValidationError):
        AnExample1Config.load()
        _ = Example2Config.get()

    def mock_tomllib_load2(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, float]]:
        return {"section1": {"field3": 1.1}}

    monkeypatch.setattr(tomllib, "load", mock_tomllib_load2)

    AnExample1Config.load()
    test_config = Example2Config.get()
    assert test_config.section1.field3 == 1.1
    assert test_config.section1.field4 == 0.5
    assert test_config.section2.field1 == "field1"


def test_update() -> None:
    with pytest.raises(TypeError):
        # a Config cannot be updated
        _ = AnExample1Config.get().update(
            {"section1": {"setting1": "new s1", "setting2": 222}}
        )
