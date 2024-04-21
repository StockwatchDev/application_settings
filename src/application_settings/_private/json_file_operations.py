"""Functions for storing dicts to and loading dicts from json files."""
import json


def load_json(path):
    """Load the info in the json file given by path and return as dict"""
    data_stored = {}
    with path.open(mode="r") as fptr:
        data_stored = json.load(fptr)
    return data_stored


def save_json(path, data):
    """Save the info in the data dict to the json file given by path"""
    with path.open(mode="w") as fptr:
        json.dump(data, fptr)
