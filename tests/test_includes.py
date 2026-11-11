# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import json
import logging
from pathlib import Path

import pytest

from application_settings import ConfigBase, dataclass
from application_settings._private.file_operations import load
from application_settings.parameter_kind import ParameterKind


@dataclass(frozen=True)
class IncludeConfig(ConfigBase):
    """Example config that is used to test includes"""

    name: str = "default name"
    ratio: float = 0.5
    port: int = 80


def _write(folder: Path, name: str, content: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / name
    file_path.write_text(content, encoding="utf-8")
    return file_path


def _load(path: Path, throw: bool = False) -> dict[str, object]:
    return load(ParameterKind.CONFIG, path, throw)


# --- what works today, so that later changes do not break it silently ---


def test_included_values_are_added(tmp_path: Path) -> None:
    _write(tmp_path, "common.toml", "ratio = 2.5\nport = 8080\n")
    main = _write(tmp_path, "main.toml", 'name = "main"\n__include__ = "common.toml"\n')
    data = _load(main)
    assert (data["name"], data["ratio"], data["port"]) == ("main", 2.5, 8080)


def test_the_including_file_wins_on_conflict(tmp_path: Path) -> None:
    _write(tmp_path, "common.toml", 'name = "common"\nratio = 2.5\n')
    main = _write(tmp_path, "main.toml", 'name = "main"\n__include__ = "common.toml"\n')
    data = _load(main)
    assert (data["name"], data["ratio"]) == ("main", 2.5)


def test_include_path_is_relative_to_the_including_file(tmp_path: Path) -> None:
    _write(tmp_path / "sub", "common.toml", "port = 1\n")
    main = _write(tmp_path, "main.toml", '__include__ = "sub/common.toml"\n')
    assert _load(main)["port"] == 1


def test_include_path_with_parent_folder(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    _write(tmp_path, "common.toml", "port = 6\n")
    main = _write(tmp_path, "main.toml", '__include__ = "sub/../common.toml"\n')
    assert _load(main)["port"] == 6


def test_include_path_is_normalised(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (tmp_path / "sub").mkdir()
    main = _write(tmp_path, "main.toml", '__include__ = "sub/../nope.toml"\n')
    with caplog.at_level(logging.WARNING):
        _load(main)
    messages = [r.getMessage() for r in caplog.records if "nope.toml" in r.getMessage()]
    assert messages
    assert not any(".." in message for message in messages)


def test_absolute_include_path(tmp_path: Path) -> None:
    common = _write(tmp_path / "elsewhere", "common.toml", "port = 2\n")
    main = _write(
        tmp_path / "here", "main.toml", f"__include__ = '{common.as_posix()}'\n"
    )
    assert _load(main)["port"] == 2


def test_nested_includes(tmp_path: Path) -> None:
    _write(tmp_path, "c.toml", "port = 3\nratio = 1.5\n")
    _write(tmp_path, "b.toml", 'ratio = 2.5\n__include__ = "c.toml"\n')
    main = _write(tmp_path, "main.toml", '__include__ = "b.toml"\n')
    data = _load(main)
    assert (data["port"], data["ratio"]) == (3, 2.5)  # the including file wins


def test_last_listed_include_wins_over_earlier_ones(tmp_path: Path) -> None:
    _write(tmp_path, "first.toml", "port = 1\n")
    _write(tmp_path, "second.toml", "port = 2\nratio = 2.5\n")
    main = _write(
        tmp_path, "main.toml", '__include__ = ["first.toml", "second.toml"]\n'
    )
    data = _load(main)
    assert (data["port"], data["ratio"]) == (2, 2.5)


def test_including_file_wins_over_all_includes(tmp_path: Path) -> None:
    _write(tmp_path, "first.toml", "port = 1\nratio = 1.5\n")
    _write(tmp_path, "second.toml", "port = 2\nratio = 2.5\n")
    main = _write(
        tmp_path, "main.toml", 'port = 9\n__include__ = ["first.toml", "second.toml"]\n'
    )
    data = _load(main)
    assert (data["port"], data["ratio"]) == (9, 2.5)


def test_three_includes_are_applied_in_the_listed_order(tmp_path: Path) -> None:
    for number in (1, 2, 3):
        _write(tmp_path, f"inc{number}.toml", f"port = {number}\nn{number} = 1\n")
    main = _write(
        tmp_path, "main.toml", '__include__ = ["inc2.toml", "inc3.toml", "inc1.toml"]\n'
    )
    data = _load(main)
    assert data["port"] == 1  # listed last
    assert (data["n1"], data["n2"], data["n3"]) == (1, 1, 1)


def test_tables_are_merged_per_key(tmp_path: Path) -> None:
    _write(tmp_path, "common.toml", '[section]\nport = 2\nlabel = "common"\n')
    main = _write(
        tmp_path, "main.toml", '__include__ = "common.toml"\n[section]\nport = 1\n'
    )
    assert _load(main)["section"] == {"port": 1, "label": "common"}


def test_tables_of_several_includes_are_merged(tmp_path: Path) -> None:
    _write(tmp_path, "a.toml", "[section]\nport = 1\nlabel = 'a'\n")
    _write(tmp_path, "b.toml", "[section]\nport = 2\nratio = 2.5\n")
    main = _write(tmp_path, "main.toml", '__include__ = ["a.toml", "b.toml"]\n')
    assert _load(main)["section"] == {"port": 2, "label": "a", "ratio": 2.5}


def test_tables_are_merged_through_nested_includes(tmp_path: Path) -> None:
    _write(tmp_path, "c.toml", "[section]\nx = 0\ny = 2\n")
    _write(tmp_path, "b.toml", '__include__ = "c.toml"\n[section]\nx = 1\n')
    main = _write(tmp_path, "main.toml", '__include__ = "b.toml"\n[section]\nz = 3\n')
    assert _load(main)["section"] == {"x": 1, "y": 2, "z": 3}


def test_lists_are_replaced_not_merged(tmp_path: Path) -> None:
    _write(tmp_path, "common.toml", "items = [1, 2]\n")
    main = _write(tmp_path, "main.toml", '__include__ = "common.toml"\nitems = [3]\n')
    assert _load(main)["items"] == [3]


def test_json_includes(tmp_path: Path) -> None:
    _write(tmp_path, "common.json", json.dumps({"port": 4}))
    main = _write(
        tmp_path, "main.json", json.dumps({"name": "m", "__include__": "common.json"})
    )
    data = _load(main)
    assert (data["name"], data["port"]) == ("m", 4)


def test_missing_include_is_skipped_with_a_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    main = _write(tmp_path, "main.toml", 'name = "m"\n__include__ = "nope.toml"\n')
    with caplog.at_level(logging.WARNING):
        data = _load(main)
    assert data["name"] == "m"
    assert any("nope.toml" in r.getMessage() for r in caplog.records)


def test_missing_include_raises_if_the_file_is_required(tmp_path: Path) -> None:
    main = _write(tmp_path, "main.toml", '__include__ = "nope.toml"\n')
    with pytest.raises(FileNotFoundError):
        _load(main, throw=True)


@pytest.mark.parametrize(
    "value",
    [
        14,
        True,
        None,
        "",
        [""],
        [1],
        ["common.json", 2],
        ["common.json", None],
        {"a": 1},
    ],
)
def test_include_with_a_wrong_shape_is_rejected(tmp_path: Path, value: object) -> None:
    _write(tmp_path, "common.json", json.dumps({"port": 1}))
    main = _write(tmp_path, "main.json", json.dumps({"__include__": value}))
    with pytest.raises(ValueError, match="__include__ must be"):
        _load(main)


def test_empty_list_of_includes_is_fine(tmp_path: Path) -> None:
    main = _write(tmp_path, "main.toml", 'name = "m"\n__include__ = []\n')
    assert _load(main)["name"] == "m"


def test_include_with_a_reference_is_rejected(tmp_path: Path) -> None:
    main = _write(tmp_path, "main.toml", '__include__ = "${env:DIR}/common.toml"\n')
    with pytest.raises(ValueError, match="__include__.*reference"):
        _load(main)


# --- problems that are to be fixed; the markers go away together with the fix ---


@pytest.mark.parametrize("cycle", ["self", "two files"])
def test_circular_include_raises(tmp_path: Path, cycle: str) -> None:
    if cycle == "self":
        main = _write(tmp_path, "main.toml", '__include__ = "main.toml"\n')
    else:
        main = _write(tmp_path, "main.toml", '__include__ = "other.toml"\n')
        _write(tmp_path, "other.toml", '__include__ = "main.toml"\n')
    with pytest.raises(ValueError, match="circular"):
        _load(main)


def test_circular_include_names_the_files(tmp_path: Path) -> None:
    main = _write(tmp_path, "main.toml", '__include__ = "other.toml"\n')
    _write(tmp_path, "other.toml", '__include__ = "main.toml"\n')
    with pytest.raises(ValueError) as excinfo:
        _load(main)
    assert "main.toml" in str(excinfo.value) and "other.toml" in str(excinfo.value)


def test_a_file_that_is_included_twice_is_no_cycle(tmp_path: Path) -> None:
    _write(tmp_path, "shared.toml", "port = 7\n")
    _write(tmp_path, "b.toml", '__include__ = "shared.toml"\n')
    _write(tmp_path, "c.toml", '__include__ = "shared.toml"\n')
    main = _write(tmp_path, "main.toml", '__include__ = ["b.toml", "c.toml"]\n')
    assert _load(main)["port"] == 7


def test_include_key_is_not_in_the_loaded_data(tmp_path: Path) -> None:
    _write(tmp_path, "common.toml", "port = 5\n")
    main = _write(tmp_path, "main.toml", '__include__ = "common.toml"\n')
    assert "__include__" not in _load(main)


def test_include_key_of_a_nested_include_is_not_in_the_loaded_data(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "c.toml", "port = 5\n")
    _write(tmp_path, "b.toml", '__include__ = "c.toml"\n')
    main = _write(tmp_path, "main.toml", '__include__ = "b.toml"\n')
    assert "__include__" not in _load(main)


def test_include_key_is_not_reported_as_an_extra_parameter(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    _write(tmp_path, "common.toml", "port = 5\n")
    main = _write(tmp_path, "main.toml", 'name = "m"\n__include__ = "common.toml"\n')
    IncludeConfig.set_filepath(main)
    with caplog.at_level(logging.DEBUG):
        config = IncludeConfig.load()
    assert config.port == 5
    assert not any("__include__" in r.getMessage() for r in caplog.records)
