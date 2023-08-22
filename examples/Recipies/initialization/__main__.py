"""Example to demonstrate how to implement configurable module globals and class variables

Run this example with the following command:
python ./__main__.py -c ./the_config.toml -w ./the_config.toml
"""

# the next module is placed at the top of the entry point but that does not help
from modules.wrongly_initialized_config import WronglyInitializedConfig  # isort:skip

# the next module contains configured class variables and configured module globals
from modules.my_dataclass import MyDataclass, the_first_global, the_second_global

from application_settings import config_filepath_from_cli


def main() -> int:
    """print an instance of my_dataclass and all globals"""
    print("In main()")
    # properly configured variables are initialized to 1.0 and not to 0.0
    print(MyDataclass())  # MyDataclass(the_first_classvar=0.0, the_second_classvar=1.0)
    print(f"{the_first_global = }")  # the_first_global = 0.0
    print(f"{the_second_global = }")  # the_second_global = 1.0
    return 0


config_filepath_from_cli(
    WronglyInitializedConfig, short_option="-w", long_option="--config_filepath_w"
)
print("Now loading WronglyInitializedConfig")
WronglyInitializedConfig.load()

main()
