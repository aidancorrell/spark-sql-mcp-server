# Contributing to Spark SQL MCP Server

Thanks for your interest in contributing! This document outlines how to get started.

## Development Setup

```bash
git clone https://github.com/aidancorrell/spark-sql-mcp-server.git
cd spark-sql-mcp-server
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest -v
```

## Code Style

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
ruff check .
ruff format .
```

All code must pass lint checks before merging.

## Pull Request Process

1. Fork the repository and create a feature branch from `main`
2. Make your changes with clear, descriptive commits
3. Add tests for new functionality
4. Ensure all tests pass and linting is clean
5. Update documentation if needed (README, docstrings)
6. Open a PR with a clear description of the changes
7. **Add a label** to categorize the change (see below)

### PR Labels

Add one of these labels to your PR for changelog categorization:

| Label | Use for |
|-------|---------|
| `breaking` | Backwards-incompatible changes |
| `feature` | New functionality |
| `enhancement` | Improvements to existing features |
| `bug` | Bug fixes |
| `docs` | Documentation-only changes |
| `internal` | Refactoring, CI, dependencies |

The changelog is automatically updated when PRs are merged.

### PR Requirements

- All CI checks must pass
- At least one approving review required
- Keep PRs focused—one feature or fix per PR
- Squash commits when merging

## Reporting Issues

- Search existing issues before creating a new one
- Include reproduction steps, expected vs actual behavior
- For bugs, include Python version and relevant environment details

## Security

If you discover a security vulnerability, please open a GitHub security advisory rather than a public issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
