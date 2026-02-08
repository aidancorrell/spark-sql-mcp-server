# Spark SQL MCP Server

An [MCP](https://modelcontextprotocol.io) server that enables AI assistants to query Spark SQL clusters via the Thrift/HiveServer2 protocol.

Works with any HiveServer2-compatible system: **Apache Spark**, **AWS EMR**, **Hive**, **Impala**, **Presto**.

## Features

- **Query Spark SQL** — Execute read-only SQL queries against your Spark cluster
- **Schema Discovery** — List databases, tables, and describe table structures
- **Multiple Auth Methods** — NONE, LDAP, NOSASL, CUSTOM, and Kerberos authentication
- **EMR Compatible** — Works with AWS EMR clusters out of the box
- **Read-Only Enforcement** — Only SELECT, SHOW, DESCRIBE, EXPLAIN, and WITH statements are allowed
- **Safety Defaults** — Automatic LIMIT clause on unbounded queries, sanitized error messages

## Installation

```bash
pip install spark-sql-mcp-server
```

Or run directly with [`uvx`](https://docs.astral.sh/uv/):

```bash
uvx spark-sql-mcp-server
```

## Quick Start

### 1. Set Environment Variables

```bash
export SPARK_HOST="your-emr-master-node.amazonaws.com"
export SPARK_PORT="10000"        # default
export SPARK_DATABASE="default"  # default
export SPARK_AUTH="NONE"         # NONE | LDAP | KERBEROS | CUSTOM | NOSASL
```

### 2. Add to Claude Code

**Global** (all projects) — add to `~/.claude.json` under your project's `mcpServers`:

```json
{
  "mcpServers": {
    "spark-sql": {
      "command": "uvx",
      "args": ["spark-sql-mcp-server"],
      "env": {
        "SPARK_HOST": "your-emr-master-node.amazonaws.com",
        "SPARK_PORT": "10000",
        "SPARK_AUTH": "NONE"
      }
    }
  }
}
```

**Project-level** — add to `.claude/mcp.json` in your repo:

```json
{
  "mcpServers": {
    "spark-sql": {
      "command": "uvx",
      "args": ["spark-sql-mcp-server"],
      "env": {
        "SPARK_HOST": "your-emr-master-node.amazonaws.com",
        "SPARK_PORT": "10000",
        "SPARK_AUTH": "NONE"
      }
    }
  }
}
```

### 3. Add to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spark-sql": {
      "command": "uvx",
      "args": ["spark-sql-mcp-server"],
      "env": {
        "SPARK_HOST": "your-emr-master-node.amazonaws.com",
        "SPARK_PORT": "10000"
      }
    }
  }
}
```

### 4. Query

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
| `execute_query` | Run read-only SQL queries with formatted results |

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

### Local Testing with Docker

A Docker Compose setup provides a local Spark Thrift Server with sample data for integration testing.

```bash
# Start the Spark Thrift Server
cd docker && docker compose up -d

# Wait for it to be ready (takes ~30s on first start)
docker logs -f spark-thrift-server  # look for "Sample data loaded."

# Run integration tests
pytest -m integration -v

# Tear down
cd docker && docker compose down -v
```

The local server comes with sample tables: `default.employees`, `default.orders`, and `test_db.metrics`.

Unit tests run by default with `pytest` (integration tests are skipped unless `-m integration` is specified).

#### Using the local server with Claude Code

With the Docker Spark server running, add it to your MCP config to test the server interactively.

**Global** — add to `~/.claude.json` under your project's `mcpServers`:

```json
{
  "spark-sql": {
    "command": "uvx",
    "args": ["spark-sql-mcp-server"],
    "env": {
      "SPARK_HOST": "localhost",
      "SPARK_PORT": "10000",
      "SPARK_AUTH": "NONE"
    }
  }
}
```

**Project-level** — add to `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "spark-sql": {
      "command": "uvx",
      "args": ["spark-sql-mcp-server"],
      "env": {
        "SPARK_HOST": "localhost",
        "SPARK_PORT": "10000",
        "SPARK_AUTH": "NONE"
      }
    }
  }
}
```

Then start a new Claude Code session and ask it to query the sample data.

## Security

### Read-Only Enforcement

The `execute_query` tool only allows read-only SQL statements. Queries must start with one of: `SELECT`, `SHOW`, `DESCRIBE`, `DESC`, `EXPLAIN`, or `WITH`. All other statement types (DROP, INSERT, DELETE, CREATE, ALTER, SET, ADD JAR, etc.) are rejected before reaching the Spark cluster.

### Error Sanitization

Database errors are sanitized before being returned to the MCP client. Internal details such as server hostnames, file paths, and stack traces are not exposed. Connection failures report only the target host/port and error type.

### Credential Handling

- Passwords are never included in log output or error messages
- The `SparkConfig` object masks passwords in its string representation
- `SPARK_PASSWORD` is marked as a secret in the MCP registry schema

### Known Limitations

- **No TLS/SSL support** — Thrift connections are unencrypted. For production use with LDAP auth, use an SSH tunnel to protect credentials in transit.
- **No query timeout** — Long-running queries are not automatically cancelled. Rely on Spark cluster-level timeout configuration.
- **No per-user access control** — All queries execute with the privileges of the configured Spark user. Use HiveServer2 authorization (Ranger, Sentry) to restrict access at the database level.
- **Auth mode defaults to NONE** — Appropriate for local development but not for production. Set `SPARK_AUTH` to `LDAP` or `KERBEROS` for authenticated environments.

## License

MIT
