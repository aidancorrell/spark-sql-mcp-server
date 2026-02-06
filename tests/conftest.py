from unittest.mock import MagicMock

import pytest

from spark_sql_mcp.config import SparkConfig
from spark_sql_mcp.spark_client import SparkSQLClient


@pytest.fixture
def spark_config():
    return SparkConfig(host="localhost", port=10000)


@pytest.fixture
def mock_hive_cursor():
    cursor = MagicMock()
    cursor.description = [("id",), ("name",)]
    cursor.fetchall.return_value = [(1, "alice"), (2, "bob")]
    return cursor


@pytest.fixture
def mock_hive_connection(mock_hive_cursor):
    conn = MagicMock()
    conn.cursor.return_value = mock_hive_cursor
    return conn


@pytest.fixture
def connected_client(spark_config, mock_hive_connection):
    client = SparkSQLClient(spark_config)
    client._connection = mock_hive_connection
    return client
