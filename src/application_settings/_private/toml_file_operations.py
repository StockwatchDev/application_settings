"""Functions for storing dicts to and loading dicts from toml files."""

from pathlib import Path
from typing import Any

import tomlkit

from application_settings._private.file_operations_utils import deep_update


def load_toml(path: Path) -> dict[str, Any]:
    """Load the info in the toml file given by path and return as dict"""
    data_stored: dict[str, Any] = {}
    with path.open(mode="r") as fptr:
        data_stored = tomlkit.load(fptr)
    return data_stored


def save_toml(path: Path, data: dict[str, Any]) -> None:
    """Update the toml file given by path with data"""
    if path.stat().st_size > 0:
        old_data = load_toml(path)
        updated_data = deep_update(old_data, data)
    else:
        updated_data = data
    with path.open(mode="w") as fptr:
        tomlkit.dump(updated_data, fptr)
