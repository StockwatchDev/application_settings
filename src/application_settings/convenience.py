"""Functions that can be called from the application to make life easy."""

import importlib
import importlib.util
import sys
from argparse import ArgumentParser
from logging import Formatter, Handler, LogRecord, getLogger
from pathlib import Path
from types import ModuleType
from typing import Optional

from loguru import logger

from application_settings._private.file_operations import get_container_from_file
from application_settings.configuring_base import ConfigBase
from application_settings.parameter_kind import ParameterKind
from application_settings.protocols import (
    ParameterContainerProtocol,
    UpdateableParameterContainerProtocol,
)
from application_settings.settings_base import SettingsBase


def _get_module_from_file(qualified_classname: str) -> Optional[ModuleType]:
    components = qualified_classname.split(".")
    module_name = components[-2]
    filename = "/".join(components[:-1])
    file_path = Path.cwd() / f"{filename}.py"
    logger.debug(f"Trying to load {qualified_classname} from {file_path}")
    if not (spec := importlib.util.spec_from_file_location(module_name, file_path)):
        logger.error(f"Unable to find module spec {module_name} with path {file_path}.")
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    if spec.loader:
        spec.loader.exec_module(module)
    return module


def _get_module(qualified_classname: str) -> Optional[ModuleType]:
    components = qualified_classname.split(".")
    if len(components) < 2:
        logger.error(
            f"Unable to import {qualified_classname}: no package / module name or no class name provided."
        )
        return None
    if components[0] == "":
        # relative import, no package
        logger.info(
            f"{qualified_classname}: attempted relative import with no known parent package. Will try to load file, but this may fail."
        )
        if not (module := _get_module_from_file(qualified_classname)):
            return None
    else:
        try:
            module = importlib.import_module(".".join(components[:-1]))
        except ModuleNotFoundError:
            logger.error(f"Module {'.'.join(components[:-1])} not found.")
            return None
    return module


def _get_config_class(
    qualified_classname: str,
) -> Optional[type[ParameterContainerProtocol]]:
    if not (module := _get_module(qualified_classname)):
        return None
    components = qualified_classname.split(".")
    if not (the_class := getattr(module, components[-1], None)):
        logger.error(
            f"No class {components[-1]} found in module {'.'.join(components[:-1])}"
        )
        return None
    if not isinstance(the_class, type):
        logger.error(
            f"Attribute {components[-1]} found in module {'.'.join(components[:-1])} but this is not a class."
        )
        return None
    logger.debug(f"Class {components[-1]} found in module {'.'.join(components[:-1])}")
    if issubclass(the_class, ParameterContainerProtocol):
        if not issubclass(the_class, UpdateableParameterContainerProtocol):
            # next line should not be needed but otherwise mypy complains
            typed_class: type[ParameterContainerProtocol] = the_class
            return typed_class

        logger.error(
            f"Class {components[-1]} implements a Settings rather than a Config"
        )
    else:
        logger.error(f"Class {components[-1]} does not implement a Config")
    return None


def _get_settings_class(
    qualified_classname: str,
) -> Optional[type[UpdateableParameterContainerProtocol]]:
    if not (module := _get_module(qualified_classname)):
        return None
    components = qualified_classname.split(".")
    if not (the_class := getattr(module, components[-1], None)):
        logger.error(
            f"No class {components[-1]} found in module {'.'.join(components[:-1])}"
        )
        return None
    if not isinstance(the_class, type):
        logger.error(
            f"Attribute {components[-1]} found in module {'.'.join(components[:-1])} but this is not a class."
        )
        return None
    logger.debug(f"Class {components[-1]} found in module {'.'.join(components[:-1])}")
    if issubclass(the_class, UpdateableParameterContainerProtocol):
        # next line should not be needed but otherwise mypy complains
        typed_class: type[UpdateableParameterContainerProtocol] = the_class
        return typed_class

    logger.error(f"Class {components[-1]} does not implement a Settings")
    return None


