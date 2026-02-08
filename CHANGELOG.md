# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Internal

* Publish to PyPI and update install instructions ([#6](https://github.com/aidancorrell/spark-sql-mcp-server/pull/6)) by @aidancorrell

## 0.1.0 - 2025-02-06

### Feature

* Initial release
* Query Spark SQL via Thrift/HiveServer2 protocol
* List databases and tables
* Describe table schemas
* Execute SQL queries with automatic LIMIT safety
* Support for NONE, LDAP, and Kerberos authentication
