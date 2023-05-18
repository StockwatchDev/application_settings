"""Example for settings."""
from pathlib import Path

from pydantic.dataclasses import dataclass

from application_settings import SettingsBase, SettingsSectionBase


@dataclass(frozen=True)
class BasicSettingsSection(SettingsSectionBase):
    """Settings section for the basics"""

    totals: int = 2


@dataclass(frozen=True)
class MyExampleSettings(SettingsBase):
    """Settings for an example"""

    name: str = "nice name"
    basics: BasicSettingsSection = BasicSettingsSection()


def main1() -> None:
    """example how to use the module application_settings"""
    # One of the first things to do in an application is loading the parameters
    MyExampleSettings.load()
    # Now you can access parameters via get()
    # If you get() MyExampleSettings before load(), it will be loaded automatically
    a_variable = MyExampleSettings.get().name
    print(f"a_variable == '{a_variable}'")  # a_variable == 'the stored name'
    # You can also directly get() a section; but remember that the settings should
    # be loaded already then (get() on a section does not automatically load())
    another_variable = BasicSettingsSection.get().totals
    print(f"another_variable == {another_variable}")  # another_variable == 3

    # You can update the settings:
    MyExampleSettings.update({"basics": {"totals": 33}})
    # The updated values will be written to the settings file automatically and the
    # singleton is replaced by a new instance of MyExampleSettings with the updated values
    refreshed_totals = BasicSettingsSection.get().totals
    print(f"refreshed_totals == {refreshed_totals}")  # refreshed_totals == 33


def main2() -> None:
    """continued example how to use the module application_settings"""
    # You can also edit the settings file. Suppose that we changed the value for name to
    # "updated name"

    # You can reload a setting
    MyExampleSettings.load()
    refreshed_name = MyExampleSettings.get().name
    print(f"refreshed_name == '{refreshed_name}'")  # refreshed_name == 'updated name'


if __name__ == "__main__":
    # Set the filepath to the default filename, but then in the local folder
    local_filepath = (
        Path(__file__).parent.absolute() / MyExampleSettings.default_filename()
    )
    MyExampleSettings.set_filepath(local_filepath)

    main1()

    # Edit the config file
    with local_filepath.open("r") as file:
        filedata = file.read()
    filedata = filedata.replace('"the stored name"', '"updated name"')
    with local_filepath.open("w") as file:
        file.write(filedata)

    main2()

    # Restore the original config file
    with local_filepath.open("r") as file:
        filedata = file.read()
    filedata = filedata.replace('"updated name"', '"the stored name"')
    filedata = filedata.replace("33", "3")
    with local_filepath.open("w") as file:
        file.write(filedata)
