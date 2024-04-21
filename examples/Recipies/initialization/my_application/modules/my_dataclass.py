"""Module with two configurable class variables and two configurable module globals

Configuration has been done such that the_first_classvar_is_set and the_first_global will be
initialized with the default value (0.0) and not with the configured value (1.0);
the_second_classvar_is_set and the_second_global will be initialized correctly with the
configured value (1.0).
"""

from dataclasses import dataclass

from modules.correctly_initialized_config import CorrectlyInitializedConfig
from modules.wrongly_initialized_config import WronglyInitializedConfig


@dataclass
class MyDataclass:
    """Example of class with classvars that are configured"""

    the_first_classvar_is_set = WronglyInitializedConfig.get().configvar_is_set
    the_second_classvar_is_set = CorrectlyInitializedConfig.get().configvar_is_set


print("Now initializing the module globals")
the_first_global_is_set = WronglyInitializedConfig.get().configvar_is_set
the_second_global_is_set = CorrectlyInitializedConfig.get().configvar_is_set
