"""Spark SQL MCP Server entry point."""

from mcp.server.fastmcp import FastMCP

from .config import SparkConfig
from .spark_client import SparkSQLClient
from .tools import register_tools

mcp = FastMCP("spark-sql-mcp-server")

_client: SparkSQLClient | None = None


def get_client() -> SparkSQLClient:
    if _client is None:
        raise RuntimeError("Spark client not initialized")
    return _client


register_tools(mcp, get_client)


def main() -> None:
    global _client
    config = SparkConfig.from_env()
    _client = SparkSQLClient(config)
    _client.connect()
    try:
        mcp.run()
    finally:
        _client.close()


if __name__ == "__main__":
    main()
