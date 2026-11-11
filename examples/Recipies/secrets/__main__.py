"""Example for references to environment variables and files, and for secrets.

Cd to the folder containing this file and run this example with the following command:
python .

A real environment variable takes precedence over a variable in example.env, try e.g.:
EXAMPLE_PORT=9090 python .
"""

from pathlib import Path

from app_config import SecretsExampleConfig


def main() -> None:
    """Load the config and show how to use the values"""
    SecretsExampleConfig.set_filepath(Path(__file__).parent / "config.toml")
    config = SecretsExampleConfig.load()

    # Secrets are masked when printed or logged
    print(config)

    # Other values are used as usual, they have the type of the parameter
    print(f"{config.name = }")
    print(f"{config.port = }")
    print(f"{config.database.host = }")

    # The value of a secret has to be asked for explicitly
    password = config.database.password.get_secret_value()
    print(f"The password has {len(password)} characters")


if __name__ == "__main__":
    main()
