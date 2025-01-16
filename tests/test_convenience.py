"""Test the module application_settings.convenience"""

# pylint: disable=unused-argument

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock, patch

import pytest

from application_settings._private.file_operations import FileFormat
from application_settings.convenience import (
    _get_config_class,
    _get_module,
    _get_module_from_file,
    _get_settings_class,
    config_filepath_from_cli,
    parameters_folderpath_from_cli,
    settings_filepath_from_cli,
    use_standard_logging,
)
from application_settings.parameter_kind import ParameterKind, ParameterKindStr

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class MockParameterContainerProtocolClass:
    """Mock class that adheres to the ParameterContainerProtocol"""

    @staticmethod
    def kind() -> ParameterKind:
        """kind method"""
        return ParameterKind.CONFIG

    @classmethod
    def kind_string(cls) -> ParameterKindStr:
        """kine_string method"""
        return "Config"

    @classmethod
    def get(cls) -> Self:
        """get method"""
        return cls()

    @classmethod
    def get_without_load(cls) -> None:
        """get_without_load method"""

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        """set method"""
        return cls()

    def _set(self) -> Self:
        """_set method"""
        return self

    def _check_uninitialized_and_extra(
        self, data: dict[str, Any], section_name: str = ""
    ) -> Self:
        """_check_uninitialized_and_extra method"""
        return self

    @classmethod
    def default_file_format(cls) -> FileFormat:
        """default_file_format method"""
        return FileFormat.JSON

    @classmethod
    def default_foldername(cls) -> str:
        """default_foldername method"""
        return "a folder"

    @classmethod
    def default_filename(cls) -> str:
        """default_filename method"""
        return " a filename"

    @classmethod
    def default_filepath(cls) -> Optional[Path]:
        """default_filepath method"""
        return None

    @classmethod
    def set_filepath(cls, file_path: str = "", load: bool = False) -> None:
        """set_filepath method"""
        return None

    @classmethod
    def filepath(cls) -> Optional[Path]:
        """filepath method"""
        return None

    @classmethod
    def load(cls, throw_if_file_not_found: bool = False) -> Self:
        """load method"""
        return cls()

    def _save(self) -> Self:
        """_save method"""
        return self


class MockUpdateableParameterContainerProtocolClass(
    MockParameterContainerProtocolClass
):
    """Mock class that adheres to the UpdateableParameterContainerProtocol"""

    @classmethod
    def update(cls, changes: dict[str, Any]) -> Self:
        """update method"""
        return cls()


class MockConfigClass(MockParameterContainerProtocolClass):
    """Mock class for Config"""


class MockSettingsClass(MockUpdateableParameterContainerProtocolClass):
    """Mock class for Settings"""


def test_get_module_from_file_valid() -> None:
    """Test retrieving a module from a valid file."""
    with patch("application_settings.convenience.importlib.util") as mock_importlib:
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_importlib.spec_from_file_location.return_value = mock_spec
        mock_importlib.module_from_spec.return_value = mock_module
        qualified_classname = "path.to.module.ClassName"
        assert _get_module_from_file(qualified_classname) == mock_module


def test_get_module_from_file_invalid() -> None:
    """Test retrieving a module from an invalid file."""
    with patch("application_settings.convenience.importlib.util") as mock_importlib:
        mock_importlib.spec_from_file_location.return_value = None
        qualified_classname = "invalid.module.ClassName"
        assert _get_module_from_file(qualified_classname) is None


def test_get_module_valid() -> None:
    """Test retrieving a module by its valid qualified name."""
    with patch(
        "application_settings.convenience.importlib.import_module"
    ) as mock_import_module:
        mock_module = MagicMock()
        mock_import_module.return_value = mock_module
        qualified_classname = "valid.module.ClassName"
        assert _get_module(qualified_classname) == mock_module


def test_get_module_invalid() -> None:
    """Test retrieving a module by an invalid qualified name."""
    with patch(
        "application_settings.convenience.importlib.import_module"
    ) as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        qualified_classname = "invalid.module.ClassName"
        assert _get_module(qualified_classname) is None


def test_get_module_invalid_no_package() -> None:
    """Test retrieving a module with a missing package name."""
    qualified_classname = "ClassName"
    assert _get_module(qualified_classname) is None


def test_get_module_invalid_local() -> None:
    """Test retrieving a module with a local import syntax."""
    with patch(
        "application_settings.convenience._get_module_from_file"
    ) as mock_import_module:
        mock_import_module.return_value = None
        qualified_classname = ".ClassName"
        assert _get_module(qualified_classname) is None


