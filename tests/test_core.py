"""Tests for core module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from poetry_ide_setup.core import setup_ide_configuration
from poetry_ide_setup.exceptions import IdeaDirectoryNotFoundError, PoetryNotFoundError


class TestSetupIdeConfiguration:
    """Test core setup functionality."""

    @patch('poetry_ide_setup.core.PoetryDetector')
    @patch('poetry_ide_setup.core.ProjectDetector')
    @patch('poetry_ide_setup.core.XMLUpdater')
    def test_setup_ide_configuration_success(
        self,
        mock_xml_updater: MagicMock,
        mock_project_detector: MagicMock,
        mock_poetry_detector: MagicMock,
        mock_idea_python_project: Path,
        mock_interpreter_path: Path,
    ) -> None:
        """Test successful IDE configuration setup."""
        # Setup mocks
        mock_poetry_detector.is_poetry_available.return_value = True
        mock_poetry_detector.is_in_poetry_project.return_value = True
        mock_poetry_detector.get_environment_info.return_value = (mock_interpreter_path, "test-env-abc123")
        
        mock_project_detector.find_idea_directory.return_value = mock_idea_python_project / ".idea"
        mock_project_detector.get_project_name.return_value = "test-project"
        mock_project_detector.get_misc_xml_path.return_value = mock_idea_python_project / ".idea" / "misc.xml"
        mock_project_detector.validate_project_structure.return_value = True
        mock_project_detector.is_python_project.return_value = True
        
        mock_xml_updater.get_current_interpreter.return_value = None
        mock_xml_updater.validate_misc_xml.return_value = True
        
        # Run setup
        result = setup_ide_configuration(project_path=mock_idea_python_project)
        
        # Verify results
        assert result.interpreter_path == mock_interpreter_path
        assert result.project_name == "test-project"
        assert result.environment_name == "test-env-abc123"
        assert result.was_updated is True
        
        # Verify XML was updated
        mock_xml_updater.update_misc_xml.assert_called_once()

    @patch('poetry_ide_setup.core.PoetryDetector')
    def test_setup_ide_configuration_poetry_not_available(
        self,
        mock_poetry_detector: MagicMock,
        mock_idea_python_project: Path,
    ) -> None:
        """Test error when Poetry is not available."""
        mock_poetry_detector.is_poetry_available.return_value = False
        
        with pytest.raises(PoetryNotFoundError, match="Poetry is not available"):
            setup_ide_configuration(project_path=mock_idea_python_project)

    @patch('poetry_ide_setup.core.PoetryDetector')
    @patch('poetry_ide_setup.core.ProjectDetector')
    def test_setup_ide_configuration_no_idea_directory(
        self,
        mock_project_detector: MagicMock,
        mock_poetry_detector: MagicMock,
        temp_dir: Path,
    ) -> None:
        """Test error when .idea directory is missing."""
        mock_poetry_detector.is_poetry_available.return_value = True
        mock_project_detector.find_idea_directory.side_effect = IdeaDirectoryNotFoundError("No .idea directory")
        
        with pytest.raises(IdeaDirectoryNotFoundError, match="No .idea directory"):
            setup_ide_configuration(project_path=temp_dir)

    @patch('poetry_ide_setup.core.PoetryDetector')
    @patch('poetry_ide_setup.core.ProjectDetector')
    @patch('poetry_ide_setup.core.XMLUpdater')
    def test_setup_ide_configuration_already_configured(
        self,
        mock_xml_updater: MagicMock,
        mock_project_detector: MagicMock,
        mock_poetry_detector: MagicMock,
        mock_idea_python_project: Path,
        mock_interpreter_path: Path,
    ) -> None:
        """Test when configuration is already up to date."""
        # Setup mocks
        mock_poetry_detector.is_poetry_available.return_value = True
        mock_poetry_detector.get_environment_info.return_value = (mock_interpreter_path, "test-env-abc123")
        
        mock_project_detector.find_idea_directory.return_value = mock_idea_python_project / ".idea"
        mock_project_detector.get_project_name.return_value = "test-project"
        mock_project_detector.get_misc_xml_path.return_value = mock_idea_python_project / ".idea" / "misc.xml"
        
        # Mock that interpreter is already correctly configured
        mock_xml_updater.get_current_interpreter.return_value = "Poetry (test-env-abc123)"
        
        # Run setup
        result = setup_ide_configuration(project_path=mock_idea_python_project)
        
        # Verify results
        assert result.was_updated is False
        assert result.previous_interpreter == "Poetry (test-env-abc123)"
        
        # Verify XML was NOT updated
        mock_xml_updater.update_misc_xml.assert_not_called()

    @patch('poetry_ide_setup.core.PoetryDetector')
    @patch('poetry_ide_setup.core.ProjectDetector')
    @patch('poetry_ide_setup.core.XMLUpdater')
    def test_setup_ide_configuration_dry_run(
        self,
        mock_xml_updater: MagicMock,
        mock_project_detector: MagicMock,
        mock_poetry_detector: MagicMock,
        mock_idea_python_project: Path,
        mock_interpreter_path: Path,
    ) -> None:
        """Test dry run mode."""
        # Setup mocks
        mock_poetry_detector.is_poetry_available.return_value = True
        mock_poetry_detector.get_environment_info.return_value = (mock_interpreter_path, "test-env-abc123")
        
        mock_project_detector.find_idea_directory.return_value = mock_idea_python_project / ".idea"
        mock_project_detector.get_project_name.return_value = "test-project"
        mock_project_detector.get_misc_xml_path.return_value = mock_idea_python_project / ".idea" / "misc.xml"
        
        mock_xml_updater.get_current_interpreter.return_value = None
        
        # Run setup with dry run
        result = setup_ide_configuration(project_path=mock_idea_python_project, dry_run=True)
        
        # Verify results indicate update would happen
        assert result.was_updated is True
        
        # Verify XML was NOT actually updated
        mock_xml_updater.update_misc_xml.assert_not_called()

    @patch('poetry_ide_setup.core.PoetryDetector')
    @patch('poetry_ide_setup.core.ProjectDetector')
    @patch('poetry_ide_setup.core.XMLUpdater')
    def test_setup_ide_configuration_force_update(
        self,
        mock_xml_updater: MagicMock,
        mock_project_detector: MagicMock,
        mock_poetry_detector: MagicMock,
        mock_idea_python_project: Path,
        mock_interpreter_path: Path,
    ) -> None:
        """Test force update mode."""
        # Setup mocks
        mock_poetry_detector.is_poetry_available.return_value = True
        mock_poetry_detector.get_environment_info.return_value = (mock_interpreter_path, "test-env-abc123")
        
        mock_project_detector.find_idea_directory.return_value = mock_idea_python_project / ".idea"
        mock_project_detector.get_project_name.return_value = "test-project"
        mock_project_detector.get_misc_xml_path.return_value = mock_idea_python_project / ".idea" / "misc.xml"
        
        # Mock that interpreter is already correctly configured
        mock_xml_updater.get_current_interpreter.return_value = "Poetry (test-env-abc123)"
        mock_xml_updater.validate_misc_xml.return_value = True
        
        # Run setup with force
        result = setup_ide_configuration(project_path=mock_idea_python_project, force=True)
        
        # Verify results
        assert result.was_updated is True
        
        # Verify XML was updated despite being already correct
        mock_xml_updater.update_misc_xml.assert_called_once()

    @patch('poetry_ide_setup.core.console')
    @patch('poetry_ide_setup.core.PoetryDetector')
    @patch('poetry_ide_setup.core.ProjectDetector')
    @patch('poetry_ide_setup.core.XMLUpdater')
    def test_setup_ide_configuration_verbose_output(
        self,
        mock_xml_updater: MagicMock,
        mock_project_detector: MagicMock,
        mock_poetry_detector: MagicMock,
        mock_console: MagicMock,
        mock_idea_python_project: Path,
        mock_interpreter_path: Path,
    ) -> None:
        """Test verbose output mode."""
        # Setup mocks
        mock_poetry_detector.is_poetry_available.return_value = True
        mock_poetry_detector.is_in_poetry_project.return_value = True
        mock_poetry_detector.get_environment_info.return_value = (mock_interpreter_path, "test-env-abc123")
        
        mock_project_detector.find_idea_directory.return_value = mock_idea_python_project / ".idea"
        mock_project_detector.get_project_name.return_value = "test-project"
        mock_project_detector.get_misc_xml_path.return_value = mock_idea_python_project / ".idea" / "misc.xml"
        mock_project_detector.validate_project_structure.return_value = True
        mock_project_detector.is_python_project.return_value = True
        
        mock_xml_updater.get_current_interpreter.return_value = None
        mock_xml_updater.validate_misc_xml.return_value = True
        
        # Run setup with verbose
        setup_ide_configuration(project_path=mock_idea_python_project, verbose=True)
        
        # Verify verbose output was printed
        assert mock_console.print.call_count > 0
        verbose_calls = [call for call in mock_console.print.call_args_list if '[dim]' in str(call)]
        assert len(verbose_calls) > 0