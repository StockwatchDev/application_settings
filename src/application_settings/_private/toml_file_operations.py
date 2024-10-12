"""Functions for storing dicts to and loading dicts from toml files."""

from pathlib import Path
from typing import Any

import tomlkit
from loguru import logger

from application_settings._private.file_operations_utils import deep_update


def load_toml(path: Path) -> dict[str, Any]:
    """Load the info in the toml file given by path and return as dict"""
    data_stored: dict[str, Any] = {}
    if (
        path.stat().st_size > 0
    ):  # this evaluates to false if the file does not exist or is empty
        with path.open(mode="r") as fptr:
            data_stored = tomlkit.load(fptr)
    else:
        logger.warning(f"File {path} does not exist or is empty.")
    return data_stored


def save_toml(path: Path, data: dict[str, Any]) -> None:
    """Update the toml file given by path with data"""
    old_data = load_toml(path)
    updated_data = deep_update(old_data, data)
    with path.open(mode="w") as fptr:
        tomlkit.dump(updated_data, fptr)
