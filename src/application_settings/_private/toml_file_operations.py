"""Funtions for storing dicts to and loading dicts from toml files."""
import sys
from pathlib import Path
from typing import Any

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_toml(path: Path) -> dict[str, Any]:
    """Load the info in the toml file given by path and return as dict"""
    data_stored: dict[str, Any] = {}
    with path.open(mode="rb") as fptr:
        data_stored = tomllib.load(fptr)
    return data_stored


def save_toml(path: Path, data: dict[str, Any]) -> None:
    """Save the info in the data dict to the toml file given by path"""
    with path.open(mode="wb") as fptr:
        tomli_w.dump(data, fptr)
