# Defining parameters

This package lets you define parameters for configuration and settings. The difference
between configuration and settings is as follows. `Config` is for parameters that do not
change during runtime and are read from file. `Settings` are parameters that can change
programmatically during runtime and are read from and saved to file for persistancy over
sessions. During definition, they differ only in terms of the base classes that are used.

The intended structure is that parameters are defined in section classes. Sections can be
nested. There should be one special root section for the application, referred to as the
container, that handles file storage. Config sections and Settings sections should never
be mixed (i.e., do not nest a Settings section in a Config section and vice versa).

## Defining non-container section(s)

A section is defined by subclassing the relevant base class (`ConfigSectionBase` for
config, `SettingsSectionBase` for settings) and decorating it with
`@dataclass(frozen=True)`. Parameters are defined as fields of the dataclass. For a
dataclass, it is mandatory to add a type hint for each field. These type hints are used
also to validate the data that is read from the parameter file. If you
specify a default value as well, then you prevent the occurance of an exception if the
value for the parameter of concern is not found in the parameter file.

The `dataclass` decorator provided by `application_settings` is actually an exported
[`pydantic.dataclasses.dataclass`](https://docs.pydantic.dev/usage/dataclasses/), which
is a drop-in replacement for a `dataclass` from the standard python library, enhanced
with data validation. If you need additional dataclass functionality such as `fields`
etc., you can import those from the standard library.

Nested sections are obtained by defining fields in a section that are type hinted with
the appropriate contained section class(es) and instantiated (possible only when all
parameters of the nested section have default values).

## Defining the container

The container is a special section that is to be the root for parametrisation of an
application. It is defined likewise: by subclassing the relevant base class (`ConfigBase`
for config, `SettingsBase` for settings), decorating it with `@dataclass(frozen=True)`,
defining fields for parameters and nested non-root sections.

Note that albeit settings can be changed programmatically, we still set `frozen=True` for
the settings container and -sections (see also the example section below).

## Parameter docstrings

The python standard states that class variables are to be documented in the docstring of the containing class.
[PEP 224](https://peps.python.org/pep-0224/) proposed to enable inline documentation of class attributes, namely
by having a docstring appear directly after an attribute definition (analogous to how it's done for e.g. a class
definition). This PEP was rejected. However, IDE's such as VSCode do know how to handle this documentation style.
Moreover, the package [`attributes-doc`](https://pypi.org/project/attributes-doc/) provides the functionality to add
the docstring literals to the objects in question such that introspection tools can make use of it. This is achieved
by means of a decorator `@attributes_doc` for the class that defines the attributes. Our package `application_settings`
exports this decorator to facilitate documentation and introspection.


## Example

=== "Configuration"
    ```python
    from application_settings import ConfigBase, ConfigSectionBase, attributes_doc, dataclass

    @attributes_doc
    @dataclass(frozen=True)
    class MyExampleConfigSection(ConfigSectionBase):
        """Config section for an example"""

        field1: float = 0.5
        """Docstring for the first field; defaults to 0.5"""

        field2: int = 2
        """Docstring for the second field; defaults to 2"""


    @attributes_doc
    @dataclass(frozen=True)
    class MyExampleConfig(ConfigBase):
        """Config for an example"""

        name: str = "nice example"
        """With this parameter you can configure the name; defaults to 'nice example'"""

        section1: MyExampleConfigSection = MyExampleConfigSection()
        """Holds the configuration parameters for the first section"""

    ```

=== "Settings"
    ```python
    from application_settings import SettingsBase, SettingsSectionBase, attributes_doc, dataclass

    @attributes_doc
    @dataclass(frozen=True)
    class BasicSettingsSection(SettingsSectionBase):
        """Settings section for the basics"""

        totals: int = 2
        """The totals value; defaults to 2"""


    @attributes_doc
    @dataclass(frozen=True)
    class MyExampleSettings(SettingsBase):
        """Settings for an example"""

        name: str = "nice name"
        """This parameter holds the name setting; defaults to 'nice name'"""

        basics: BasicSettingsSection = BasicSettingsSection()
        """Holds the setting parameters for the basic section"""


    ```
