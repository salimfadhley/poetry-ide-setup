"""Tests for poetry_detector module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from poetry_ide_setup.exceptions import InterpreterNotFoundError, PoetryNotFoundError
from poetry_ide_setup.poetry_detector import PoetryDetector


class TestPoetryDetector:
    """Test Poetry detection functionality."""

    @patch("subprocess.run")
    def test_get_interpreter_path_success_env_info(
        self, mock_run: MagicMock, mock_interpreter_path: Path
    ) -> None:
        """Test successful interpreter detection via poetry env info."""
        # Mock poetry env info --path
        mock_run.return_value.stdout = str(mock_interpreter_path.parent.parent)
        mock_run.return_value.returncode = 0

        result = PoetryDetector.get_interpreter_path()

        expected_path = mock_interpreter_path.parent.parent / "bin" / "python"
        assert result == expected_path

    @patch("subprocess.run")
    def test_get_interpreter_path_fallback_which_python(
        self, mock_run: MagicMock, mock_interpreter_path: Path
    ) -> None:
        """Test fallback to poetry run which python."""
        # First call (poetry env info) fails
        # Second call (poetry run which python) succeeds
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, "poetry env info --path"),
            MagicMock(stdout=str(mock_interpreter_path), returncode=0),
        ]

        result = PoetryDetector.get_interpreter_path()

        assert result == mock_interpreter_path

    @patch("subprocess.run")
    def test_get_interpreter_path_poetry_not_found(self, mock_run: MagicMock) -> None:
        """Test error when Poetry is not available."""
        # All subprocess calls fail
        mock_run.side_effect = FileNotFoundError("poetry command not found")

        with pytest.raises(PoetryNotFoundError, match="Poetry is not available"):
            PoetryDetector.get_interpreter_path()

    @patch("subprocess.run")
    def test_get_interpreter_path_no_interpreter(
        self, mock_run: MagicMock, temp_dir: Path
    ) -> None:
        """Test error when interpreter cannot be found."""
        # poetry env info returns non-existent path
        # poetry run which python fails
        # poetry --version succeeds (Poetry is available)
        fake_venv = temp_dir / "fake_venv"
        mock_run.side_effect = [
            MagicMock(stdout=str(fake_venv), returncode=0),  # env info
            subprocess.CalledProcessError(1, "which python"),  # which python fails
            MagicMock(returncode=0),  # poetry --version succeeds
        ]

        with pytest.raises(
            InterpreterNotFoundError, match="no Python interpreter could be detected"
        ):
            PoetryDetector.get_interpreter_path()

    @patch("subprocess.run")
    def test_get_environment_info_success(
        self, mock_run: MagicMock, mock_interpreter_path: Path
    ) -> None:
        """Test successful environment info detection."""
        # Mock poetry env info --path and poetry env info
        mock_run.side_effect = [
            MagicMock(stdout=str(mock_interpreter_path.parent.parent), returncode=0),
            MagicMock(stdout="Name: test-project-abc123", returncode=0),
        ]

        interpreter_path, env_name = PoetryDetector.get_environment_info()

        expected_path = mock_interpreter_path.parent.parent / "bin" / "python"
        assert interpreter_path == expected_path
        assert env_name == "test-project-abc123"

    @patch("subprocess.run")
    def test_get_environment_info_fallback_name(
        self, mock_run: MagicMock, mock_interpreter_path: Path
    ) -> None:
        """Test environment name fallback from path."""
        # Mock poetry env info --path success, poetry env info failure
        mock_run.side_effect = [
            MagicMock(stdout=str(mock_interpreter_path.parent.parent), returncode=0),
            subprocess.CalledProcessError(1, "poetry env info"),
        ]

        interpreter_path, env_name = PoetryDetector.get_environment_info()

        expected_path = mock_interpreter_path.parent.parent / "bin" / "python"
        assert interpreter_path == expected_path
        assert env_name == mock_interpreter_path.parent.parent.name

    @patch("subprocess.run")
    def test_is_poetry_available_true(self, mock_run: MagicMock) -> None:
        """Test Poetry availability check when available."""
        mock_run.return_value.returncode = 0

        assert PoetryDetector.is_poetry_available() is True

    @patch("subprocess.run")
    def test_is_poetry_available_false(self, mock_run: MagicMock) -> None:
        """Test Poetry availability check when not available."""
        mock_run.side_effect = FileNotFoundError("poetry not found")

        assert PoetryDetector.is_poetry_available() is False

    def test_is_in_poetry_project_true(self, mock_poetry_project: Path) -> None:
        """Test Poetry project detection when in Poetry project."""
        assert PoetryDetector.is_in_poetry_project(mock_poetry_project) is True

    def test_is_in_poetry_project_false_no_file(self, temp_dir: Path) -> None:
        """Test Poetry project detection when no pyproject.toml."""
        assert PoetryDetector.is_in_poetry_project(temp_dir) is False

    def test_is_in_poetry_project_false_no_poetry_config(self, temp_dir: Path) -> None:
        """Test Poetry project detection when pyproject.toml has no Poetry config."""
        (temp_dir / "pyproject.toml").write_text(
            "[build-system]\nrequires = ['setuptools']"
        )

        assert PoetryDetector.is_in_poetry_project(temp_dir) is False

    def test_is_in_poetry_project_current_directory(
        self, mock_poetry_project: Path
    ) -> None:
        """Test Poetry project detection in current directory."""
        with patch("pathlib.Path.cwd", return_value=mock_poetry_project):
            assert PoetryDetector.is_in_poetry_project() is True
