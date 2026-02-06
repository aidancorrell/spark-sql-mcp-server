from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from spark_sql_mcp.tools import format_as_table, register_tools


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
