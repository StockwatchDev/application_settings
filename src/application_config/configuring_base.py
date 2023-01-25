"""Module for handling configuration."""
import sys
from dataclasses import fields
from pathlib import Path
from re import sub
from typing import Any, TypeVar

from pathvalidate import sanitize_filepath
from pydantic.dataclasses import dataclass

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


TConfig = TypeVar("TConfig", bound="ConfigBase")  # pylint: disable=invalid-name
TConfigSection = TypeVar(  # pylint: disable=invalid-name
    "TConfigSection", bound="ConfigSectionBase"
)


_ALL_CONFIGS: dict[int, Any] = {}


@dataclass(frozen=True)
class ConfigSectionBase:
    """Base class for all ConfigSection classes (so that we can bound a TypeVar)"""


@dataclass(frozen=True)
class ConfigBase:
    """Base class for main Config class"""

    @classmethod
    def default_config_foldername(cls: type[TConfig]) -> str:
        """Return the class name without 'Config' and with a preceding dot as default for the folder that will hold the config file."""
        return (
            "."
            + sub("(?<!^)(?=[A-Z])", "_", cls.__name__.replace("Config", "")).lower()
        )

    @classmethod
    def default_config_filepath(cls: type[TConfig]) -> Path | None:
        """Return the fully qualified path for the configfile: e.g. ~/.Example/config.toml"""
        return Path.home() / f"{cls.default_config_foldername()}" / "config.toml"

    @classmethod
    def get(
        cls: type[TConfig], reload: bool = False, configfile_path: str | Path = ""
    ) -> TConfig:
        """Access method for the singleton."""

        if ((_the_config_or_none := _ALL_CONFIGS.get(id(cls))) is None) or reload:
            # no config has been made yet or it needs to be reloaded,
            # so let's instantiate one and keep it in the global store
            _the_config = cls._create_instance(configfile_path)
            _ALL_CONFIGS[id(cls)] = _the_config
        else:
            _the_config = _the_config_or_none
        return _the_config

    @classmethod
    def _create_instance(cls: type[TConfig], configfile_path: str | Path) -> TConfig:
        """Instantiate the Config."""

        # get whatever is stored in the config file
        config_stored = cls._get_stored_config(configfile_path)
        # filter out fields that are both stored and an attribute of the Config
        _config_fields = {
            fld for fld in fields(cls) if fld.init and fld.name in config_stored.keys()
        }
        # instantiate the sections and keep them in a dict
        # actually sections: dict[str, TConfigSection]
        # but MyPy doesn't swallow that
        sections: dict[str, Any] = {
            fld.name: cls._instantiate_section_config(fld.type, config_stored[fld.name])
            for fld in _config_fields
        }

        # instantiate the Config with the sections
        return cls(**sections)

    @classmethod
    def _get_stored_config(cls, configfile_path: str | Path) -> dict[str, Any]:
        """Get the config stored in the toml file"""
        config_stored: dict[str, Any] = {}
        if configfile_path:
            if isinstance(configfile_path, Path):
                path: Path | None = configfile_path
            else:
                if (
                    not sanitize_filepath(configfile_path, platform="auto")
                    == configfile_path
                ):
                    raise ValueError
                path = Path(configfile_path)
        else:
            path = cls.default_config_filepath()
        if path:
            try:
                with path.open(mode="rb") as fptr:
                    config_stored = tomllib.load(fptr)
            except FileNotFoundError:
                print(
                    f"Error: configfile {path} not found; trying with defaults, but this may not work."
                )
        else:
            print(
                "No path specified for configfile; trying with defaults, but this may not work."
            )
        return config_stored

    @classmethod
    def _instantiate_section_config(
        cls: type[TConfig],
        class_to_instantiate: type[TConfigSection],
        arg_dict: dict[str, Any],
    ) -> TConfigSection:
        """Return an instance of class_to_instantiate, properly initialized"""
        # pre-condition: class_to_instantiate is the class of an initializable field of cls
        assert (
            len([f for f in fields(cls) if f.init and f.type == class_to_instantiate])
            > 0
        )

        field_set = {f.name for f in fields(class_to_instantiate) if f.init}
        filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
        return class_to_instantiate(**filtered_arg_dict)
