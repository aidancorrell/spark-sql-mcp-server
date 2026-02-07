"""Integration tests for Spark SQL MCP Server against a live Spark Thrift Server."""

import pytest

from spark_sql_mcp.spark_client import SparkSQLClient

pytestmark = pytest.mark.integration


class TestListDatabases:
    def test_returns_default_database(self, spark_client: SparkSQLClient):
        databases = spark_client.list_databases()
        assert "default" in databases

    def test_returns_test_db(self, spark_client: SparkSQLClient):
        databases = spark_client.list_databases()
        assert "test_db" in databases


class TestListTables:
    def test_default_database_has_employees(self, spark_client: SparkSQLClient):
        tables = spark_client.list_tables("default")
        assert "employees" in tables

    def test_default_database_has_orders(self, spark_client: SparkSQLClient):
        tables = spark_client.list_tables("default")
        assert "orders" in tables

    def test_test_db_has_metrics(self, spark_client: SparkSQLClient):
        tables = spark_client.list_tables("test_db")
        assert "metrics" in tables


class TestDescribeTable:
    def test_employees_schema(self, spark_client: SparkSQLClient):
        schema = spark_client.describe_table("employees")
        col_names = [row["col_name"] for row in schema]
        assert "id" in col_names
        assert "name" in col_names
        assert "department" in col_names
        assert "salary" in col_names

    def test_orders_schema(self, spark_client: SparkSQLClient):
        schema = spark_client.describe_table("orders")
        col_names = [row["col_name"] for row in schema]
        assert "order_id" in col_names
        assert "customer" in col_names
        assert "amount" in col_names
        assert "status" in col_names

    def test_cross_database_describe(self, spark_client: SparkSQLClient):
        schema = spark_client.describe_table("metrics", database="test_db")
        col_names = [row["col_name"] for row in schema]
        assert "metric_name" in col_names
        assert "metric_value" in col_names
        assert "recorded_at" in col_names


class TestExecuteQuery:
    def test_select_all_employees(self, spark_client: SparkSQLClient):
        results = spark_client.execute_query("SELECT * FROM employees")
        assert len(results) == 5

    def test_aggregation_query(self, spark_client: SparkSQLClient):
        results = spark_client.execute_query(
            "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department"
        )
        departments = {row["department"] for row in results}
        assert departments == {"Engineering", "Marketing", "Sales"}

    def test_filtered_query(self, spark_client: SparkSQLClient):
        results = spark_client.execute_query(
            "SELECT * FROM employees WHERE department = 'Engineering'"
        )
        assert len(results) == 2
        assert all(row["department"] == "Engineering" for row in results)

    def test_cross_database_query(self, spark_client: SparkSQLClient):
        results = spark_client.execute_query("SELECT * FROM test_db.metrics")
        assert len(results) == 3

    def test_orders_query(self, spark_client: SparkSQLClient):
        results = spark_client.execute_query(
            "SELECT * FROM orders WHERE status = 'completed'"
        )
        assert len(results) == 3
