from pydantic import SecretStr

from envbase import EnvBase


class RedisConfig(EnvBase):
    """Reads REDIS_CONFIG_URI, REDIS_CONFIG_PORT and REDIS_CONFIG_SSL."""

    uri: str = "localhost"
    port: int = 9010
    ssl: bool = False


class Postgres(EnvBase):
    """Reads PG_HOST and PG_PASSWORD."""

    host: str = "localhost"
    password: SecretStr = SecretStr("")

    _prefix = "pg"


if __name__ == "__main__":
    print(RedisConfig.file(), RedisConfig().dump())
    print(Postgres.file(), Postgres().json())
