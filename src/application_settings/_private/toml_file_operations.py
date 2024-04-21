"""Functions for storing dicts to and loading dicts from toml files."""
import toml


def load_toml(path):
    """Load the info in the toml file given by path and return as dict"""
    data_stored = {}
    with path.open(mode="r") as fptr:
        data_stored = toml.load(fptr)
    return data_stored


def save_toml(path, data):
    """Save the info in the data dict to the toml file given by path"""
    with path.open(mode="w") as fptr:
        toml.dump(data, fptr)
