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

## Changelog

This project uses [changie](https://changie.dev/) to manage the changelog. Every PR that affects users must include a changelog entry.

### Adding a Changelog Entry

```bash
# Install changie (if not already installed)
brew install changie  # or: go install github.com/miniscruff/changie@latest

# Create a changelog entry (interactive)
changie new
```

Select the appropriate kind:
- **Breaking Change** — backwards-incompatible changes
- **Feature** — new functionality
- **Enhancement** — improvements to existing features
- **Bug Fix** — fixes for bugs
- **Documentation** — documentation-only changes
- **Internal** — refactoring, CI, dependencies

This creates a file in `.changes/unreleased/`. Commit it with your PR.

## Pull Request Process

1. Fork the repository and create a feature branch from `main`
2. Make your changes with clear, descriptive commits
3. Add tests for new functionality
4. Ensure all tests pass and linting is clean
5. **Add a changelog entry** via `changie new`
6. Update documentation if needed (README, docstrings)
7. Open a PR with a clear description of the changes

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
