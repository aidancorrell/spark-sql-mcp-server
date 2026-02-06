# Spark SQL MCP Server

An [MCP](https://modelcontextprotocol.io) server that enables AI assistants to query Spark SQL clusters via the Thrift/HiveServer2 protocol.

Works with any HiveServer2-compatible system: **Apache Spark**, **AWS EMR**, **Hive**, **Impala**, **Presto**.

## Features

- **Query Spark SQL** — Execute SQL queries against your Spark cluster
- **Schema Discovery** — List databases, tables, and describe table structures
- **Multiple Auth Methods** — NONE, LDAP, and Kerberos authentication
- **EMR Compatible** — Works with AWS EMR clusters out of the box
- **Safety Defaults** — Automatic LIMIT clause on unbounded queries

## Installation

```bash
pip install git+https://github.com/aidancorrell/spark-sql-mcp-server.git
```

## Quick Start

### 1. Set Environment Variables

```bash
export SPARK_HOST="your-emr-master-node.amazonaws.com"
export SPARK_PORT="10000"        # default
export SPARK_DATABASE="default"  # default
export SPARK_AUTH="NONE"         # NONE | LDAP | KERBEROS
```

### 2. Add to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spark-sql": {
      "command": "spark-sql-mcp",
      "env": {
        "SPARK_HOST": "your-emr-master-node.amazonaws.com",
        "SPARK_PORT": "10000"
      }
    }
  }
}
```

### 3. Query

Ask Claude things like:

- "What databases are available in our Spark cluster?"
- "Show me the schema of the `sales.transactions` table"
- "Query the top 10 customers by revenue from the analytics database"

## Available Tools

| Tool | Description |
|------|-------------|
| `list_databases` | List all available databases |
| `list_tables` | List tables in a database |
| `describe_table` | Get table schema (columns, types) |
| `execute_query` | Run SQL queries with formatted results |

## Authentication

### No Auth (default)

```bash
export SPARK_AUTH="NONE"
```

### LDAP

```bash
export SPARK_AUTH="LDAP"
export SPARK_USERNAME="your-username"
export SPARK_PASSWORD="your-password"
```

### Kerberos

```bash
export SPARK_AUTH="KERBEROS"
export SPARK_KERBEROS_SERVICE_NAME="hive"  # default
# Ensure you have a valid Kerberos ticket (kinit)
```

## AWS EMR Setup

1. **Security Group** — Allow inbound traffic on port 10000 from your IP
2. **SSH Tunnel** (recommended):
   ```bash
   ssh -i your-key.pem -L 10000:localhost:10000 hadoop@your-emr-master
   ```
3. Set `SPARK_HOST=localhost`

## Development

```bash
git clone https://github.com/aidancorrell/spark-sql-mcp-server.git
cd spark-sql-mcp-server
pip install -e ".[dev]"
pytest
ruff check .
```

## License

MIT
