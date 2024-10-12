"""Functions for storing dicts to and loading dicts from json files."""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from application_settings._private.file_operations_utils import deep_update


def load_json(path: Path) -> dict[str, Any]:
    """Load the info in the json file given by path and return as dict"""
    data_stored: dict[str, Any] = {}
    if (
        path.stat().st_size > 0
    ):  # this evaluates to false if the file does not exist or is empty
        with path.open(mode="r") as fptr:
            data_stored = json.load(fptr)
    else:
        logger.warning(f"File {path} does not exist or is empty.")
    return data_stored


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Update the json file given by path with the data"""
    old_data = load_json(path)
    updated_data = deep_update(old_data, data)
    with path.open(mode="w") as fptr:
        json.dump(updated_data, fptr)
