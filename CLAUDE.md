# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`poetry-ide-setup` is a Python package and command-line utility that automatically configures IntelliJ IDEA and PyCharm projects to use the same Python interpreter as the currently active Poetry environment. It eliminates manual SDK configuration in JetBrains IDEs.

## Development Setup

### Prerequisites
- Python ≥ 3.11
- Poetry for dependency management
- IntelliJ IDEA or PyCharm (for testing)

### Installation and Setup
```bash
# Install dependencies
poetry install

# Install development dependencies (already included in install)
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Common Development Commands

```bash
# Run the application
poetry run ide-setup

# Run with options
poetry run ide-setup --project-path /path/to/project --dry-run --verbose

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=poetry_ide_setup --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_core.py

# Run specific test method
poetry run pytest tests/test_core.py::TestSetupIdeConfiguration::test_setup_ide_configuration_success

# Type checking
poetry run mypy src/

# Code formatting
poetry run black src/ tests/

# Linting
poetry run ruff check src/ tests/

# Fix auto-fixable linting issues
poetry run ruff check --fix src/ tests/

# Run all quality checks
poetry run black src/ tests/ && poetry run ruff check src/ tests/ && poetry run mypy src/ && poetry run pytest
```

## Project Architecture

### Package Structure
```
src/poetry_ide_setup/
├── __init__.py          # Package metadata
├── __main__.py          # CLI entry point (poetry run ide-setup)
├── core.py              # Main orchestration logic
├── poetry_detector.py   # Poetry environment detection
├── project_detector.py  # IntelliJ/PyCharm project detection
├── xml_updater.py       # XML configuration file updates
└── exceptions.py        # Custom exception classes
```

### Key Components

1. **PoetryDetector** (`poetry_detector.py`): Detects Poetry environments and Python interpreters
   - Uses `poetry env info --path` and fallbacks
   - Cross-platform path handling (Windows vs Unix)
   - Validates Poetry availability and project structure

2. **ProjectDetector** (`project_detector.py`): Finds and validates IntelliJ/PyCharm projects
   - Locates `.idea/` directories
   - Extracts project names from `.idea/.name` or directory names
   - Validates project structure and Python configuration

3. **XMLUpdater** (`xml_updater.py`): Safely updates IDE configuration files
   - Parses and modifies `.idea/misc.xml` with proper XML handling
   - Creates backups before modifications
   - Preserves existing XML structure and formatting
   - Schema-compliant updates for `ProjectRootManager` component

4. **Core** (`core.py`): Orchestrates the entire setup process
   - Coordinates all components
   - Handles dry-run and force modes
   - Provides detailed result information
   - Comprehensive error handling

### CLI Interface
- Entry point: `poetry run ide-setup`
- Built with Typer for rich CLI experience
- Supports `--project-path`, `--dry-run`, `--force`, `--verbose` options
- Rich console output with colors and formatting

### XML Configuration Details
The tool updates `.idea/misc.xml` to configure the Python interpreter:
```xml
<component name="ProjectRootManager" 
           version="2" 
           languageLevel="JDK_11" 
           project-jdk-name="Poetry (env-name-abc123)" 
           project-jdk-type="Python SDK">
  <output url="file://$PROJECT_DIR$/out" />
</component>
```

### Error Handling
Custom exception hierarchy in `exceptions.py`:
- `PoetryIdeSetupError`: Base exception
- `PoetryNotFoundError`: Poetry unavailable
- `IdeaDirectoryNotFoundError`: No `.idea/` directory
- `InterpreterNotFoundError`: Python interpreter detection failed
- `ConfigurationError`: IDE configuration update failed
- `XMLParsingError`: XML file parsing/writing issues

## Testing Strategy

### Test Structure
- `tests/conftest.py`: Shared fixtures for mock projects and environments
- Individual test files for each module
- Integration tests in `test_core.py`
- CLI tests in `test_cli.py`

### Key Test Fixtures
- `temp_dir`: Temporary directory for test isolation
- `mock_poetry_project`: Mock Poetry project with `pyproject.toml`
- `mock_idea_project`: Mock IntelliJ project with `.idea/` structure
- `mock_misc_xml`: Mock `misc.xml` configuration file
- `mock_interpreter_path`: Mock Python interpreter executable

### Running Tests
```bash
# All tests
poetry run pytest

# With coverage report
poetry run pytest --cov=poetry_ide_setup --cov-report=html

# Specific test categories
poetry run pytest tests/test_core.py        # Integration tests
poetry run pytest tests/test_cli.py         # CLI tests
poetry run pytest tests/test_xml_updater.py # XML handling tests
```

## Code Quality Standards

### Type Hints
- All functions have type hints for parameters and return values
- Use `from typing import` for complex types
- Optional parameters use `Optional[Type]`

### Documentation
- Docstrings for all public functions and classes
- Include parameter descriptions and exception information
- Use Google/NumPy docstring format

### Error Handling
- Use custom exceptions from `exceptions.py`
- Provide descriptive error messages
- Handle cross-platform differences
- Graceful degradation when possible

### Cross-Platform Compatibility
- Handle Windows vs Unix path differences
- Use `pathlib.Path` for all file operations
- Account for different Poetry installation locations
- Test on multiple platforms via CI

## Dependencies

### Runtime Dependencies
- `typer`: CLI framework with rich features
- `rich`: Rich console output and formatting

### Development Dependencies
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `black`: Code formatting
- `ruff`: Fast Python linter
- `mypy`: Static type checking
- `pre-commit`: Git pre-commit hooks

## Distribution
- Package name: `poetry-ide-setup`
- Entry point: `ide-setup` (installed via `poetry.scripts`)
- Built with Poetry's build system
- Supports Python ≥ 3.11
- Cross-platform (Windows, macOS, Linux)