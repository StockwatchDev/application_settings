"""Config with secrets, whose values come from environment variables and files"""

from application_settings import ConfigBase, ConfigSectionBase, Secret, dataclass


@dataclass(frozen=True)
class DatabaseSection(ConfigSectionBase):
    """Config section for the database"""

    # a parameter without a default value must be given in the config file
    password: Secret[str]
    host: str = "localhost"


@dataclass(frozen=True)
class SecretsExampleConfig(ConfigBase):
    """Config for the example"""

    # parameters without a default value come first
    api_key: Secret[str]
    database: DatabaseSection
    name: str = "secrets example"
    port: int = 8080
