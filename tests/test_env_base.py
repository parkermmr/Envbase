from pathlib import Path

import pytest
from pydantic import SecretStr

from envbase import EnvBase
from envbase.env_base import snake


class RedisConfig(EnvBase):
    uri: str = "localhost"
    port: int = 9010
    ssl: bool = False


class Redis(EnvBase):
    uri: str = "localhost"
    port: int = 9010
    _prefix = "redis"


class Bare(EnvBase):
    uri: str = "localhost"
    _prefix = ""


class Custom(EnvBase):
    uri: str = "localhost"
    password: SecretStr = SecretStr("")
    path: Path = Path("/tmp")
    _prefix = "custom"
    _resources = "config"
    _variable = "STAGE"


@pytest.fixture(autouse=True)
def workspace(tmp_path, monkeypatch):
    for name in ("EXECUTION_ENVIRONMENT", "STAGE", "REDIS_URI", "REDIS_CONFIG_URI", "URI"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "resources").mkdir()
    return tmp_path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_snake():
    assert snake("RedisConfig") == "redis_config"
    assert snake("HTTPServer") == "http_server"
    assert snake("S3Store") == "s3_store"


def test_defaults():
    assert RedisConfig().dump() == {"uri": "localhost", "port": 9010, "ssl": False}


def test_class_name_prefix(monkeypatch):
    monkeypatch.setenv("REDIS_CONFIG_URI", "cache")
    monkeypatch.setenv("REDIS_CONFIG_PORT", "6379")
    monkeypatch.setenv("REDIS_CONFIG_SSL", "true")
    assert RedisConfig().dump() == {"uri": "cache", "port": 6379, "ssl": True}


def test_explicit_prefix(monkeypatch):
    monkeypatch.setenv("REDIS_URI", "cache")
    assert Redis().uri == "cache"
    assert RedisConfig().uri == "localhost"


def test_empty_prefix(monkeypatch):
    monkeypatch.setenv("URI", "cache")
    assert Bare().uri == "cache"


def test_default_file(workspace):
    write(workspace / "resources/.env", "REDIS_URI=fromfile\nOTHER_KEY=ignored\n")
    assert Redis().uri == "fromfile"


def test_environment_file(workspace, monkeypatch):
    write(workspace / "resources/.env", "REDIS_URI=base\n")
    write(workspace / "resources/.env.prod", "REDIS_URI=prod\n")
    monkeypatch.setenv("EXECUTION_ENVIRONMENT", "prod")
    assert Redis().uri == "prod"
    assert Redis.file() == Path("resources/.env.prod")


def test_missing_file(monkeypatch):
    monkeypatch.setenv("EXECUTION_ENVIRONMENT", "nowhere")
    assert Redis().uri == "localhost"


def test_precedence(workspace, monkeypatch):
    write(workspace / "resources/.env", "REDIS_URI=file\nREDIS_PORT=1\n")
    monkeypatch.setenv("REDIS_URI", "environ")
    assert Redis().dump() == {"uri": "environ", "port": 1}
    assert Redis(uri="keyword").uri == "keyword"


def test_custom_options(workspace, monkeypatch):
    write(workspace / "config/.env.dev", "CUSTOM_URI=dev\n")
    monkeypatch.setenv("STAGE", "dev")
    assert Custom().uri == "dev"
    assert Custom()._prefix == "custom"


def test_subclass_inherits_options(monkeypatch):
    class Replica(Redis):
        replicas: int = 1

    monkeypatch.setenv("REDIS_REPLICAS", "3")
    assert Replica().replicas == 3


def test_dump_and_json():
    config = Custom(password="secret")
    assert config.dump()["password"].get_secret_value() == "secret"
    assert config.dump()["path"] == Path("/tmp")
    assert config.json() == {"uri": "localhost", "password": "**********", "path": "/tmp"}
    assert config.json(include={"uri"}) == {"uri": "localhost"}
