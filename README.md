[![CI Status][ci-shield]][ci-url]
[![Coverage][coverage-shield]][coverage-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

# Envbase

Pydantic settings with class name prefixes and per environment dotenv
files.

```
pip install envbase
```

## Usage

```python
from envbase import EnvBase

class RedisConfig(EnvBase):
    uri: str = "localhost"
    port: int = 9010
    ssl: bool = False

config = RedisConfig()
config.uri        # REDIS_CONFIG_URI, else resources/.env, else "localhost"
config.dump()     # {"uri": "localhost", "port": 9010, "ssl": False}
config.json()     # same, json safe values (secrets masked, paths as strings)
```

## Prefixes

Each field reads `PREFIX_FIELD`. The prefix is the snake case class name
unless `_prefix` is set. Matching is case insensitive.

| Class                           | `uri` reads        |
|---------------------------------|--------------------|
| `class RedisConfig(EnvBase)`    | `REDIS_CONFIG_URI` |
| `class HTTPServer(EnvBase)`     | `HTTP_SERVER_URI`  |
| `_prefix = "redis"`             | `REDIS_URI`        |
| `_prefix = ""`                  | `URI`              |

Nested models read `PREFIX_FIELD__SUBFIELD`. Subclasses inherit `_prefix`.

## Files

Values are loaded from a dotenv file in the resources directory:

| `EXECUTION_ENVIRONMENT` | File                     |
|-------------------------|--------------------------|
| unset                   | `./resources/.env`       |
| `prod`                  | `./resources/.env.prod`  |

A missing file is skipped. Keys in the file that belong to other classes
are ignored, so one file can hold every class's settings.

Precedence, highest first: keyword arguments, environment variables, the
dotenv file, field defaults.

## Options

```python
class RedisConfig(EnvBase):
    uri: str = "localhost"

    _prefix = "redis"               # default: snake case class name
    _resources = "./config"         # default: ./resources (relative to cwd)
    _variable = "STAGE"             # default: EXECUTION_ENVIRONMENT
```

`RedisConfig.prefix()` and `RedisConfig.file()` show what a class resolves
to. Everything else is plain pydantic settings: validators, `SecretStr`,
`model_config`, and the `_env_file` keyword all work as usual.

## Tests

```
pytest --cov
```

[ci-shield]: https://img.shields.io/github/actions/workflow/status/parkermmr/envbase/ci.yml?branch=main&style=for-the-badge&label=CI
[ci-url]: https://github.com/parkermmr/envbase/actions/workflows/ci.yml
[coverage-shield]: https://img.shields.io/codecov/c/github/parkermmr/envbase?style=for-the-badge
[coverage-url]: https://codecov.io/gh/parkermmr/envbase
[contributors-shield]: https://img.shields.io/github/contributors/parkermmr/envbase.svg?style=for-the-badge
[contributors-url]: https://github.com/parkermmr/envbase/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/parkermmr/envbase.svg?style=for-the-badge
[forks-url]: https://github.com/parkermmr/envbase/network/members
[stars-shield]: https://img.shields.io/github/stars/parkermmr/envbase.svg?style=for-the-badge
[stars-url]: https://github.com/parkermmr/envbase/stargazers
[issues-shield]: https://img.shields.io/github/issues/parkermmr/envbase.svg?style=for-the-badge
[issues-url]: https://github.com/parkermmr/envbase/issues
