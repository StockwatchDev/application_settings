"""Example to demonstrate how to implement configurable module globals and class variables

Cd to the folder containing this file and run this example with the following command:
python . -c ./the_config.toml -w ./the_config.toml
"""

# the next module is placed at the top of the entry point but that does not help
from modules.wrongly_initialized_config import WronglyInitializedConfig  # isort:skip

# the next module contains configured class variables and configured module globals
from modules.my_dataclass import (
    MyDataclass,
    the_first_global_is_set,
    the_second_global_is_set,
)

from application_settings import config_filepath_from_cli


def main() -> int:
    """print an instance of my_dataclass and all globals"""
    print("In main()")
    # properly configured variables are initialized to 1.0 and not to 0.0
    print(
        MyDataclass()
    )  # MyDataclass(the_first_classvar_is_set_is_set=0.0, the_second_classvar_is_set=1.0)
    print(f"{the_first_global_is_set = }")  # the_first_global_is_set = False
    print(f"{the_second_global_is_set = }")  # the_second_global_is_set = True
    return 0


# don't do as shown here (this is the wrong way),
# do it as in 'correctly_initialized_config.py'
config_filepath_from_cli(
    WronglyInitializedConfig, short_option="-w", long_option="--config_filepath_w"
)
print("Now loading WronglyInitializedConfig")
WronglyInitializedConfig.load()

main()
