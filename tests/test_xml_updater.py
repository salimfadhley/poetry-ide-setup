"""Tests for xml_updater module."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from poetry_ide_setup.exceptions import ConfigurationError, XMLParsingError
from poetry_ide_setup.xml_updater import XMLUpdater


class TestXMLUpdater:
    """Test XML configuration updating functionality."""

    def test_update_misc_xml_new_file(
        self, temp_dir: Path, mock_interpreter_path: Path
    ) -> None:
        """Test creating new misc.xml file."""
        misc_xml_path = temp_dir / ".idea" / "misc.xml"
        misc_xml_path.parent.mkdir(parents=True)

        XMLUpdater.update_misc_xml(
            misc_xml_path=misc_xml_path,
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            backup=False,
        )

        assert misc_xml_path.exists()

        # Parse and verify content
        tree = ET.parse(misc_xml_path)
        root = tree.getroot()

        assert root.tag == "project"
        assert root.get("version") == "4"

        prm = root.find(".//component[@name='ProjectRootManager']")
        assert prm is not None
        assert prm.get("project-jdk-name") == "Poetry (test-env-abc123)"
        assert prm.get("project-jdk-type") == "Python SDK"

    def test_update_misc_xml_existing_file(
        self, mock_misc_xml: Path, mock_interpreter_path: Path
    ) -> None:
        """Test updating existing misc.xml file."""
        XMLUpdater.update_misc_xml(
            misc_xml_path=mock_misc_xml,
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            backup=False,
        )

        # Parse and verify content
        tree = ET.parse(mock_misc_xml)
        root = tree.getroot()

        prm = root.find(".//component[@name='ProjectRootManager']")
        assert prm is not None
        assert prm.get("project-jdk-name") == "Poetry (test-env-abc123)"
        assert prm.get("project-jdk-type") == "Python SDK"

    def test_update_misc_xml_with_backup(
        self, mock_misc_xml: Path, mock_interpreter_path: Path
    ) -> None:
        """Test creating backup when updating misc.xml."""
        original_content = mock_misc_xml.read_text()

        XMLUpdater.update_misc_xml(
            misc_xml_path=mock_misc_xml,
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            backup=True,
        )

        backup_path = mock_misc_xml.with_suffix(".xml.backup")
        assert backup_path.exists()
        assert backup_path.read_text() == original_content

    def test_update_misc_xml_invalid_xml(
        self, temp_dir: Path, mock_interpreter_path: Path
    ) -> None:
        """Test error handling for invalid XML."""
        misc_xml_path = temp_dir / ".idea" / "misc.xml"
        misc_xml_path.parent.mkdir(parents=True)
        misc_xml_path.write_text("invalid xml content")

        with pytest.raises(XMLParsingError, match="Failed to parse"):
            XMLUpdater.update_misc_xml(
                misc_xml_path=misc_xml_path,
                interpreter_path=mock_interpreter_path,
                project_name="test-project",
                environment_name="test-env-abc123",
                backup=False,
            )

    def test_update_misc_xml_permission_error(
        self, temp_dir: Path, mock_interpreter_path: Path
    ) -> None:
        """Test error handling for permission issues."""
        misc_xml_path = temp_dir / ".idea" / "misc.xml"
        misc_xml_path.parent.mkdir(parents=True)

        # Create directory where file should be (will cause permission error)
        misc_xml_path.mkdir()

        with pytest.raises(ConfigurationError, match="is a directory, not a file"):
            XMLUpdater.update_misc_xml(
                misc_xml_path=misc_xml_path,
                interpreter_path=mock_interpreter_path,
                project_name="test-project",
                environment_name="test-env-abc123",
                backup=False,
            )

    def test_validate_misc_xml_valid(self, mock_misc_xml: Path) -> None:
        """Test validation of valid misc.xml."""
        assert XMLUpdater.validate_misc_xml(mock_misc_xml) is True

    def test_validate_misc_xml_missing(self, temp_dir: Path) -> None:
        """Test validation of missing misc.xml (should be OK)."""
        misc_xml_path = temp_dir / "misc.xml"
        assert XMLUpdater.validate_misc_xml(misc_xml_path) is True

    def test_validate_misc_xml_invalid(self, temp_dir: Path) -> None:
        """Test validation of invalid XML."""
        misc_xml_path = temp_dir / "misc.xml"
        misc_xml_path.write_text("invalid xml")

        assert XMLUpdater.validate_misc_xml(misc_xml_path) is False

    def test_validate_misc_xml_wrong_structure(self, temp_dir: Path) -> None:
        """Test validation of XML with wrong structure."""
        misc_xml_path = temp_dir / "misc.xml"
        misc_xml_path.write_text('<?xml version="1.0"?><root></root>')

        assert XMLUpdater.validate_misc_xml(misc_xml_path) is False

    def test_get_current_interpreter_success(self, mock_misc_xml: Path) -> None:
        """Test getting current interpreter from misc.xml."""
        interpreter = XMLUpdater.get_current_interpreter(mock_misc_xml)
        assert interpreter == "Python 3.11"

    def test_get_current_interpreter_missing_file(self, temp_dir: Path) -> None:
        """Test getting current interpreter from missing file."""
        misc_xml_path = temp_dir / "misc.xml"
        interpreter = XMLUpdater.get_current_interpreter(misc_xml_path)
        assert interpreter is None

    def test_get_current_interpreter_no_prm(self, temp_dir: Path) -> None:
        """Test getting current interpreter when no ProjectRootManager."""
        misc_xml_path = temp_dir / "misc.xml"
        misc_xml_path.write_text('<?xml version="1.0"?><project version="4"></project>')

        interpreter = XMLUpdater.get_current_interpreter(misc_xml_path)
        assert interpreter is None

    def test_get_current_interpreter_invalid_xml(self, temp_dir: Path) -> None:
        """Test getting current interpreter from invalid XML."""
        misc_xml_path = temp_dir / "misc.xml"
        misc_xml_path.write_text("invalid xml")

        interpreter = XMLUpdater.get_current_interpreter(misc_xml_path)
        assert interpreter is None

    def test_xml_formatting(self, temp_dir: Path, mock_interpreter_path: Path) -> None:
        """Test that generated XML is properly formatted."""
        misc_xml_path = temp_dir / ".idea" / "misc.xml"
        misc_xml_path.parent.mkdir(parents=True)

        XMLUpdater.update_misc_xml(
            misc_xml_path=misc_xml_path,
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            backup=False,
        )

        content = misc_xml_path.read_text()

        # Check for proper XML declaration
        assert content.startswith('<?xml version="1.0" encoding="UTF-8"?>')

        # Check for proper indentation (basic check)
        lines = content.split("\n")
        assert any("  <component" in line for line in lines)  # 2-space indentation

    def test_preserve_existing_components(
        self, temp_dir: Path, mock_interpreter_path: Path
    ) -> None:
        """Test that existing components are preserved when updating."""
        misc_xml_path = temp_dir / ".idea" / "misc.xml"
        misc_xml_path.parent.mkdir(parents=True)

        # Create misc.xml with additional component
        initial_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" languageLevel="JDK_11" project-jdk-name="Old Python" project-jdk-type="Python SDK">
    <output url="file://$PROJECT_DIR$/out" />
  </component>
  <component name="OtherComponent">
    <property name="some.setting" value="some.value" />
  </component>
</project>"""
        misc_xml_path.write_text(initial_content)

        XMLUpdater.update_misc_xml(
            misc_xml_path=misc_xml_path,
            interpreter_path=mock_interpreter_path,
            project_name="test-project",
            environment_name="test-env-abc123",
            backup=False,
        )

        # Parse and verify both components exist
        tree = ET.parse(misc_xml_path)
        root = tree.getroot()

        prm = root.find(".//component[@name='ProjectRootManager']")
        assert prm is not None
        assert prm.get("project-jdk-name") == "Poetry (test-env-abc123)"

        other = root.find(".//component[@name='OtherComponent']")
        assert other is not None

        prop = other.find("property")
        assert prop is not None
        assert prop.get("name") == "some.setting"
