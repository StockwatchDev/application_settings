"""Functions for storing dicts to and loading dicts from json files."""
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """Load the info in the json file given by path and return as dict"""
    data_stored: dict[str, Any] = {}
    with path.open(mode="r") as fptr:
        data_stored = json.load(fptr)
    return data_stored


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Save the info in the data dict to the json file given by path"""
    with path.open(mode="w") as fptr:
        json.dump(data, fptr)
