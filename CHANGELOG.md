# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2023-xx-yy

### Added

- Documentation extended and multiple versions served on Github Pages

### Changed

- The method `update` now is a class method (breaking).

## [0.2.0] - 2023-03-19

### Added

- Files can be formatted as `toml` or `json`.
- Introduced settings, i.e., read-write parameters (where config is read-only)
- Now also useable with python 3.9
- Documentation extended and served on Github Pages

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
