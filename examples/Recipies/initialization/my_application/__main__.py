"""Example to demonstrate how to implement configurable module globals and class variables

Cd to the folder containing this file and run this example with the following command:
python . -c ./the_config.toml -w ./the_config.toml
"""

# import of WronglyInitializedConfig placed at the top of the entry point but that does not help
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
    # properly configured variables are initialized to True and not to False
    print(
        MyDataclass()
    )  # MyDataclass(the_first_classvar_is_set=False, the_second_classvar_is_set=True)
    print(f"{the_first_global_is_set = }")  # the_first_global_is_set = False
    print(f"{the_second_global_is_set = }")  # the_second_global_is_set = True
    return 0


# getting the filepath from the cli here is too late, and therefore initialization goes wrong
print("Now setting filepath for WronglyInitializedConfig")
config_filepath_from_cli(
    WronglyInitializedConfig, short_option="-w", long_option="--config_filepath_w"
)

main()
