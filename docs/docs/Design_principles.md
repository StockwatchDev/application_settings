# Design principles

`application_settings` is deliberately small. This chapter describes the principles that
it is built on.

## Purpose and priorities

The parameters of an application are an API, and this package is a means to deliver a
high quality one. There are two audiences, and each has its own kind of parameters:

- **Config** is the API for _deployment_: it is used by whoever installs and operates the
  application, and it deals with deployment concerns such as locations, endpoints,
  credentials and logging.
- **Settings** are the API for the _end user_: they deal with preferences and use case
  concerns, and they are usually changed through a user interface.

The package serves these purposes, in order of priority:

1. Deliver a high quality API for application deployment.
2. Make it effective to create a high quality API for deployment and for use case
   concerns, with one way of declaring both. This holds for applications and for
   libraries alike.
3. Deliver a high quality API for use case concerns. This has the lowest priority,
   because it is often a front end matter: the front end decides how a preference is
   shown, validated and reacted to, and the package only has to load and save it.

When concerns conflict, the higher priority wins. A convenience for settings is not
offered if it weakens a guarantee that config gives to a deployment.

The package is meant to be developer-friendly for the deployment concerns of libraries
as well as of applications. A library declares the parameters that it needs as a typed
section, and whoever deploys the application sets them in the config file of the
application, in one place, without the library choosing a file format or a location
(see [Usage in a library package](./5-Usage_in_a_library_package.md)).