def config_filepath_from_cli(
    config_class: type[ParameterContainerProtocol] = ConfigBase,
    parser: ArgumentParser = ArgumentParser(),
    short_option: str = "-c",
    long_option: str = "--config_filepath",
    load: bool = False,
) -> ArgumentParser:
    """Add a commandline option for the config file and set filepath if it is given"""
    helptext: str = "Path of the configuration file"
    return _parameters_filepath_from_cli(
        config_class=config_class,
        settings_class=None,
        parser=parser,
        short_option=short_option,
        long_option=long_option,
        helptext=helptext,
        load=load,
    )


def settings_filepath_from_cli(
    settings_class: type[UpdateableParameterContainerProtocol] = SettingsBase,
    parser: ArgumentParser = ArgumentParser(),
    short_option: str = "-s",
    long_option: str = "--settings_filepath",
    load: bool = False,
) -> ArgumentParser:
    """Add a commandline option for the settings file and set filepath if it is given"""
    helptext: str = "Path of the settings file"
    return _parameters_filepath_from_cli(
        config_class=None,
        settings_class=settings_class,
        parser=parser,
        short_option=short_option,
        long_option=long_option,
        helptext=helptext,
        load=load,
    )


def parameters_folderpath_from_cli(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    config_class: type[ParameterContainerProtocol] = ConfigBase,
    settings_class: type[UpdateableParameterContainerProtocol] = SettingsBase,
    parser: ArgumentParser = ArgumentParser(),
    short_option: str = "-p",
    long_option: str = "--parameters_folderpath",
    load: bool = False,
) -> ArgumentParser:
    """Add a commandline option '--parameters_folderpath' for the common config and settings folder and set filepaths if it is given.

    Default filenames will be appended to the folderpath for config and settings."""
    helptext: str = "Common path of the config file and settings file"
    return _parameters_filepath_from_cli(
        config_class=config_class,
        settings_class=settings_class,
        parser=parser,
        short_option=short_option,
        long_option=long_option,
        helptext=helptext,
        load=load,
    )


def _parameters_filepath_from_cli(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    config_class: Optional[type[ParameterContainerProtocol]],
    settings_class: Optional[type[UpdateableParameterContainerProtocol]],
    parser: ArgumentParser,
    short_option: str,
    long_option: str,
    helptext: str,
    load: bool,
) -> ArgumentParser:
    parser.add_argument(
        short_option,
        long_option,
        nargs=1,
        default=None,
        type=Path,
        help=helptext,
    )
    args, _ = parser.parse_known_args()
    if cmdline_path := getattr(args, long_option[2:], None):
        universal_cmdline_path = Path(cmdline_path[0])
        if config_class == ConfigBase:
            config_classname = get_container_from_file(
                ParameterKind.CONFIG, universal_cmdline_path, True
            )
            if not (config_class := _get_config_class(config_classname)):
                raise ValueError(f"Unable to import {config_classname}")
        if settings_class == SettingsBase:
            settings_classname = get_container_from_file(
                ParameterKind.SETTINGS, universal_cmdline_path, True
            )
            if not (settings_class := _get_settings_class(settings_classname)):
                raise ValueError(f"Unable to import {settings_classname}")
        if config_class and settings_class:
            config_class.set_filepath(
                universal_cmdline_path / config_class.default_filename(), load=load
            )
            settings_class.set_filepath(
                universal_cmdline_path / settings_class.default_filename(), load=load
            )
        elif config_class:
            config_class.set_filepath(universal_cmdline_path, load=load)
        elif settings_class:
            settings_class.set_filepath(universal_cmdline_path, load=load)
    return parser


def use_standard_logging(enable: bool = False, fmt: Optional[Formatter] = None) -> None:
    """Propagate Loguru messages to standard logging"""

    class PropagateHandler(Handler):
        """Handler to propagate log records to standard logging"""

        def emit(self, record: LogRecord) -> None:
            """Let the standard logger handle the log record"""

            getLogger(record.name).handle(record)

    handler = PropagateHandler()
    handler.setFormatter(fmt)
    logger.remove()  # Remove all handlers added so far, including the default one.
    logger.add(handler, format="{message}")

    if enable:
        logger.enable(__package__)
