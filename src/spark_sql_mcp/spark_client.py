"""Spark SQL client using Thrift/HiveServer2 protocol."""

import re
from typing import Any

from pyhive import hive

from .config import SparkConfig

_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)*$")


def _validate_identifier(name: str) -> str:
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


class SparkSQLClient:
    def __init__(self, config: SparkConfig):
        self._config = config
        self._connection: hive.Connection | None = None

    @property
    def connection(self) -> hive.Connection:
        if self._connection is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._connection

    def connect(self) -> None:
        kwargs: dict[str, Any] = {
            "host": self._config.host,
            "port": self._config.port,
            "database": self._config.database,
            "auth": self._config.auth,
            "username": self._config.username,
            "password": self._config.password,
        }
        if self._config.auth == "KERBEROS":
            kwargs["kerberos_service_name"] = self._config.kerberos_service_name
        try:
            self._connection = hive.Connection(**kwargs)
        except Exception as exc:
            raise ConnectionError(
                f"Failed to connect to Spark Thrift Server at "
                f"{self._config.host}:{self._config.port}: {type(exc).__name__}"
            ) from None

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            if cursor.description is None:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def list_databases(self) -> list[str]:
        results = self.execute_query("SHOW DATABASES")
        return [next(iter(r.values())) for r in results]

    def list_tables(self, database: str | None = None) -> list[str]:
        db = _validate_identifier(database or self._config.database)
        results = self.execute_query(f"SHOW TABLES IN {db}")
        return [r.get("tableName", next(iter(r.values()))) for r in results]

    def describe_table(self, table: str, database: str | None = None) -> list[dict[str, Any]]:
        db = _validate_identifier(database or self._config.database)
        tbl = _validate_identifier(table)
        return self.execute_query(f"DESCRIBE {db}.{tbl}")
