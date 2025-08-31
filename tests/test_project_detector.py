"""Tests for project_detector module."""

from pathlib import Path

import pytest

from poetry_ide_setup.exceptions import IdeaDirectoryNotFoundError
from poetry_ide_setup.project_detector import ProjectDetector


class TestProjectDetector:
    """Test project detection functionality."""

    def test_find_idea_directory_success(self, mock_idea_project: Path) -> None:
        """Test successful .idea directory detection."""
        idea_path = ProjectDetector.find_idea_directory(mock_idea_project)

        assert idea_path == mock_idea_project / ".idea"
        assert idea_path.exists()
        assert idea_path.is_dir()

    def test_find_idea_directory_not_found(self, temp_dir: Path) -> None:
        """Test error when .idea directory doesn't exist."""
        with pytest.raises(
            IdeaDirectoryNotFoundError, match="No .idea directory found"
        ):
            ProjectDetector.find_idea_directory(temp_dir)

    def test_find_idea_directory_not_dir(self, temp_dir: Path) -> None:
        """Test error when .idea exists but is not a directory."""
        (temp_dir / ".idea").write_text("not a directory")

        with pytest.raises(
            IdeaDirectoryNotFoundError, match=".idea exists but is not a directory"
        ):
            ProjectDetector.find_idea_directory(temp_dir)

    def test_get_project_name_from_name_file(self, mock_idea_project: Path) -> None:
        """Test getting project name from .idea/.name file."""
        idea_path = mock_idea_project / ".idea"
        project_name = ProjectDetector.get_project_name(idea_path)

        assert project_name == "test-project"

    def test_get_project_name_from_directory_fallback(self, temp_dir: Path) -> None:
        """Test getting project name from directory name when .name file missing."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()

        project_name = ProjectDetector.get_project_name(idea_path)

        assert project_name == temp_dir.name

    def test_get_project_name_empty_name_file(self, temp_dir: Path) -> None:
        """Test fallback when .name file is empty."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()
        (idea_path / ".name").write_text("")

        project_name = ProjectDetector.get_project_name(idea_path)

        assert project_name == temp_dir.name

    def test_get_misc_xml_path(self, mock_idea_project: Path) -> None:
        """Test getting misc.xml path."""
        idea_path = mock_idea_project / ".idea"
        misc_xml_path = ProjectDetector.get_misc_xml_path(idea_path)

        assert misc_xml_path == idea_path / "misc.xml"

    def test_validate_project_structure_valid(self, mock_idea_project: Path) -> None:
        """Test project structure validation for valid project."""
        assert ProjectDetector.validate_project_structure(mock_idea_project) is True

    def test_validate_project_structure_no_idea(self, temp_dir: Path) -> None:
        """Test project structure validation when no .idea directory."""
        assert ProjectDetector.validate_project_structure(temp_dir) is False

    def test_validate_project_structure_minimal(self, temp_dir: Path) -> None:
        """Test project structure validation for minimal project."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()

        # Even with just .idea directory, it should be considered valid
        assert ProjectDetector.validate_project_structure(temp_dir) is True

    def test_is_python_project_from_modules_xml(
        self, mock_idea_python_project: Path
    ) -> None:
        """Test Python project detection from modules.xml."""
        idea_path = mock_idea_python_project / ".idea"

        # Need to create the .iml file with PYTHON_MODULE type
        iml_content = """<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
</module>"""
        (idea_path / "test-project.iml").write_text(iml_content)

        # Update modules.xml to reference the Python module
        modules_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/test-project.iml" filepath="$PROJECT_DIR$/.idea/test-project.iml" />
    </modules>
  </component>
</project>"""
        (idea_path / "modules.xml").write_text(modules_content)

        assert ProjectDetector.is_python_project(idea_path) is True

    def test_is_python_project_from_workspace_xml(self, temp_dir: Path) -> None:
        """Test Python project detection from workspace.xml."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()

        workspace_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="PropertiesComponent">
    <property name="settings.editor.selected.configurable" value="PyInterpreter" />
  </component>
</project>"""
        (idea_path / "workspace.xml").write_text(workspace_content)

        assert ProjectDetector.is_python_project(idea_path) is True

    def test_is_python_project_from_misc_xml(self, temp_dir: Path) -> None:
        """Test Python project detection from misc.xml."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()

        misc_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" project-jdk-type="Python SDK">
  </component>
</project>"""
        (idea_path / "misc.xml").write_text(misc_content)

        assert ProjectDetector.is_python_project(idea_path) is True

    def test_is_python_project_default_true(self, temp_dir: Path) -> None:
        """Test Python project detection defaults to True when uncertain."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()

        # No Python-specific indicators, should default to True
        assert ProjectDetector.is_python_project(idea_path) is True

    def test_is_python_project_invalid_xml(self, temp_dir: Path) -> None:
        """Test Python project detection with invalid XML files."""
        idea_path = temp_dir / ".idea"
        idea_path.mkdir()

        # Create invalid XML that can't be parsed
        (idea_path / "misc.xml").write_text("invalid xml content")

        # Should still default to True
        assert ProjectDetector.is_python_project(idea_path) is True
