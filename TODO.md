# TODO - poetry-ide-setup Features

Based on the project specification, here are all the features to implement:

## Core Features

### 1. Interpreter Detection
- [ ] Run `poetry env info --path` to get Poetry environment path
- [ ] Run `poetry run which python` as fallback to obtain interpreter path
- [ ] Verify interpreter exists and is executable
- [ ] Handle cases where Poetry environment is not active

### 2. Project Identification
- [ ] Confirm `.idea/` directory exists in current or specified directory
- [ ] Derive project name from `.idea/.name` file if it exists
- [ ] Fall back to folder name if `.idea/.name` doesn't exist
- [ ] Validate project structure

### 3. Configuration Update
- [ ] Parse existing `.idea/misc.xml` safely
- [ ] Modify `<component name="ProjectRootManager" ...>` with correct interpreter path
- [ ] Insert or replace interpreter definition under `<project-jdk-name>` 
- [ ] Use label format like "Poetry: <env-name>"
- [ ] Support multiple updates safely (replace if already present)
- [ ] Preserve existing XML structure and formatting
- [ ] Handle missing misc.xml (create if needed)

### 4. CLI Interface
- [ ] Main command accessible via `poetry run ide-setup`
- [ ] `--project-path <path>` option to specify IntelliJ/PyCharm project location
- [ ] `--dry-run` option to show changes without writing
- [ ] `--force` option to overwrite existing configuration
- [ ] `--verbose` option for detailed output
- [ ] Help documentation and usage examples

### 5. Validation & Feedback
- [ ] Print interpreter path that will be used
- [ ] Show which configuration files will be updated
- [ ] Display success/failure messages
- [ ] Provide descriptive error messages for common failures:
  - `.idea` directory missing
  - Poetry environment not active
  - Interpreter not found
  - Permission issues
  - XML parsing errors

## Technical Implementation

### 6. Cross-Platform Support
- [ ] Windows path handling
- [ ] macOS path handling  
- [ ] Linux path handling
- [ ] Handle different Poetry installation methods

### 7. XML Handling
- [ ] Schema-compliant XML parsing and writing
- [ ] Preserve XML formatting and comments
- [ ] Handle malformed XML gracefully
- [ ] Backup original files before modification

### 8. Error Handling
- [ ] Graceful handling of missing Poetry
- [ ] Handle corrupted .idea files
- [ ] Network/filesystem permission errors
- [ ] Invalid project paths
- [ ] Non-Poetry Python environments

## Testing & Quality

### 9. Test Suite
- [ ] Unit tests for interpreter detection
- [ ] Unit tests for project identification
- [ ] Unit tests for XML manipulation
- [ ] Integration tests with mock .idea directories
- [ ] Cross-platform testing
- [ ] Edge case testing (missing files, permissions, etc.)
- [ ] Performance tests (< 500ms requirement)

### 10. Code Quality
- [ ] Type hints throughout codebase
- [ ] Docstrings for all public functions
- [ ] Black code formatting
- [ ] Ruff linting compliance
- [ ] mypy type checking
- [ ] Pre-commit hooks

## Documentation & Distribution

### 11. Documentation
- [ ] README.md with installation and usage instructions
- [ ] CHANGELOG.md for version history
- [ ] Example configurations and use cases
- [ ] Troubleshooting guide

### 12. CI/CD & Distribution
- [ ] GitHub Actions workflow
- [ ] Testing on Linux, macOS, Windows
- [ ] Automated PyPI publishing
- [ ] Version bumping automation

## Future Enhancements (Out of Scope for v1)
- [ ] Multi-environment support per project
- [ ] Wrapper for `idea .` / `charm .` commands
- [ ] GUI front-end
- [ ] JetBrains Gateway remote development support
- [ ] Support for non-Poetry virtual environments