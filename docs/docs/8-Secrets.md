# Environment variables and secrets

A config file is often not the right place for every value. A password or an API key
should not be committed with the rest of the config, and some values differ per
environment. For this purpose, the value of a config parameter can be a _reference_ to an
environment variable or to a file, and a parameter can be declared to be a _secret_.

This is only available for config (and config sections), not for settings: settings are
written back to file, and a secret should never end up there.

A complete example is available in the folder
[`examples/Recipies/secrets`](https://github.com/StockwatchDev/application_settings/tree/develop/examples/Recipies/secrets).

## References

A reference is a value in the config file that has one of the following forms:

| Reference                | Value                                                                 |
| ------------------------ | --------------------------------------------------------------------- |
| `${env:NAME}`            | the value of the environment variable `NAME`                          |
| `${env:NAME,default}`    | the same, but if `NAME` is not set, then `default` is used            |
| `${secret:NAME}`         | the content of the file `NAME` in the secrets folder                  |
| `${secret:NAME,default}` | the same, but if the file is not found, then `default` is used        |

```toml
name = "${env:MYAPP_NAME,my application}"
port = "${env:MYAPP_PORT,8080}"

[database]
password = "${secret:db_password}"
```

The following rules apply:

- The reference has to be the _whole_ value. A value like `"prefix-${env:NAME}"` is taken
  literally, as is a value that is not closed (`"${env:NAME"`).
- A value that starts with `$${` is taken literally, without the first `$`. Hence, to get
  the text `${env:NAME}` as a value, write `"$${env:NAME}"`.
- A name consists of letters, digits, `_`, `-` and `.`; the names `.` and `..` are not
  allowed. A value that looks like a reference but is not valid, like `${env:}` or
  `${other:NAME}`, is an error.
- The default is everything after the first comma, as is: spaces are part of it, and it
  cannot contain a reference. It can be empty: `${env:NAME,}`.
- A reference works for any parameter of any type. The value that is found is a string,
  which is converted to the type of the parameter, just like a value from the file is.
- References work in every part of a config file, also in included files, except
  in the section `application_config`.
- References are resolved when the config is loaded.
- A reference is not a file inclusion: `${secret:NAME}` reads a single value from a file
  in the secrets folder, whereas [`__include__`](3-Files.md) merges a whole config file.
  Includes are loaded before references are resolved, so the value of `__include__` must
  be a literal path; a value with `${` in it is an error.

If a reference cannot be resolved and has no default, then loading the config raises a
`ReferenceResolutionError`. Its message lists _all_ references that could not be
resolved, by parameter, and never shows values.

## Where the values come from

### Environment variables

Environment variables are looked up in the environment of the process. To make life easy
during development, they can also be read from a
[dotenv file](https://pypi.org/project/python-dotenv/) by setting `dotenv_file` in the
section `application_config`. A real environment variable takes precedence over a
variable in the dotenv file, and the dotenv file does not change the environment of the
process.

```toml
[application_config]
dotenv_file = ".env"
```

A relative path is relative to the folder of the config file. If the dotenv file does not
exist, then a warning is logged and the real environment is used. Values in a dotenv file
are taken as they are: there is no variable expansion.

### Files in the secrets folder

Platforms like Docker and Kubernetes can provide secrets as files, one file per secret,
in a folder like `/run/secrets`. A reference `${secret:NAME}` reads the file `NAME` in the
folder that is set by `secrets_dir` in the section `application_config`.

```toml
[application_config]
secrets_dir = "/run/secrets"
```

- A relative path is relative to the folder of the config file.
- The file is read as UTF-8 and a single trailing newline is removed. Other whitespace is
  kept.
- `NAME` is the name of a file and can never be a path: it is not possible to
  refer to a file outside the secrets folder.
- Symbolic links are followed, which is what Kubernetes uses to provide secrets.
- If `secrets_dir` is not set or the file is not found, then the default is used; without
  a default, this is an error. A file that exists but cannot be read is always an error.

The parameters `dotenv_file` and `secrets_dir` are both empty by default, which means
that they are not used. They are read before any reference is resolved; hence, they
cannot contain a reference themselves.

## Secrets

To prevent that a value is shown by accident, declare a parameter as `Secret`. This is
the [`Secret` of pydantic](https://docs.pydantic.dev/latest/api/types/#pydantic.types.Secret),
which is available from `application_settings` as well.

```python
from application_settings import ConfigBase, Secret, dataclass


@dataclass(frozen=True)
class MyConfig(ConfigBase):
    """Config for my application"""

    api_key: Secret[str]
    port: int = 8080
```

```toml
api_key = "${env:MYAPP_API_KEY}"
```

```python
api_key = MyConfig.get().api_key.get_secret_value()
```

Note that a parameter without a default value must come before the ones with a default
value, and that it has to be given in the config file.

- The value is converted to the type that is given, in the example a `str`; `Secret[int]`
  would convert the value to an `int`.
- The value is hidden when the config is printed or logged: you see `Secret('**********')`.
  The value has to be asked for explicitly with `get_secret_value()`.
- The value is also hidden in the error when it is not valid. The error still tells which
  parameter is wrong and why, but it does not show the input. The same holds for an
  error of another parameter in which pydantic would show all arguments, e.g. when a
  parameter is missing, because that would show the secrets as well. In fact, in a
  config that has secrets, only plain values (text, numbers, booleans) are shown in
  errors for other parameters; a list or a table is not.
- `Secret` is not available in settings. Loading a settings class that has a `Secret`
  raises a `TypeError`.
- The default value of a secret has to be a `Secret` as well, e.g. `Secret("x")`.

### Secrets that do not come from a reference

The point of a secret is that its value is not in the config file or in the code. Hence,
when the value of a secret is not found by a reference, that is reported. This is the
case if the value comes from

- a default value in the code,
- the default in a reference, e.g. `${env:NAME,default}`, that was used because `NAME`
  was not found, or
- a literal in the config file, e.g. `api_key = "abc"`.

By default, a warning is logged that names the parameter. In strict mode (set
`strict_mode = true` in the section `application_config`), a `SecretsError` is raised
instead, which lists all such parameters. The config that was loaded previously, if any,
is not replaced in that case.

Messages never contain the value of a secret.

## Setting this up on a platform

=== "Local development"
    Keep a dotenv file out of version control (add it to `.gitignore`) and refer to it
    from the config file:

    ```toml
    [application_config]
    dotenv_file = ".env"
    ```

    ```text
    # .env
    MYAPP_API_KEY=value-for-development
    ```

=== "Docker"
    Environment variables can be passed with `docker run -e NAME=value`, `--env-file`, or
    the `environment:` and `env_file:` keys of Docker Compose. Docker secrets are
    mounted as files in `/run/secrets`, so set that as the secrets folder and use
    `${secret:NAME}`. Files are preferred, because environment variables can be seen with
    `docker inspect`.

=== "Kubernetes"
    A `Secret` can be exposed to a container as an environment variable (`secretKeyRef`)
    or as files in a mounted volume. Use `${env:NAME}`, or mount the volume and use
    `${secret:NAME}` with `secrets_dir` set to the mount path. Note that a Kubernetes
    `Secret` is only base64 encoded; it needs encryption at rest or an external store
    (e.g., by the External Secrets Operator or the Secrets Store CSI Driver) to be
    safe.

=== "CI"
    Pass the secrets of the CI system as environment variables to the job and use
    `${env:NAME}`.

## Good to know

- Values are read when the config is loaded and do not change afterwards. To pick up a
  changed secret, load the config again.
- A dotenv file is not encrypted. It is intended for development, do not commit one with
  real secrets.
- The check on the origin of secrets is done for parameters that are annotated with
  `Secret[...]`, also in nested sections. It is not done for `Secret` inside a union
  like `Secret[int] | None` or inside a container like `list[Secret[int]]`.