def test_get_config_class_valid() -> None:
    """Test retrieving a valid configuration class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockConfigClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_config_class(qualified_classname) is MockConfigClass  # type: ignore[comparison-overlap]


def test_get_config_class_invalid_settings() -> None:
    """Test retrieving a configuration class that is invalid because it is a settings class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockSettingsClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_not_class() -> None:
    """Test retrieving a configuration class that is not a subclass of the expected class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "instanceName", MagicMock())

        qualified_classname = "valid.module.instanceName"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_not_subclass() -> None:
    """Test retrieving a configuration class that is not a subclass of the expected class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        class MockConfigClass2:
            """Mock class that is no config"""

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockConfigClass2)

        qualified_classname = "valid.module.ClassName"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_missing_class() -> None:
    """Test retrieving a configuration class that is missing in the module."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()
        mock_get_module.return_value = mock_module
        setattr(mock_module, "MissingClass", None)

        qualified_classname = "valid.module.MissingClass"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_no_module() -> None:
    """Test retrieving a configuration class from a non-existent module."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_get_module.return_value = None

        qualified_classname = "invalid.module.ClassName"
        assert _get_config_class(qualified_classname) is None


def test_get_settings_class_invalid_not_class() -> None:
    """Test retrieving a settings class that is not a subclass of the expected class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "instanceName", MagicMock())

        qualified_classname = "valid.module.instanceName"
        assert _get_settings_class(qualified_classname) is None


def test_get_settings_class_valid() -> None:
    """Test retrieving a valid settings class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockSettingsClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_settings_class(qualified_classname) is MockSettingsClass  # type: ignore[comparison-overlap]


def test_get_settings_class_invalid_not_subclass() -> None:
    """Test retrieving a settings class that is not a subclass of the expected class."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockConfigClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_settings_class(qualified_classname) is None


def test_get_settings_class_invalid_missing_class() -> None:
    """Test retrieving a settings class that is missing in the module."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()
        mock_get_module.return_value = mock_module
        setattr(mock_module, "MissingClass", None)

        qualified_classname = "valid.module.MissingClass"
        assert _get_settings_class(qualified_classname) is None


def test_get_settings_class_invalid_no_module() -> None:
    """Test retrieving a settings class from a non-existent module."""
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_get_module.return_value = None

        qualified_classname = "invalid.module.ClassName"
        assert _get_settings_class(qualified_classname) is None


def test_config_filepath_from_cli_no_input() -> None:
    """Test retrieving the config file path from CLI without input."""
    parser = ArgumentParser()
    result = config_filepath_from_cli(parser=parser)
    assert isinstance(result, ArgumentParser)


def test_config_filepath_from_cli() -> None:
    """Test retrieving the config file path from CLI with input."""
    parser = ArgumentParser()
    with patch(
        "application_settings.convenience.ArgumentParser.parse_known_args"
    ) as mock_parse_args:
        mock_args = MagicMock()
        setattr(mock_args, "config_filepath", ["/mock/path/to/config"])
        mock_parse_args.return_value = (mock_args, [])
        with pytest.raises(ValueError):
            config_filepath_from_cli(parser=parser)


def test_settings_filepath_from_cli_no_input() -> None:
    """Test retrieving the settings file path from CLI without input."""
    parser = ArgumentParser()
    result = settings_filepath_from_cli(parser=parser)
    assert isinstance(result, ArgumentParser)


def test_settings_filepath_from_cli() -> None:
    """Test retrieving the settings file path from CLI with input."""
    parser = ArgumentParser()
    with patch(
        "application_settings.convenience.ArgumentParser.parse_known_args"
    ) as mock_parse_args:
        mock_args = MagicMock()
        setattr(mock_args, "settings_filepath", ["/mock/path/to/settings"])
        mock_parse_args.return_value = (mock_args, [])
        with pytest.raises(ValueError):
            settings_filepath_from_cli(parser=parser)


def test_parameters_folderpath_from_cli() -> None:
    """Test retrieving the parameters folder path from CLI."""
    parser = ArgumentParser()
    result = parameters_folderpath_from_cli(parser=parser)
    assert isinstance(result, ArgumentParser)


def test_use_standard_logging() -> None:
    """Test enabling standard logging."""
    with patch("application_settings.convenience.logger") as mock_logger:
        use_standard_logging(enable=True)
        mock_logger.remove.assert_called_once()
        mock_logger.add.assert_called_once()
        mock_logger.enable.assert_called_once()
