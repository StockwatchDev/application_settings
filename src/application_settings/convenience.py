"""Functions that can be called from the application to make life easy."""
from argparse import ArgumentParser
from logging import Formatter, Handler, LogRecord, getLogger
from pathlib import Path
from typing import Union

from loguru import logger

from application_settings.configuring_base import ConfigT
from application_settings.settings_base import SettingsT


def config_filepath_from_cli(
    config_class: type[ConfigT],
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
    settings_class: type[SettingsT],
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


def parameters_folderpath_from_cli(  # pylint: disable=too-many-arguments
    config_class: type[ConfigT],
    settings_class: type[SettingsT],
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


def _parameters_filepath_from_cli(  # pylint: disable=too-many-arguments
    config_class: Union[  # pylint: disable=consider-alternative-union-syntax
        type[ConfigT], None
    ],
    settings_class: Union[  # pylint: disable=consider-alternative-union-syntax
        type[SettingsT], None
    ],
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


def use_standard_logging(  # pylint: disable=consider-alternative-union-syntax
    enable: bool = False, fmt: Union[Formatter, None] = None
) -> None:
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