Config is delivered as a file. That suits deployments, for instance with infrastructure
as code, in which tooling renders or mounts that file, and in which the file refers to
secrets instead of containing them. A deployment that can only set environment variables
is served better by a package that starts from the environment (see
[How this differs from pydantic-settings](#how-this-differs-from-pydantic-settings)).

## The principles

The column Priority refers to the numbered purposes in
[Purpose and priorities](#purpose-and-priorities); "all" means that the principle
serves every one of them.

| Principle                                                                                 | Priority | In short                                                                                     | What it means for the package                                                                                       |
| ----------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [P1. The dataclass is the schema](#p1-the-dataclass-is-the-schema)                        | 2        | Parameters are declared once, as typed dataclasses, documented in place.                     | Features attach to fields and their types, not to a second description of the parameters.                           |
| [P2. Config is not settings](#p2-config-is-not-settings)                                  | all      | Config is edited by people and is read-only. Settings are written by the application.        | Every feature is decided per kind. A feature that makes no sense for the other kind is not offered for it.          |
| [P3. The file is in charge](#p3-the-file-is-in-charge)                                    | 1        | Values are in the file. If a value comes from elsewhere, the file says so explicitly.        | No lookup by naming convention. The origin of a value is visible where the parameter is set.                        |
| [P4. Zero-conf by default, strict on request](#p4-zero-conf-by-default-strict-on-request) | 1, 2     | Defaults make the application work. Deviations are reported; `strict_mode` makes them fatal. | A new check logs by default and raises in strict mode. A feature must not make a default setup fail.                |
| [P5. Access by class](#p5-access-by-class)                                                | 2        | `MyConfig.get()` works from any module. Sections can be used without a container.            | One singleton per class, no objects to pass around. A library can define parameters without choosing a file format. |
| [P6. Secrets stay secret](#p6-secrets-stay-secret)                                        | 1        | Secrets are masked in output, logs and errors, and are never written by the package.         | A feature that handles values must keep this true. The weaker cases are reported, or refused in strict mode.        |
| [P7. Load once, then immutable](#p7-load-once-then-immutable)                             | 1        | Parameters are parsed up front and are frozen. A change needs an explicit reload.            | No watchers and no mutation of what was loaded. Code may assume that a value does not change.                       |
| [P8. No global side effects](#p8-no-global-side-effects)                                  | 2        | Loading does not change the process, so the package is safe to use inside a library.         | The environment is not modified, logging is left to the application, and the real environment wins over files.      |
| [P9. Delegate to proven libraries](#p9-delegate-to-proven-libraries)                      | all      | pydantic validates, coerces and masks; tomlkit, json and python-dotenv do the reading.       | A thin layer over a library is preferred to a reimplementation. A new dependency must be small and worth it.        |

## Background

### P1. The dataclass is the schema

A parameter is defined by one thing: a field in a dataclass, with a type, a default and a
docstring. That one declaration is the API for the deployer and for the end user alike:
the IDE completes it, mypy checks it, pydantic validates it and the documentation can be
generated from it. There is no separate schema, descriptor, decorator per field, or
registry to keep in sync, and config and settings are declared in the same way.

For example, secrets are a type, `Secret[str]`, not a flag like `secret=True`. The type
is then visible to the static checker and to every part of the package that looks at the
annotation.

### P2. Config is not settings

The two kinds of parameters are the API for two different audiences, with different
owners and lifecycles:

- **Config** is the API for deployment. It is chosen by whoever deploys the application,
  it is edited by hand, it may be kept in version control, and the package never writes
  to it. TOML is the default format because it is made for people to read and edit, and
  comments survive because the package never rewrites the file.
- **Settings** are the API for the end user. They are changed by the application,
  usually via its user interface, and are saved by the package. JSON is the default
  format because it is made for machines.

Config has the higher priority (see [Purpose and priorities](#purpose-and-priorities)),
which is why most features are for config.

The kind is part of the type (`ConfigBase`, `SettingsBase`), not a flag, so a feature
can be offered for one kind only, and the type checker knows which it is. References,
file inclusion and secrets are for config only: settings are saved to file, and a
secret or a reference must never end up there.

### P3. The file is in charge

If a value comes from an environment variable or from a file such as a Docker secret,
the config file says so, with a reference like `${env:NAME}` or `${secret:NAME}`. You can
read a config file and see all the external inputs of an application, and a parameter
cannot be changed from the outside by accident because its name matches a variable.

This has shaped the rules of references: a reference must be the whole value, `$${`
escapes it, a default is written in the reference, and a secret name can never be a
path. `__include__` takes a literal path and not a reference, for the same reason: what
is read must be plain to see. Implicit conventions, such as mapping every parameter to
an environment variable by its name, would need a design that respects this principle.

### P4. Zero-conf by default, strict on request

An application should start with sensible defaults when there is no file, when a section
is missing or when a file has unknown entries. These deviations are logged: quietly by
default, and at warning level when `strict_mode` is set. Production setups can then turn
on strict mode and fail early.

An error that is always raised is reserved for things that cannot work, such as an
invalid include path, a reference that cannot be resolved without a default, or a
circular include.

### P5. Access by class

`MyConfig.get()` or `MySection.get()` can be called in any module, without passing
objects around. The result is a singleton per class that is created when it is first
needed.

This also makes the package usable inside a library. A library defines its parameters in
a section and uses `get()`. The application either contains that section in its own
container, or hands the library a dictionary with `set()`. The library never has to
decide on a file format or a location.

### P6. Secrets stay secret

A value that is declared as `Secret` is masked in `repr`, logs and validation errors.
Errors keep the location and the type of the problem, but not the input. Messages name
parameters and never show values, also not defaults. A secret that does not come from a
secrets store is reported, because the point of a secret is that it is not in the config
file or the code. Secrets are not allowed in settings, because settings are saved.

How a secret gets into the deployment is for the deployer to decide, for instance with a
secrets store that the platform exposes as files or environment variables. The developer
only has to load it and keep it masked.

Where the package cannot be certain, it shows less. For example, in a config that has
secrets, only plain values of non-secret parameters are shown in validation errors.
Limits that remain, such as the origin check not covering the elements of a list, are
written down in the documentation instead of left for the user to find.

### P7. Load once, then immutable

Parameters are parsed and validated when they are loaded, and the result is a frozen
dataclass. After that, the values do not change. Environment variables, dotenv files and
secret files are read at load time as well. To pick up a change, call `load()` or
restart the application. Settings are changed with `update()`, which creates a new
instance and saves it.

This keeps the model simple: no code has to ask whether a value is still current. A
feature that needs live values, such as a file watcher, does not fit the model and has to
be built on top of it.

### P8. No global side effects

Loading a config reads files and the environment, and that is all. A dotenv file does
not change `os.environ`, and a real environment variable wins over the value in a dotenv
file. Logging uses the standard `logging` module with a `NullHandler`, so the
application decides what is shown. Because loading is free of side effects, the package
can be used inside a library without surprising the application that uses it.

### P9. Delegate to proven libraries

The package adds the logic that is specific to configuration: files, kinds, singletons,
references. Everything else is left to libraries that do it well:

- pydantic validates, coerces, offers types such as `FilePath` and `Secret`, and
  reports errors. `Secret` and `ValidationError` are exported as they are.
- tomlkit and the standard `json` module read and write the files.
- python-dotenv reads dotenv files, with variable expansion switched off, so that a
  value is always taken as written.

When a requirement can be met by a pydantic type or constraint, the documentation shows
how to use it instead of the package building it (see
[Handling deviations](./6-Handling_deviations.md)).

## What this means for new features

When a feature is proposed, or when you implement one, check it against these questions:

0. Which of the three priorities does it serve? Does it weaken a higher one?
1. Can it be a field type or a pydantic constraint? Then use that (P1, P9).
2. For which kind is it, config or settings? Does it fit that kind (P2)?
3. Is the origin of every value visible in the file, or is the feature opt-in (P3)?
4. Does a setup without file or without the new option keep working? Is a deviation
   logged, and raised in strict mode (P4)?
5. Could it reveal or save a secret (P6)?
6. Does it keep objects immutable and loaded once (P7)?
7. Does it change the process, such as the environment or the logging configuration
   (P8)?
8. Does it add a dependency, and is that justified (P9)?

And for the implementation: write the tests first, keep the failure messages free of
values, and document the limits of the feature in the chapter that describes it.

Examples of things that are not provided, because they conflict with a principle:

- Writing config back to file (P2).
- Secrets in settings (P2, P6).
- Hot reload, such as a file watcher (P7). Reacting to a changed preference is a front
  end matter, which has the lowest priority for this package.
- Setting `os.environ` from a dotenv file (P8).

The package does not fetch secrets from a cloud secret manager either: that needs
credentials, network access and caching, and getting a secret into the deployment is a
task for the deployer, not for the developer. A store such as Azure Key Vault is used
through the platform, which delivers the secrets as files or environment variables (see
[Environment variables and secrets](./8-Secrets.md)).

## How this differs from pydantic-settings

[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) is the
best known package for this purpose and it is built on pydantic as well. The two overlap,
but they start from different places. The comparison was verified against
pydantic-settings 2.16.2 (with pydantic 2.14.3), by reading its source and by running it.

| Aspect                  | application_settings                                                                                                            | pydantic-settings                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Starting point          | A file (TOML or JSON) that you write                                                                                            | The environment: a `BaseSettings` class is filled from environment variables first                                           |
| Other sources           | Included files, and explicit references to environment variables and secret files                                               | Dotenv files, a secrets directory, command line, cloud secret managers, and TOML, YAML and JSON files through source classes |
| Precedence              | Fixed and explicit: file, included files, references                                                                            | An ordered tuple of sources, which you can change with `settings_customise_sources`                                          |
| Naming                  | Names in the file are the parameter names                                                                                       | Environment variable names follow conventions such as `env_prefix` and `env_nested_delimiter`                                |
| Config versus settings  | Two kinds: read-only config, and read-write settings that are saved                                                             | One kind: values are loaded, and nothing is saved                                                                            |
| Access                  | A singleton per class, `MyConfig.get()`                                                                                         | An instance that you create and pass around, or cache                                                                        |
| Use in a library        | Sections without a container, parametrized by the application                                                                   | Possible; each library reads its own environment variables                                                                   |
| Namespace for a library | Section name in the file, chosen by the application                                                                             | `env_prefix`, chosen by the library author; two libraries can collide                                                        |
| Secrets                 | `Secret[T]`, masked, with origin checks and a strict mode; the deployment delivers the values as environment variables or files | `secrets_dir` and cloud managers as sources; masking through pydantic's `SecretStr`                                          |

Choose application_settings when you want parameters in a file that people edit, with a
clear separation between config that is edited and settings that the application saves,
when you want to parametrize a library, when your deployment tooling delivers the
configuration as a file, or when you want the file to show where each value comes from.

It is not a fit when the environment is the main source of your configuration
(twelve-factor style applications), or when you need flexibility and want to compose
your own sources.
