# Environment variables and secrets

A config file is often not the right place for every value. A password or an API key
should not be committed with the rest of the config, and some values differ per
environment. For this purpose, the value of a config parameter can be a _reference_ to an
environment variable or to a file, and a parameter can be declared to be a _secret_.

This is only available for config (and config sections), not for settings: settings are
written back to file, and a secret should never end up there.

A complete example is available in the folder
[`examples/recipes/secrets`](https://github.com/StockwatchDev/application_settings/tree/develop/examples/recipes/secrets).

## References

A reference is a value in the config file that has one of the following forms:

| Reference                     | Value                                                          |
| ----------------------------- | -------------------------------------------------------------- |
| `${env:VAR_NAME}`             | the value of the environment variable `VAR_NAME`               |
| `${env:VAR_NAME,default}`     | the same, but if `VAR_NAME` is not set, then `default` is used |
| `${secret:file_name}`         | the content of the file `file_name` in the secrets folder      |
| `${secret:file_name,default}` | the same, but if the file is not found, then `default` is used |

```toml
name = "${env:MYAPP_NAME,my application}"
port = "${env:MYAPP_PORT,8080}"

[database]
password = "${secret:db_password}"
```

The following rules apply:

- The reference has to be the _whole_ value. A value like `"prefix-${env:VAR_NAME}"` is taken
  literally, as is a value that is not closed (`"${env:VAR_NAME"`).
- A value that starts with `$${` is taken literally, without the first `$`. Hence, to get
  the text `${env:VAR_NAME}` as a value, write `"$${env:VAR_NAME}"`.
- A name (of an environment variable or of a file in the secrets folder) consists of
  letters, digits, `_`, `-` and `.`; the names `.` and `..` are not allowed. The rule is
  the same for both and deliberately not stricter, because the platform that provides the
  variables and files may use names beyond the portable `A-Z`, `a-z`, `0-9` and `_`. A
  name that does not exist is reported as not found.
- Only the schemes `env` and `secret` exist. A value of the form `${...}` that is not a
  valid reference to one of them is an error: this holds for an unknown scheme
  (`${other:name}`), a missing scheme (`${name}`) and an empty or invalid name
  (`${env:}`).
- The default is everything after the first comma, as is: spaces are part of it, and a
  reference in it is not resolved but taken literally, so `${env:A,${env:B}}` gives
  the text `${env:B}` when `A` is not set. It can be empty: `${env:VAR_NAME,}`.
- A reference works for any parameter. The value that is found is always a string. It is
  converted to the type of the parameter in the same way as any value from the file, e.g.
  `"5"` becomes `5` for an `int` parameter; `strict_mode` does not change this. Hence, a
  reference cannot provide a list or a table: loading then fails with a validation error.
- References work in every part of a config file, also in included files, except
  in the section `application_config`.
- References are resolved when the config is loaded.
- A reference is not a file inclusion: `${secret:file_name}` reads a single value from a file
  in the secrets folder, whereas [`__include__`](3-files.md) merges a whole config file.
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
in a folder like `/run/secrets`. A reference `${secret:file_name}` reads the file `file_name` in the
folder that is set by `secrets_dir` in the section `application_config`.

```toml
[application_config]
secrets_dir = "/run/secrets"
```

- A relative path is relative to the folder of the config file.
- The file is read as UTF-8 and a single trailing newline is removed. Other whitespace is
  kept.
- `file_name` is the name of a file and can never be a path: it is not possible to
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

- The value is converted to `T` as for any other parameter, e.g. `Secret[int]` gives an
  `int`, and is then wrapped in a `Secret`.
- The value is hidden when the config is printed or logged: you see `Secret('**********')`.
  The value has to be asked for explicitly with `get_secret_value()`.
- If the config is not valid, the error does not show secret values. The error still
  names the parameter and says what is wrong, but not its input when that is a
  `Secret`. For other parameters, only plain values (text, numbers, booleans) are shown,
  because a list or a table could hold a secret, and pydantic reports all arguments
  for errors like a missing parameter.
- `Secret` is not available in settings. Loading a settings class that has a `Secret`
  raises a `TypeError`.
- The default value of a secret has to be a `Secret` as well, e.g. `Secret("x")`.

### Secrets that do not come from a reference

The point of a secret is that its value is not in the config file or in the code. Hence,
when the value of a secret is not found by a reference, that is reported. This is the
case if the value comes from

- a default value in the code,
- the default in a reference, e.g. `${env:VAR_NAME,default}`, that was used because `VAR_NAME`
  was not found, or
- a literal in the config file, e.g. `api_key = "abc"`.

By default, a warning is logged that names the parameter (never its value). In strict mode
(set `strict_mode = true` in the section `application_config`), a `SecretsError` is raised
instead, which lists all such parameters; the config that was loaded previously, if any,
is not replaced in that case. Use strict mode in production: a misconfigured deployment
then fails at startup instead of silently running with a default or literal secret.

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
    `${secret:file_name}`. Files are preferred, because environment variables can be seen with
    `docker inspect`.

=== "Kubernetes"
    A `Secret` can be exposed to a container as an environment variable (`secretKeyRef`)
    or as files in a mounted volume. Use `${env:VAR_NAME}`, or mount the volume and use
    `${secret:file_name}` with `secrets_dir` set to the mount path. Note that a Kubernetes
    `Secret` is only base64 encoded; it needs encryption at rest or an external store
    (e.g., by the External Secrets Operator or the Secrets Store CSI Driver) to be
    safe.

=== "CI"
    Pass the secrets of the CI system as environment variables to the job and use
    `${env:VAR_NAME}`.

## Good to know

- Values are read when the config is loaded and do not change afterwards. To pick up a
  changed secret, load the config again.
- A dotenv file is not encrypted. It is intended for development, do not commit one with
  real secrets.
- The check on the origin of secrets is done for parameters that are annotated with
  `Secret[...]` or `Secret[...] | None`, also in nested sections. An optional secret that
  is `None` is not reported, because there is no value to protect. The check is not done
  for a `Secret` inside another union or inside a container, like `list[Secret[int]]`.
  Such a parameter is still hidden in errors and is still not allowed in settings.
