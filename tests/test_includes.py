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


def test_first_listed_include_wins_over_later_ones(tmp_path: Path) -> None:
    _write(tmp_path, "first.toml", "port = 1\n")
    _write(tmp_path, "second.toml", "port = 2\nratio = 2.5\n")
    main = _write(
        tmp_path, "main.toml", '__include__ = ["first.toml", "second.toml"]\n'
    )
    data = _load(main)
    assert (data["port"], data["ratio"]) == (1, 2.5)


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


def test_include_with_a_reference_is_rejected(tmp_path: Path) -> None:
    main = _write(tmp_path, "main.toml", '__include__ = "${env:DIR}/common.toml"\n')
    with pytest.raises(ValueError, match="__include__.*reference"):
        _load(main)


# --- problems that are to be fixed; the markers go away together with the fix ---


@pytest.mark.xfail(strict=True, reason="no cycle detection yet (step 3)")
@pytest.mark.parametrize("cycle", ["self", "two files"])
def test_circular_include_raises(tmp_path: Path, cycle: str) -> None:
    if cycle == "self":
        main = _write(tmp_path, "main.toml", '__include__ = "main.toml"\n')
    else:
        main = _write(tmp_path, "main.toml", '__include__ = "other.toml"\n')
        _write(tmp_path, "other.toml", '__include__ = "main.toml"\n')
    with pytest.raises(ValueError, match="circular"):
        _load(main)


@pytest.mark.xfail(strict=True, reason="__include__ is reported as extra (step 6)")
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
