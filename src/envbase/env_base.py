"""
EnvBase is a pydantic settings model with class name prefixes and
per environment dotenv files.
"""

from os import environ
from pathlib import Path
from re import sub
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


def snake(name: str) -> str:
    """
    Converts a class name to snake case, keeping acronyms together.
    """
    return sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


class EnvBase(BaseSettings):
    """
    Settings read from the environment and a dotenv file.

    Each field reads the variable PREFIX_FIELD, where the prefix is the
    snake case class name (RedisConfig.uri reads REDIS_CONFIG_URI) or
    _prefix when set (_prefix = "redis" reads REDIS_URI). An empty
    _prefix reads bare field names.

    The dotenv file is .env in the _resources directory, or
    .env.{name} when the variable named by _variable holds a name.
    Keyword arguments win over the environment, the environment wins
    over the file, and the file wins over defaults.
    """

    model_config = SettingsConfigDict(
        extra="ignore",
        env_nested_delimiter="__",
    )

    _prefix: str | None = None
    _resources: str = "./resources"
    _variable: str = "EXECUTION_ENVIRONMENT"

    def __init__(self, **values: Any) -> None:
        values.setdefault("_env_prefix", type(self).prefix())
        values.setdefault("_env_file", type(self).file())
        super().__init__(**values)

    @classmethod
    def option(cls, name: str) -> Any:
        """
        Returns the class level value of an underscore option.
        """
        return cls.__private_attributes__[name].default

    @classmethod
    def prefix(cls) -> str:
        """
        Returns the variable prefix, with its trailing underscore.
        """
        prefix = cls.option("_prefix")
        if prefix is None:
            prefix = snake(cls.__name__)
        return f"{prefix.upper()}_" if prefix else ""

    @classmethod
    def file(cls) -> Path:
        """
        Returns the dotenv file for the current execution environment.
        """
        name = environ.get(cls.option("_variable"))
        resources = Path(cls.option("_resources"))
        return resources / (f".env.{name}" if name else ".env")

    def dump(self, **options: Any) -> dict[str, Any]:
        """
        Returns the fields as a dictionary of python values.
        """
        return self.model_dump(**options)

    def json(self, **options: Any) -> dict[str, Any]:
        """
        Returns the fields as a dictionary of json safe values.
        """
        return self.model_dump(mode="json", **options)
