"""
Unit tests for the `application_settings.parametrization` module.

This module tests all public functions and classes in `application_settings.parametrization`,
ensuring 100% code coverage.
"""

from unittest.mock import patch

import pytest

from application_settings.parameter_kind import ParameterKind
from application_settings.parametrization import (
    _ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS,
    ApplicationConfigSection,
    ApplicationSettingsSection,
    log_level,
)


def test_log_level_config() -> None:
    """Test `log_level` for `ParameterKind.CONFIG`."""
    with patch.object(
        ApplicationConfigSection,
        "get",
        return_value=ApplicationConfigSection(strict_mode=True),
    ):
        assert log_level(ParameterKind.CONFIG) == "WARNING"

    with patch.object(
        ApplicationConfigSection,
        "get",
        return_value=ApplicationConfigSection(strict_mode=False),
    ):
        assert log_level(ParameterKind.CONFIG) == "DEBUG"


def test_log_level_settings() -> None:
    """Test `log_level` for `ParameterKind.SETTINGS`."""
    with patch.object(
        ApplicationSettingsSection,
        "get",
        return_value=ApplicationSettingsSection(strict_mode=True),
    ):
        assert log_level(ParameterKind.SETTINGS) == "WARNING"

    with patch.object(
        ApplicationSettingsSection,
        "get",
        return_value=ApplicationSettingsSection(strict_mode=False),
    ):
        assert log_level(ParameterKind.SETTINGS) == "DEBUG"


def test_log_level_invalid_kind() -> None:
    """Test `log_level` raises an error for invalid `ParameterKind`."""
    with pytest.raises(ValueError, match="Unknown value INVALID for ParameterKind."):
        log_level("INVALID")  # type: ignore


def test_application_settings_container_section_base_kind_string() -> None:
    """Test `kind_string` method of `ApplicationSettingsContainerSectionBase`."""
    assert ApplicationSettingsSection.kind_string() == "Settings"
    assert ApplicationConfigSection.kind_string() == "Config"


def test_application_settings_container_section_base_get() -> None:
    """Test the `get` method of `ApplicationSettingsContainerSectionBase`."""
    _ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS.clear()
    settings_instance = ApplicationSettingsSection.get()
    assert isinstance(settings_instance, ApplicationSettingsSection)

    config_instance = ApplicationConfigSection.get()
    assert isinstance(config_instance, ApplicationConfigSection)


def test_application_settings_container_section_base_set() -> None:
    """Test the `set` method of `ApplicationSettingsContainerSectionBase`."""
    data = {
        "settings_container_class": "test.Class",
        "strict_mode": True,
    }
    instance = ApplicationSettingsSection.set(data)
    assert instance.settings_container_class == "test.Class"
    assert instance.strict_mode is True


def test_application_settings_container_section_base_create_instance() -> None:
    """Test `_create_instance` of `ApplicationSettingsContainerSectionBase`."""
    instance_settings = ApplicationSettingsSection._create_instance()
    assert isinstance(instance_settings, ApplicationSettingsSection)

    instance_config = ApplicationConfigSection._create_instance()
    assert isinstance(instance_config, ApplicationConfigSection)


def test_application_settings_container_section_base_get_without_load() -> None:
    """Test `get_without_load` method of `ApplicationSettingsContainerSectionBase`."""
    assert ApplicationSettingsSection.get_without_load() is None


def test_application_settings_container_section_base_get_singleton() -> None:
    """Test `_get` retrieves the singleton correctly."""
    _ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS.clear()
    assert ApplicationSettingsSection._get() is None

    instance = ApplicationSettingsSection.get()
    assert ApplicationSettingsSection._get() == instance


def test_application_settings_container_section_base_set_singleton() -> None:
    """Test `_set` stores the singleton correctly."""
    instance = ApplicationSettingsSection()
    instance._set()
    assert (
        _ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS[
            id(ApplicationSettingsSection)
        ]
        == instance
    )
