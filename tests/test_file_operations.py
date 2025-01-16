"""
Unit tests for the file operations module in `application_settings`.

This module tests the public and private functions related to file operations,
ensuring that all edge cases are covered and exceptions are handled correctly.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from application_settings._private.file_operations import (
    _check_filepath,
    _container_class_keys,
    _get_loader,
    _get_saver,
    _load_with_includes,
    get_container_from_file,
    load,
    save,
)
from application_settings.parameter_kind import ParameterKind


@pytest.fixture
def mock_path(tmp_path: Path) -> Path:
    """Provide a mock file path for tests."""
    return tmp_path / "test_file.json"


@pytest.fixture
def mock_path2(tmp_path: Path) -> Path:
    """Provide a mock file path for tests."""
    return Path("test_file.json")


def test_check_filepath_valid(mock_path: Path) -> None:
    """Test `_check_filepath` for a valid file path."""
    mock_path.touch()
    assert _check_filepath(mock_path, True, False, False) is True


def test_check_filepath_invalid_path() -> None:
    """Test `_check_filepath` with an invalid path."""
    with pytest.raises(FileNotFoundError, match="Path None not valid."):
        _check_filepath(None, True, False, False)


def test_check_filepath_file_not_found(mock_path2: Path) -> None:
    """Test `_check_filepath` for a non-existent file."""
    match_str = f"Path {str(mock_path2)} is not a file."
    with pytest.raises(FileNotFoundError, match=match_str):
        _check_filepath(mock_path2, False, True, False)


def test_check_filepath_create_file(mock_path: Path) -> None:
    """Test `_check_filepath` when a file is created."""
    assert _check_filepath(mock_path, False, False, True) is True
    assert mock_path.exists()


def test_check_filepath_invalid_extension(mock_path: Path) -> None:
    """Test `_check_filepath` with an unsupported file format."""
    mock_path = mock_path.with_suffix(".unsupported")
    assert _check_filepath(mock_path, False, False, False) is False


def test_container_class_keys() -> None:
    """Test `_container_class_keys` for correct key generation."""
    config_keys = _container_class_keys(ParameterKind.CONFIG)
    settings_keys = _container_class_keys(ParameterKind.SETTINGS)

    assert config_keys == ("application_config", "config_container_class")
    assert settings_keys == ("application_settings", "settings_container_class")


@patch(
    "application_settings._private.file_operations._check_filepath", return_value=True
)
@patch(
    "application_settings._private.file_operations._get_loader",
    return_value=Mock(
        return_value={"application_config": {"config_container_class": "test.Class"}}
    ),
)
def test_get_container_from_file(
    mock_get_loader: Mock, mock_check_filepath: Mock, mock_path: Path
) -> None:
    """Test `get_container_from_file` retrieves the correct container."""
    result = get_container_from_file(ParameterKind.CONFIG, mock_path, True)
    assert result == "test.Class"


def test_get_container_from_file_empty(mock_path: Path) -> None:
    """Test `get_container_from_file` returns an empty string when loading fails."""
    result = get_container_from_file(ParameterKind.CONFIG, mock_path, False)
    assert result == ""


@patch(
    "application_settings._private.file_operations._get_loader",
    return_value=Mock(return_value={}),
)
def test_load_with_default_values(mock_get_loader: Mock, mock_path: Path) -> None:
    """Test `load` falls back to default values when loading fails."""
    result = load(ParameterKind.SETTINGS, mock_path, False)
    assert result == {}


@patch(
    "application_settings._private.file_operations._check_filepath", return_value=True
)
@patch(
    "application_settings._private.file_operations._load_with_includes",
    return_value={"key": "value"},
)
@patch("application_settings._private.file_operations._get_loader", return_value=Mock())
def test_load_with_includes(
    mock_get_loader: Mock,
    mock_load_with_includes: Mock,
    mock_check_filepath: Mock,
    mock_path: Path,
) -> None:
    """Test `load` with included files."""
    result = load(ParameterKind.CONFIG, mock_path, False)
    assert result == {"key": "value"}


@patch(
    "application_settings._private.file_operations._check_filepath", return_value=True
)
@patch("application_settings._private.file_operations._get_saver", return_value=Mock())
def test_save(mock_get_saver: Mock, mock_check_filepath: Mock, mock_path: Path) -> None:
    """Test `save` writes data to a file."""
    save(mock_path, {"key": "value"})
    mock_get_saver.return_value.assert_called_once_with(mock_path, {"key": "value"})


def test_get_loader_json(mock_path: Path) -> None:
    """Test `_get_loader` for JSON files."""
    mock_path = mock_path.with_suffix(".json")
    loader = _get_loader(mock_path)
    assert loader is not None


def test_get_loader_toml(mock_path: Path) -> None:
    """Test `_get_loader` for TOML files."""
    mock_path = mock_path.with_suffix(".toml")
    loader = _get_loader(mock_path)
    assert loader is not None


def test_get_loader_unsupported(mock_path: Path) -> None:
    """Test `_get_loader` for unsupported file types."""
    mock_path = mock_path.with_suffix(".unsupported")
    loader = _get_loader(mock_path)
    assert loader is None


def test_get_saver_json(mock_path: Path) -> None:
    """Test `_get_saver` for JSON files."""
    mock_path = mock_path.with_suffix(".json")
    saver = _get_saver(mock_path)
    assert saver is not None


def test_get_saver_toml(mock_path: Path) -> None:
    """Test `_get_saver` for TOML files."""
    mock_path = mock_path.with_suffix(".toml")
    saver = _get_saver(mock_path)
    assert saver is not None


def test_get_saver_unsupported(mock_path: Path) -> None:
    """Test `_get_saver` for unsupported file types."""
    mock_path = mock_path.with_suffix(".unsupported")
    saver = _get_saver(mock_path)
    assert saver is None


@patch(
    "application_settings._private.file_operations.is_valid_filepath",
    return_value=False,
)
def test_load_with_includes_invalid_path(
    mock_is_valid_filepath: Mock, mock_path: Path
) -> None:
    """Test `_load_with_includes` raises an error for invalid include paths."""
    with pytest.raises(
        ValueError, match="Given path: 'invalid_path' is not a valid path for this OS"
    ):
        _load_with_includes(
            mock_path, True, Mock(return_value={"__include__": "invalid_path"})
        )
