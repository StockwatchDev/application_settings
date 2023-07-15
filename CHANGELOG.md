# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Check for presence of the dataclass decorator
  (Issue [#76](https://github.com/StockwatchDev/application_settings/issues/76))
- Enable file inclusion for toml config files
  (Issue [#67](https://github.com/StockwatchDev/application_settings/issues/67))

### Changed

- pydantic.dataclasses.dataclass and pydantic.ValidationError now exported from our
  namespace (Issue [#36](https://github.com/StockwatchDev/application_settings/issues/36))
- Exceptions added to docstrings (Issue 
  [#16](https://github.com/StockwatchDev/application_settings/issues/16))
- Upgraded pydantic to version 2.0, which has a different way of doing type conversion,
  see the [conversion table](https://docs.pydantic.dev/2.0/usage/conversion_table/)
  (Issue [#75](https://github.com/StockwatchDev/application_settings/issues/75))

### Fixed

## [0.3.0] - 2023-06-21

### Added

- Multiple versions of documentation served on Github Pages.
- You can now request a (re-) load when setting the filepath or via a method `load`.
- You can choose whether or not to throw a `FileNotFoundError` during `load`
  when the parameter file is not found in the expected location
  (Issue [#51](https://github.com/StockwatchDev/application_settings/issues/51))
- Support for parameters in the main container (Issue
  [#20](https://github.com/StockwatchDev/application_settings/issues/20)).
- Support for subsections (arbitrary depth) (Issue
  [#5](https://github.com/StockwatchDev/application_settings/issues/5)).
- Sections also stored as a singleton, so that libs can define and access parameters
  via their own Section (Issue 
  [#46](https://github.com/StockwatchDev/application_settings/issues/46)).
- Literal SectionTypeStr exported.
- Convenience functions to specify filepath for config and settings via command-line
  [[#53](https://github.com/StockwatchDev/application_settings/issues/53)]

### Changed

- The method `update` now is a class method (breaking).
- You cannot request a reload via method `get` anymore, use separate method `load`
  (breaking).
- A Container now is a specialization of a ContainerSection.

### Fixed

- Default folder name no longer just a dot if container class is called Config or
  Settings.

## [0.2.0] - 2023-03-19

### Added

- Files can be formatted as `toml` or `json`.
- Introduced settings, i.e., read-write parameters (where config is read-only).
- Now also useable with python 3.9.
- Documentation extended and served on Github Pages.

### Changed

- File path for config / settings now via `set_filepath()` and no longer as argument of
  `get()`.

## [0.1.0] - 2023-02-13

### Added 

- Loading a `toml` file.
- Initializing a dataclass with the loaded toml and storing it as a singleton.
- Default path, folder and file name.
- Specification of a config file path via argument of `get()`.
- Validation using pydantic.
- README that explains it all.

[//]: # (Header for a release: ## [1.1.0] - 2019-02-15)

[//]: # (Sections: Added / Changed / Deprecated / Removed / Fixed)
