"""Functions for storing dicts to and loading dicts from toml files."""
from pathlib import Path
from typing import Any

import tomlkit


def load_toml(path: Path) -> dict[str, Any]:
    """Load the info in the toml file given by path and return as dict"""
    data_stored: dict[str, Any] = {}
    with path.open(mode="r") as fptr:
        data_stored = tomlkit.load(fptr)
    return data_stored


def save_toml(path: Path, data: dict[str, Any]) -> None:
    """Save the info in the data dict to the toml file given by path"""
    with path.open(mode="w") as fptr:
        tomlkit.dump(data, fptr)
