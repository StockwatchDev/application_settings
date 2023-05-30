"""Functions that can be called from the application to make life easy."""

from argparse import ArgumentParser, ArgumentError
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
    try:
        parser.add_argument(
            short_option,
            long_option,
            nargs=1,
            default=None,
            type=Path,
            help=helptext,
            required=False,
        )
    except ArgumentError as the_error:
        if "conflicting option string" in the_error.message:
            if "--config_filepath" in the_error.message:
                print(
                        "Warning: commandline option '--config_filepath' has been set already."
                    )
            if short_option in the_error.message:
                print(
                        f"Warning: commandline option '{short_option}' has been set already."
                    )
        else:
            raise the_error
    args = parser.parse_args()
    if cmdline_path := args.config_filepath:
        universal_cmdline_path = Path(cmdline_path[0])
        config_class.set_filepath(universal_cmdline_path)
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
