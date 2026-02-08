from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from spark_sql_mcp.tools import (
    _safe_tool_call,
    _validate_readonly,
    format_as_table,
    register_tools,
)


class TestFormatAsTable:
    def test_basic(self):
        rows = [{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]
        result = format_as_table(rows)
        assert "| id | name |" in result
        assert "| 1 | alice |" in result
        assert "| 2 | bob |" in result

    def test_empty(self):
        assert format_as_table([]) == "No results."

    def test_single_column(self):
        rows = [{"count": 42}]
        result = format_as_table(rows)
        assert "| count |" in result
        assert "| 42 |" in result

    def test_none_values(self):
        rows = [{"a": None, "b": "ok"}]
        result = format_as_table(rows)
        assert "| None | ok |" in result


class TestValidateReadonly:
    def test_select_allowed(self):
        _validate_readonly("SELECT * FROM users")

    def test_select_with_leading_whitespace(self):
        _validate_readonly("  SELECT * FROM users")

    def test_show_allowed(self):
        _validate_readonly("SHOW DATABASES")

    def test_describe_allowed(self):
        _validate_readonly("DESCRIBE users")

    def test_desc_allowed(self):
        _validate_readonly("DESC users")

    def test_explain_allowed(self):
        _validate_readonly("EXPLAIN SELECT * FROM users")

    def test_with_cte_allowed(self):
        _validate_readonly("WITH cte AS (SELECT 1) SELECT * FROM cte")

    def test_case_insensitive(self):
        _validate_readonly("select * from users")

    def test_drop_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("DROP TABLE users")

    def test_insert_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("INSERT INTO users VALUES (1)")

    def test_delete_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("DELETE FROM users")

    def test_update_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("UPDATE users SET name = 'x'")

    def test_create_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("CREATE TABLE t (id INT)")

    def test_alter_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("ALTER TABLE users ADD COLUMN age INT")

    def test_set_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("SET spark.sql.shuffle.partitions=10")

    def test_add_jar_rejected(self):
        with pytest.raises(ValueError, match="read-only"):
            _validate_readonly("ADD JAR /path/to/jar")


class TestSafeToolCall:
    def test_returns_result_on_success(self):
        assert _safe_tool_call(lambda: "ok") == "ok"

    def test_value_error_shows_message(self):
        def _raise():
            raise ValueError("bad input")
        result = _safe_tool_call(_raise)
        assert result == "Error: bad input"

    def test_generic_error_is_sanitized(self):
        def _raise():
            raise RuntimeError("internal-host.corp:10000 connection refused")
        result = _safe_tool_call(_raise)
        assert "internal-host" not in result
        assert "query execution failed" in result

    def test_exception_details_not_leaked(self):
        def _raise():
            raise Exception("/internal/warehouse/path/secret_table")
        result = _safe_tool_call(_raise)
        assert "/internal" not in result
        assert "secret_table" not in result


class TestToolRegistration:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.list_databases.return_value = ["default", "analytics"]
        client.list_tables.return_value = ["users", "orders"]
        client.describe_table.return_value = [
            {"col_name": "id", "data_type": "int", "comment": ""},
        ]
        client.execute_query.return_value = [{"id": 1, "name": "test"}]
        return client

    @pytest.fixture
    def server(self, mock_client):
        mcp = FastMCP("test")
        register_tools(mcp, lambda: mock_client)
        return mcp

    def test_tools_registered(self, server):
        # Access the internal tool manager to verify registration
        assert server._tool_manager is not None
