# pylint: disable=missing-module-docstring
from .config_example import ExampleInitConfig

test_global: float = ExampleInitConfig.get().field0
