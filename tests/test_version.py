# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from application_settings import __version__


def test_version() -> None:
    assert __version__ == "0.4.0.dev0"
