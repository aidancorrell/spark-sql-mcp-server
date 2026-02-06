"""MCP tool definitions for Spark SQL operations."""

import re
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP

from .spark_client import SparkSQLClient

_LIMIT_RE = re.compile(r"\bLIMIT\b", re.IGNORECASE)


def format_as_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No results."
    columns = list(rows[0].keys())
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(lines)


def register_tools(mcp: FastMCP, get_client: Callable[[], SparkSQLClient]) -> None:
    @mcp.tool()
    def list_databases() -> str:
        """List all available databases in the Spark cluster."""
        return "\n".join(get_client().list_databases())

    @mcp.tool()
    def list_tables(database: str | None = None) -> str:
        """List all tables in a database. Uses the default database if not specified."""
        tables = get_client().list_tables(database)
        return "\n".join(tables) if tables else "No tables found."

    @mcp.tool()
    def describe_table(table: str, database: str | None = None) -> str:
        """Get the schema/structure of a table including column names and types."""
        return format_as_table(get_client().describe_table(table, database))

    @mcp.tool()
    def execute_query(sql: str, limit: int = 100) -> str:
        """Execute a Spark SQL query and return results as a formatted table.

        A LIMIT clause is automatically appended if not present in the query.
        """
        query = sql if _LIMIT_RE.search(sql) else f"{sql} LIMIT {limit}"
        results = get_client().execute_query(query)
        if not results:
            return "Query returned no results."
        return format_as_table(results[:limit])
