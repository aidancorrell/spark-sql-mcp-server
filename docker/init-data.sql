-- Sample data for integration testing

-- Tables in the default database
CREATE TABLE IF NOT EXISTS employees (
    id INT,
    name STRING,
    department STRING,
    salary DOUBLE
) USING parquet;

INSERT OVERWRITE TABLE employees VALUES
    (1, 'Alice', 'Engineering', 95000.0),
    (2, 'Bob', 'Engineering', 90000.0),
    (3, 'Carol', 'Marketing', 85000.0),
    (4, 'David', 'Marketing', 80000.0),
    (5, 'Eve', 'Sales', 75000.0);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT,
    customer STRING,
    amount DOUBLE,
    status STRING
) USING parquet;

INSERT OVERWRITE TABLE orders VALUES
    (101, 'Alice', 250.00, 'completed'),
    (102, 'Bob', 175.50, 'completed'),
    (103, 'Carol', 320.00, 'pending'),
    (104, 'David', 95.25, 'completed'),
    (105, 'Eve', 410.00, 'pending');

-- Separate database with its own table
CREATE DATABASE IF NOT EXISTS test_db;

CREATE TABLE IF NOT EXISTS test_db.metrics (
    metric_name STRING,
    metric_value DOUBLE,
    recorded_at STRING
) USING parquet;

INSERT OVERWRITE TABLE test_db.metrics VALUES
    ('cpu_usage', 72.5, '2024-01-15'),
    ('memory_usage', 85.3, '2024-01-15'),
    ('disk_io', 45.0, '2024-01-15');
