"""Configuration management for Spark SQL MCP Server."""

import os
from dataclasses import dataclass

_VALID_AUTH_MODES = frozenset({"NONE", "LDAP", "KERBEROS", "CUSTOM", "NOSASL"})


@dataclass(frozen=True)
class SparkConfig:
    host: str
    port: int = 10000
    database: str = "default"
    auth: str = "NONE"
    username: str | None = None
    password: str | None = None
    kerberos_service_name: str = "hive"

    def __repr__(self) -> str:
        return (
            f"SparkConfig(host={self.host!r}, port={self.port!r}, "
            f"database={self.database!r}, auth={self.auth!r}, "
            f"username={self.username!r}, "
            f"password={'****' if self.password else None!r}, "
            f"kerberos_service_name={self.kerberos_service_name!r})"
        )

    @classmethod
    def from_env(cls) -> "SparkConfig":
        host = os.environ.get("SPARK_HOST")
        if not host:
            raise ValueError("SPARK_HOST environment variable is required")

        auth = os.environ.get("SPARK_AUTH", "NONE").upper()
        if auth not in _VALID_AUTH_MODES:
            raise ValueError(
                f"Invalid SPARK_AUTH value: {auth!r}. "
                f"Must be one of: {', '.join(sorted(_VALID_AUTH_MODES))}"
            )

        return cls(
            host=host,
            port=int(os.environ.get("SPARK_PORT", "10000")),
            database=os.environ.get("SPARK_DATABASE", "default"),
            auth=auth,
            username=os.environ.get("SPARK_USERNAME"),
            password=os.environ.get("SPARK_PASSWORD"),
            kerberos_service_name=os.environ.get("SPARK_KERBEROS_SERVICE_NAME", "hive"),
        )
