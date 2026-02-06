"""Configuration management for Spark SQL MCP Server."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SparkConfig:
    host: str
    port: int = 10000
    database: str = "default"
    auth: str = "NONE"
    username: str | None = None
    password: str | None = None
    kerberos_service_name: str = "hive"

    @classmethod
    def from_env(cls) -> "SparkConfig":
        host = os.environ.get("SPARK_HOST")
        if not host:
            raise ValueError("SPARK_HOST environment variable is required")

        return cls(
            host=host,
            port=int(os.environ.get("SPARK_PORT", "10000")),
            database=os.environ.get("SPARK_DATABASE", "default"),
            auth=os.environ.get("SPARK_AUTH", "NONE"),
            username=os.environ.get("SPARK_USERNAME"),
            password=os.environ.get("SPARK_PASSWORD"),
            kerberos_service_name=os.environ.get("SPARK_KERBEROS_SERVICE_NAME", "hive"),
        )
