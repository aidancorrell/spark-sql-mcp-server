import pytest

from spark_sql_mcp.config import SparkConfig


def test_from_env_minimal(monkeypatch):
    monkeypatch.setenv("SPARK_HOST", "localhost")
    config = SparkConfig.from_env()
    assert config.host == "localhost"
    assert config.port == 10000
    assert config.database == "default"
    assert config.auth == "NONE"
    assert config.username is None
    assert config.password is None
    assert config.kerberos_service_name == "hive"


def test_from_env_full(monkeypatch):
    monkeypatch.setenv("SPARK_HOST", "emr-master.example.com")
    monkeypatch.setenv("SPARK_PORT", "10001")
    monkeypatch.setenv("SPARK_DATABASE", "analytics")
    monkeypatch.setenv("SPARK_AUTH", "LDAP")
    monkeypatch.setenv("SPARK_USERNAME", "admin")
    monkeypatch.setenv("SPARK_PASSWORD", "secret")
    monkeypatch.setenv("SPARK_KERBEROS_SERVICE_NAME", "spark")

    config = SparkConfig.from_env()
    assert config.host == "emr-master.example.com"
    assert config.port == 10001
    assert config.database == "analytics"
    assert config.auth == "LDAP"
    assert config.username == "admin"
    assert config.password == "secret"
    assert config.kerberos_service_name == "spark"


def test_from_env_missing_host(monkeypatch):
    monkeypatch.delenv("SPARK_HOST", raising=False)
    with pytest.raises(ValueError, match="SPARK_HOST"):
        SparkConfig.from_env()


def test_frozen():
    config = SparkConfig(host="localhost")
    with pytest.raises(AttributeError):
        config.host = "other"
