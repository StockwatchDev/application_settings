"""Functions that can be called from the application to make life easy."""

from argparse import ArgumentParser
from pathlib import Path

from application_settings.configuring_base import ConfigT
from application_settings.settings_base import SettingsT


def config_filepath_from_commandline_option(
    config_class: type[ConfigT],
    parser: ArgumentParser = ArgumentParser(),
    short_option: str = "-c",
) -> ArgumentParser:
    """Add a commandline option '--config_filepath' for the config file and set filepath if it is given"""
    long_option: str = "--config_filepath"
    helptext: str = "Path of the configuration file"
    parser.add_argument(
        short_option,
        long_option,
        nargs="?",
        default=None,
        type=Path,
        help=helptext,
    )
    args = parser.parse_args()
    if cmdline_path := args.config_filepath:
        config_class.set_filepath(cmdline_path)
    return parser


def settings_filepath_from_commandline_option(
    settings_class: type[SettingsT],
    parser: ArgumentParser = ArgumentParser(),
    short_option: str = "-s",
) -> ArgumentParser:
    """Add a commandline option '--settings_filepath' for the settings file and set filepath if it is given"""
    long_option: str = "--settings_filepath"
    helptext: str = "Path of the settings file"
    parser.add_argument(
        short_option,
        long_option,
        nargs="?",
        default=None,
        type=Path,
        help=helptext,
    )
    args = parser.parse_args()
    if cmdline_path := args.settings_filepath:
        settings_class.set_filepath(cmdline_path)
    return parser
