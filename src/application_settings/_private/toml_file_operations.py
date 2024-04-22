"""Functions for storing dicts to and loading dicts from toml files."""
import tomli_w
import tomli


def load_toml(path):
    """Load the info in the toml file given by path and return as dict"""
    data_stored = {}
    with path.open(mode="rb") as fptr:
        data_stored = tomli.load(fptr)
    return data_stored


def save_toml(path, data):
    """Save the info in the data dict to the toml file given by path"""
    with path.open(mode="wb") as fptr:
        tomli_w.dump(data, fptr)
