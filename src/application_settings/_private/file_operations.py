"""Functions for storing dicts to and loading dicts from file."""
from collections.abc import Callable
from enum import Enum, unique
from pathlib import Path
from typing import Any, cast

from loguru import logger
from pathvalidate import is_valid_filepath

from application_settings._private.json_file_operations import load_json, save_json
from application_settings._private.toml_file_operations import load_toml, save_toml
from application_settings.type_notation_helper import LoaderOpt, PathOpt, SaverOpt


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
        if loader := _get_loader(path=real_path):
            if kind == "Config":
                return _load_with_includes(real_path, throw_if_file_not_found, loader)
            return loader(real_path)
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
        if saver := _get_saver(path=path):
            return saver(path, data)
    return None


def _get_loader(path: Path) -> LoaderOpt:
    """Return the loader to be used for the file extension ext and the kind (Config or Settings)"""
    # TODO: enable with_includes for all all kinds
    ext = path.suffix[1:].lower()
    if ext == FileFormat.JSON.value:
        return load_json
    if ext == FileFormat.TOML.value:
        return load_toml
    return None


def _load_with_includes(
    path: Path, throw_if_file_not_found: bool, loader: Callable[[Path], dict[str, Any]]
) -> dict[str, Any]:
    data_stored = loader(path)
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
                        _load_with_includes(
                            included_file_path, throw_if_file_not_found, loader
                        )
                        | data_stored
                    )
            else:
                raise ValueError(
                    f"Given path: '{included_file}' is not a valid path for this OS"
                )
    return data_stored


def _get_saver(path: Path) -> SaverOpt:
    """Return the loader to be used for the file extension ext and the kind (Config or Settings)"""
    # TODO: enable with_includes for all kinds
    ext = path.suffix[1:].lower()
    if ext == FileFormat.JSON.value:
        return save_json
    if ext == FileFormat.TOML.value:
        return save_toml
    return None
