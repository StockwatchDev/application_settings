"""Funtions for storing dicts to and loading dicts from file."""
import json
import sys
from enum import Enum, unique
from pathlib import Path
from typing import Any, cast

import tomli_w
from loguru import logger
from pathvalidate import is_valid_filepath

from application_settings.type_notation_helper import PathOpt

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@unique
class FileFormat(Enum):
    """File formats that are supported by application_settings"""

    TOML = "toml"
    JSON = "json"


def _check_filepath(
    path: PathOpt,
    throw_if_invalid_path: bool,
    throw_if_file_not_found: bool,
    create_file_if_not_found: bool,
) -> bool:
    """Log an error and/or throw if path cannot be loaded and return a bool whether it can"""
    if not path:
        err_mess = f"Path {str(path)} not valid."
        if throw_if_invalid_path:
            raise FileNotFoundError(err_mess)
        logger.error(err_mess)
        return False
    ext = path.suffix[1:].lower()
    try:
        FileFormat(ext)
    except ValueError:
        logger.error(f"Unknown file format {ext} given in {path}.")
        return False
    if not path.is_file():
        mess = f"Path {str(path)} is not a file."
        if create_file_if_not_found:
            path.touch()
            if not path.is_file():
                logger.error(f"Creation of file {str(path)} failed.")
                return False
            logger.info(f"File {str(path)} created.")
            return True
        if throw_if_file_not_found:
            raise FileNotFoundError(mess)
        logger.warning(mess)
        return False
    return True


def load(kind: str, path: PathOpt, throw_if_file_not_found: bool) -> dict[str, Any]:
    """Load data from the file given in path; log error or throw if not possible"""
    if _check_filepath(
        path,
        throw_if_invalid_path=throw_if_file_not_found,
        throw_if_file_not_found=throw_if_file_not_found,
        create_file_if_not_found=False,
    ):
        real_path = cast(Path, path)
        if (ext := real_path.suffix[1:].lower()) == FileFormat.JSON.value:
            return _load_json(real_path)
        if ext == FileFormat.TOML.value:
            if kind == "Config":
                return _load_toml_with_includes(real_path, throw_if_file_not_found)
            return _load_toml(real_path)
    logger.warning(
        "Trying with default values, as loading from file is impossible. This may fail."
    )
    return {}


def save(path: Path, data: dict[str, Any]) -> None:
    """Save data to the file given in path; log error or throw if not possible"""
    if _check_filepath(
        path,
        throw_if_invalid_path=True,
        throw_if_file_not_found=False,
        create_file_if_not_found=True,
    ):
        if (ext := path.suffix[1:].lower()) == FileFormat.JSON.value:
            return _save_json(path, data)
        if ext == FileFormat.TOML.value:
            return _save_toml(path, data)
    return None


def _load_toml(path: Path) -> dict[str, Any]:
    data_stored: dict[str, Any] = {}
    with path.open(mode="rb") as fptr:
        data_stored = tomllib.load(fptr)
    return data_stored


def _load_json(path: Path) -> dict[str, Any]:
    data_stored: dict[str, Any] = {}
    with path.open(mode="r") as fptr:
        data_stored = json.load(fptr)
    return data_stored


def _load_toml_with_includes(
    path: Path, throw_if_file_not_found: bool
) -> dict[str, Any]:
    data_stored = _load_toml(path)
    if included_files := data_stored.get("__include__"):
        if not isinstance(included_files, list):
            included_files = [included_files]
        for included_file in included_files:
            if is_valid_filepath(included_file, platform="auto"):
                included_file_path = Path(included_file)
                if not included_file_path.is_absolute():
                    included_file_path = path.parents[0] / included_file_path
                included_file_path.resolve()
                if _check_filepath(
                    included_file_path,
                    throw_if_invalid_path=throw_if_file_not_found,
                    throw_if_file_not_found=throw_if_file_not_found,
                    create_file_if_not_found=False,
                ):
                    data_stored = (
                        _load_toml_with_includes(
                            included_file_path, throw_if_file_not_found
                        )
                        | data_stored
                    )
            else:
                raise ValueError(
                    f"Given path: '{included_file}' is not a valid path for this OS"
                )
    return data_stored


def _save_json(path: Path, data: dict[str, Any]) -> None:
    with path.open(mode="w") as fptr:
        json.dump(data, fptr)


def _save_toml(path: Path, data: dict[str, Any]) -> None:
    with path.open(mode="wb") as fptr:
        tomli_w.dump(data, fptr)
