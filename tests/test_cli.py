"""Tests for CLI interface."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer.testing

from poetry_ide_setup.__main__ import app
from poetry_ide_setup.core import SetupResult
from poetry_ide_setup.exceptions import PoetryIdeSetupError


class TestCLI:
    """Test CLI functionality."""

    def setup_method(self) -> None:
        """Set up test runner."""
        self.runner = typer.testing.CliRunner()

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_success(self, mock_setup: MagicMock, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test successful CLI execution."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=temp_dir / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        result = self.runner.invoke(app, [])
        
        assert result.exit_code == 0
        assert "✓ IDE configuration updated successfully" in result.stdout
        assert str(mock_interpreter_path) in result.stdout
        assert "test-project" in result.stdout

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_with_project_path(self, mock_setup: MagicMock, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test CLI with project path option."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=temp_dir / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        result = self.runner.invoke(app, ["--project-path", str(temp_dir)])
        
        assert result.exit_code == 0
        mock_setup.assert_called_once()
        args, kwargs = mock_setup.call_args
        assert kwargs["project_path"] == temp_dir

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_dry_run(self, mock_setup: MagicMock, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test CLI dry run mode."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=temp_dir / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        result = self.runner.invoke(app, ["--dry-run"])
        
        assert result.exit_code == 0
        assert "DRY RUN - No files were modified" in result.stdout
        mock_setup.assert_called_once()
        args, kwargs = mock_setup.call_args
        assert kwargs["dry_run"] is True

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_force(self, mock_setup: MagicMock, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test CLI force mode."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=temp_dir / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        result = self.runner.invoke(app, ["--force"])
        
        assert result.exit_code == 0
        mock_setup.assert_called_once()
        args, kwargs = mock_setup.call_args
        assert kwargs["force"] is True

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_verbose(self, mock_setup: MagicMock, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test CLI verbose mode."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=temp_dir / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        result = self.runner.invoke(app, ["--verbose"])
        
        assert result.exit_code == 0
        assert "poetry-ide-setup starting" in result.stdout
        mock_setup.assert_called_once()
        args, kwargs = mock_setup.call_args
        assert kwargs["verbose"] is True

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_all_options(self, mock_setup: MagicMock, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test CLI with all options."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=temp_dir / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        result = self.runner.invoke(app, [
            "--project-path", str(temp_dir),
            "--dry-run",
            "--force",
            "--verbose"
        ])
        
        assert result.exit_code == 0
        mock_setup.assert_called_once()
        args, kwargs = mock_setup.call_args
        assert kwargs["project_path"] == temp_dir
        assert kwargs["dry_run"] is True
        assert kwargs["force"] is True
        assert kwargs["verbose"] is True

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_poetry_ide_setup_error(self, mock_setup: MagicMock) -> None:
        """Test CLI handling of PoetryIdeSetupError."""
        mock_setup.side_effect = PoetryIdeSetupError("Test error message")
        
        result = self.runner.invoke(app, [])
        
        assert result.exit_code == 1
        assert "Error: Test error message" in result.stdout

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_unexpected_error(self, mock_setup: MagicMock) -> None:
        """Test CLI handling of unexpected errors."""
        mock_setup.side_effect = ValueError("Unexpected error")
        
        result = self.runner.invoke(app, [])
        
        assert result.exit_code == 1
        assert "Unexpected error: Unexpected error" in result.stdout

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_unexpected_error_verbose(self, mock_setup: MagicMock) -> None:
        """Test CLI handling of unexpected errors with verbose output."""
        mock_setup.side_effect = ValueError("Unexpected error")
        
        result = self.runner.invoke(app, ["--verbose"])
        
        assert result.exit_code == 1
        assert "Unexpected error: Unexpected error" in result.stdout
        # Note: Testing exception printing is difficult with typer.testing

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Configure IntelliJ IDEA and PyCharm" in result.stdout
        assert "--project-path" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--force" in result.stdout
        assert "--verbose" in result.stdout

    @patch('poetry_ide_setup.__main__.setup_ide_configuration')
    def test_cli_current_directory_default(self, mock_setup: MagicMock, mock_interpreter_path: Path) -> None:
        """Test CLI uses current directory by default."""
        mock_setup.return_value = SetupResult(
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            config_file=Path.cwd() / ".idea" / "misc.xml",
            was_updated=True,
        )
        
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path("/fake/current/dir")
            
            result = self.runner.invoke(app, [])
            
            assert result.exit_code == 0
            mock_setup.assert_called_once()
            args, kwargs = mock_setup.call_args
            assert kwargs["project_path"] == Path("/fake/current/dir")