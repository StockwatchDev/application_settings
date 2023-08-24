"""Module with two configurable class variables and two configurable module globals

Configuration has been done such that the_first_classvar and the_first_global will be
initialized with the default value (0.0) and not with the configured value (1.0);
the_second_classvar and the_second_global will be initialized correctly with the
configured value (1.0).
"""

from dataclasses import dataclass

from modules.correctly_initialized_config import CorrectlyInitializedConfig
from modules.wrongly_initialized_config import WronglyInitializedConfig


@dataclass
class MyDataclass:
    the_first_classvar: float = WronglyInitializedConfig.get().initial_value
    the_second_classvar: float = CorrectlyInitializedConfig.get().initial_value


print("Now initializing the module globals")
the_first_global = WronglyInitializedConfig.get().initial_value
the_second_global = CorrectlyInitializedConfig.get().initial_value
