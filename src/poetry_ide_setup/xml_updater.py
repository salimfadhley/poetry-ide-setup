"""XML configuration file updater for IntelliJ IDEA/PyCharm."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from .exceptions import ConfigurationError, XMLParsingError


class XMLUpdater:
    """Updates IntelliJ IDEA/PyCharm XML configuration files."""

    @staticmethod
    def update_misc_xml(
        misc_xml_path: Path,
        interpreter_path: Path,
        project_name: str,
        environment_name: str,
        backup: bool = True,
    ) -> None:
        """
        Update misc.xml with Poetry Python interpreter configuration.
        
        Args:
            misc_xml_path: Path to misc.xml file
            interpreter_path: Path to Python interpreter
            project_name: Name of the project
            environment_name: Name of Poetry environment
            backup: Whether to create backup before modifying
            
        Raises:
            XMLParsingError: If XML cannot be parsed or written
            ConfigurationError: If configuration cannot be updated
        """
        if backup and misc_xml_path.exists():
            XMLUpdater._create_backup(misc_xml_path)
        
        # Try to parse existing misc.xml or create new one
        if misc_xml_path.exists():
            try:
                tree = ET.parse(misc_xml_path)
                root = tree.getroot()
            except ET.ParseError as e:
                raise XMLParsingError(f"Failed to parse {misc_xml_path}: {e}")
        else:
            # Create new misc.xml structure
            root = ET.Element("project", version="4")
            tree = ET.ElementTree(root)
        
        # Update or create ProjectRootManager component
        XMLUpdater._update_project_root_manager(root, interpreter_path, project_name, environment_name)
        
        # Write the updated XML
        try:
            XMLUpdater._write_xml_with_formatting(tree, misc_xml_path)
        except OSError as e:
            raise ConfigurationError(f"Failed to write {misc_xml_path}: {e}")

    @staticmethod
    def _update_project_root_manager(
        root: ET.Element,
        interpreter_path: Path,
        project_name: str,
        environment_name: str,
    ) -> None:
        """Update or create ProjectRootManager component in the XML."""
        
        # Find existing ProjectRootManager or create new one
        prm_component = None
        for component in root.findall("component"):
            if component.get("name") == "ProjectRootManager":
                prm_component = component
                break
        
        if prm_component is None:
            prm_component = ET.SubElement(root, "component", name="ProjectRootManager")
        
        # Set version and language level (defaults that work for most Python projects)
        prm_component.set("version", "2")
        prm_component.set("languageLevel", "JDK_11")  # IntelliJ default
        
        # Set project SDK name - this is the key part for IDE integration
        sdk_name = f"Poetry ({environment_name})"
        prm_component.set("project-jdk-name", sdk_name)
        prm_component.set("project-jdk-type", "Python SDK")
        
        # Add output path if not present
        output_element = prm_component.find("output")
        if output_element is None:
            output_element = ET.SubElement(prm_component, "output")
            output_element.set("url", f"file://$PROJECT_DIR$/out")

    @staticmethod
    def _create_backup(file_path: Path) -> Path:
        """Create a backup of the file before modification."""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        backup_path.write_bytes(file_path.read_bytes())
        return backup_path

    @staticmethod
    def _write_xml_with_formatting(tree: ET.ElementTree, file_path: Path) -> None:
        """Write XML tree to file with proper formatting."""
        # Add XML declaration and formatting
        XMLUpdater._indent_xml(tree.getroot())
        
        # Write with proper encoding and declaration
        with open(file_path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

    @staticmethod
    def _indent_xml(elem: ET.Element, level: int = 0) -> None:
        """Add indentation to XML elements for readable formatting."""
        indent = "  " * level  # 2 spaces per level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = f"\n{indent}  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = f"\n{indent}"
            for child in elem:
                XMLUpdater._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = f"\n{indent}"
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = f"\n{indent}"

    @staticmethod
    def validate_misc_xml(misc_xml_path: Path) -> bool:
        """
        Validate that misc.xml can be parsed and has expected structure.
        
        Args:
            misc_xml_path: Path to misc.xml file
            
        Returns:
            True if XML is valid and parseable
        """
        if not misc_xml_path.exists():
            return True  # Missing file is OK, we can create it
        
        try:
            tree = ET.parse(misc_xml_path)
            root = tree.getroot()
            
            # Check basic structure
            if root.tag != "project":
                return False
            
            # Check version attribute
            version = root.get("version")
            if version is None:
                return False
            
            return True
            
        except ET.ParseError:
            return False

    @staticmethod
    def get_current_interpreter(misc_xml_path: Path) -> Optional[str]:
        """
        Get the currently configured Python interpreter from misc.xml.
        
        Args:
            misc_xml_path: Path to misc.xml file
            
        Returns:
            Current interpreter SDK name or None if not configured
        """
        if not misc_xml_path.exists():
            return None
        
        try:
            tree = ET.parse(misc_xml_path)
            root = tree.getroot()
            
            for component in root.findall("component"):
                if component.get("name") == "ProjectRootManager":
                    return component.get("project-jdk-name")
            
            return None
            
        except ET.ParseError:
            return None