"""Example to demonstrate how to load a config without specifying the config class in code

Cd to the folder containing this file and run this example with the following command:
python . -c ./the_config.toml
"""

from lib_config import MyLibConfigSection

from application_settings import ConfigBase, config_filepath_from_cli


def main() -> int:
    """print an instance of my_dataclass and all globals"""
    print(f"{MyLibConfigSection.get().configvar_with_default_zero = }")
    print(
        "In main(), loading from command line without specifying Config container class"
    )
    config_filepath_from_cli(ConfigBase, load=True)

    print(f"{MyLibConfigSection.get().configvar_with_default_zero = }")
    return 0


main()
