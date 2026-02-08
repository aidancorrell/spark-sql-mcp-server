from unittest.mock import patch

import pytest

from spark_sql_mcp.spark_client import SparkSQLClient, _validate_identifier


class TestValidateIdentifier:
    def test_simple_name(self):
        assert _validate_identifier("users") == "users"

    def test_dotted_name(self):
        assert _validate_identifier("analytics.users") == "analytics.users"

    def test_underscores(self):
        assert _validate_identifier("my_table_1") == "my_table_1"

    def test_rejects_semicolon(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            _validate_identifier("users; DROP TABLE--")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            _validate_identifier("bad name")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            _validate_identifier("")


class TestSparkSQLClient:
    def test_not_connected_raises(self, spark_config):
        client = SparkSQLClient(spark_config)
        with pytest.raises(RuntimeError, match="Not connected"):
            client.connection

    @patch("spark_sql_mcp.spark_client.hive.Connection")
    def test_connect(self, mock_conn_cls, spark_config):
        client = SparkSQLClient(spark_config)
        client.connect()
        mock_conn_cls.assert_called_once_with(
            host="localhost",
            port=10000,
            database="default",
            auth="NONE",
            username=None,
            password=None,
        )

    def test_execute_query(self, connected_client, mock_hive_cursor):
        results = connected_client.execute_query("SELECT * FROM users")
        assert results == [{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]
        mock_hive_cursor.close.assert_called_once()

    def test_execute_query_no_results(self, connected_client, mock_hive_cursor):
        mock_hive_cursor.description = None
        results = connected_client.execute_query("CREATE TABLE t (id INT)")
        assert results == []

    def test_execute_query_closes_cursor_on_error(self, connected_client, mock_hive_cursor):
        mock_hive_cursor.execute.side_effect = RuntimeError("query failed")
        with pytest.raises(RuntimeError, match="query failed"):
            connected_client.execute_query("BAD SQL")
        mock_hive_cursor.close.assert_called_once()

    def test_list_databases(self, connected_client, mock_hive_cursor):
        mock_hive_cursor.description = [("databaseName",)]
        mock_hive_cursor.fetchall.return_value = [("default",), ("analytics",)]
        assert connected_client.list_databases() == ["default", "analytics"]

    def test_list_tables(self, connected_client, mock_hive_cursor):
        mock_hive_cursor.description = [("tableName",)]
        mock_hive_cursor.fetchall.return_value = [("users",), ("orders",)]
        assert connected_client.list_tables() == ["users", "orders"]

    def test_describe_table(self, connected_client, mock_hive_cursor):
        mock_hive_cursor.description = [("col_name",), ("data_type",), ("comment",)]
        mock_hive_cursor.fetchall.return_value = [("id", "int", ""), ("name", "string", "")]
        result = connected_client.describe_table("users")
        assert result == [
            {"col_name": "id", "data_type": "int", "comment": ""},
            {"col_name": "name", "data_type": "string", "comment": ""},
        ]

    def test_close(self, connected_client, mock_hive_connection):
        connected_client.close()
        mock_hive_connection.close.assert_called_once()
        assert connected_client._connection is None

    def test_close_when_not_connected(self, spark_config):
        client = SparkSQLClient(spark_config)
        client.close()  # should not raise

    @patch("spark_sql_mcp.spark_client.hive.Connection")
    def test_connect_error_sanitized(self, mock_conn_cls, spark_config):
        mock_conn_cls.side_effect = Exception("secret connection details here")
        client = SparkSQLClient(spark_config)
        with pytest.raises(ConnectionError, match="Failed to connect") as exc_info:
            client.connect()
        # Original exception details should not leak
        assert "secret connection details" not in str(exc_info.value)
        # Should not chain the original exception
        assert exc_info.value.__cause__ is None
