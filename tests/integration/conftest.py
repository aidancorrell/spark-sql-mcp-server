"""Fixtures for integration tests against a live Spark Thrift Server."""

import subprocess
import time
from pathlib import Path

import pytest
from pyhive import hive

from spark_sql_mcp.config import SparkConfig
from spark_sql_mcp.spark_client import SparkSQLClient

DOCKER_DIR = Path(__file__).resolve().parent.parent.parent / "docker"
THRIFT_HOST = "localhost"
THRIFT_PORT = 10000


def _is_server_ready() -> bool:
    """Check if the Thrift Server is accepting connections."""
    try:
        conn = hive.Connection(host=THRIFT_HOST, port=THRIFT_PORT, auth="NONE")
        conn.close()
        return True
    except Exception:
        return False


def _wait_for_server(timeout: int = 180) -> None:
    """Wait until the Thrift Server is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _is_server_ready():
            return
        time.sleep(3)
    raise TimeoutError(
        f"Spark Thrift Server not ready after {timeout}s. "
        "Start it with: cd docker && docker compose up -d --wait"
    )


@pytest.fixture(scope="session")
def spark_client():
    """Provide a connected SparkSQLClient for the test session.

    If no Thrift Server is detected, attempts to start one via docker compose.
    """
    started_docker = False

    if not _is_server_ready():
        # Try to bring up docker compose automatically
        try:
            subprocess.run(
                ["docker", "compose", "up", "-d", "--wait"],
                cwd=DOCKER_DIR,
                check=True,
                capture_output=True,
                timeout=300,
            )
            started_docker = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
            pytest.skip(f"Could not start Spark Thrift Server via docker compose: {exc}")

    _wait_for_server()

    config = SparkConfig(host=THRIFT_HOST, port=THRIFT_PORT, auth="NONE")
    client = SparkSQLClient(config)
    client.connect()

    yield client

    client.close()

    if started_docker:
        subprocess.run(
            ["docker", "compose", "down", "-v"],
            cwd=DOCKER_DIR,
            capture_output=True,
        )
