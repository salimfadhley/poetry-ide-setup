# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/poetry_ide_setup/` (`__main__.py`, `core.py`, `poetry_detector.py`, `project_detector.py`, `xml_updater.py`, `exceptions.py`).
- Config: `pyproject.toml` (Poetry, Black, Ruff, mypy, pytest settings).
- Tests: `tests/` (pytest; add `test_*.py` files here).
- IDE: Operates on JetBrains `.idea/` and `misc.xml` in your project.

## Build, Test, and Development Commands
- Install deps: `poetry install`
- Run CLI: `poetry run ide-setup --dry-run -v` (preview changes), then `poetry run ide-setup -p .` to apply.
- Tests: `poetry run pytest -v` (coverage configured via `pyproject.toml`).
- Lint: `poetry run ruff check .`
- Format: `poetry run black .` (use `--check` in CI).
- Types: `poetry run mypy src`

## Coding Style & Naming Conventions
- Python 3.11+; 4‑space indentation and type hints required (strict mypy settings).
- Formatting: Black, line length 88; imports auto‑sorted by Ruff (`I`).
- Linting: Ruff rules `E,W,F,I,B,C4,UP`; fix warnings or justify with `# noqa` sparingly.
- Naming: modules/functions `snake_case`, classes `CamelCase`, tests `test_*.py`.

## Testing Guidelines
- Framework: pytest with `pytest-cov` (coverage reported via `--cov=poetry_ide_setup`).
- Place unit tests in `tests/`, mirroring module names: `tests/test_xml_updater.py`, etc.
- Write fast, isolated tests; mock filesystem/process calls where needed.
- Run full suite: `poetry run pytest` before opening a PR.

## Commit & Pull Request Guidelines
- Commits: follow Conventional Commits, e.g., `feat: add dry-run preview panel`, `fix: handle missing .idea directory`.
- PRs: include a clear description, related issue, usage examples (CLI commands/output), and tests for new behavior.
- Quality gate: run `ruff`, `black --check`, `mypy`, and `pytest` locally; ensure no new warnings.

## Security & Configuration Tips
- The tool writes to `.idea/misc.xml` and creates a backup `misc.xml.backup` on change.
- Prefer `--dry-run` first; use `--force` cautiously when overwriting existing settings.
- Consider ignoring backup files in VCS if they appear (`*.backup`).

