"""XML configuration file updater for IntelliJ IDEA/PyCharm."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Any, cast

from .exceptions import ConfigurationError, XMLParsingError


class XMLUpdater:
    """Updates IntelliJ IDEA/PyCharm XML configuration files."""

    @staticmethod
    def update_misc_xml(
        misc_xml_path: Path,
        interpreter_path: Path,
        project_name: str,
        environment_name: str,
        python_version: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """
        Update misc.xml with Poetry Python interpreter configuration.

        Args:
            misc_xml_path: Path to misc.xml file
            interpreter_path: Path to Python interpreter
            project_name: Name of the project
            environment_name: Name of Poetry environment
            python_version: Optional Python version string (e.g., "3.12")
            backup: Whether to create backup before modifying

        Raises:
            XMLParsingError: If XML cannot be parsed or written
            ConfigurationError: If configuration cannot be updated
        """
        if backup and misc_xml_path.exists():
            XMLUpdater._create_backup(misc_xml_path)

        # Try to parse existing misc.xml or create new one
        if misc_xml_path.exists():
            if misc_xml_path.is_dir():
                raise ConfigurationError(f"{misc_xml_path} is a directory, not a file")
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
        XMLUpdater._update_project_root_manager(
            root, interpreter_path, project_name, environment_name, python_version
        )

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
        python_version: Optional[str] = None,
    ) -> None:
        """Update or create ProjectRootManager component in the XML."""

        # Find existing ProjectRootManager or create new one
        prm_component = None
        for component in root.findall("component"):
            if component.get("name") == "ProjectRootManager":
                prm_component = component
                break

        if prm_component is None:
            # Add comment before the component to identify it was configured by poetry-ide-setup
            comment = ET.Comment(" Configured by poetry-ide-setup ")
            root.append(comment)
            prm_component = ET.SubElement(root, "component", name="ProjectRootManager")

        # Set version and language level (defaults that work for most Python projects)
        prm_component.set("version", "2")
        prm_component.set("languageLevel", "JDK_11")  # IntelliJ default

        # Set project SDK name - this is the key part for IDE integration
        sdk_name = f"Python {python_version} {project_name}"
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
    def _write_xml_with_formatting(tree: Any, file_path: Path) -> None:
        """Write XML tree to file with proper formatting."""
        # Add XML declaration and formatting
        # getroot may return None per typeshed; guard and cast for mypy
        root = tree.getroot()
        if root is None:
            raise XMLParsingError("XML tree has no root element")
        XMLUpdater._indent_xml(root)

        # Write with proper encoding and declaration
        with open(file_path, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding="utf-8", xml_declaration=False)

    @staticmethod
    def _indent_xml(elem: Optional[ET.Element], level: int = 0) -> None:
        """Add indentation to XML elements for readable formatting."""
        if elem is None:
            return
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

    @staticmethod
    def list_all_sdks(idea_path: Path) -> list[str]:
        """
        List all currently configured Python SDKs from IDE configuration.

        Args:
            idea_path: Path to the .idea directory

        Returns:
            List of SDK names found in configuration files
        """
        sdks = []

        # Check misc.xml for current project SDK
        misc_xml_path = idea_path / "misc.xml"
        current_sdk = XMLUpdater.get_current_interpreter(misc_xml_path)
        if current_sdk:
            sdks.append(f"Project SDK: {current_sdk}")

        # Check for additional SDK configurations in other files
        # Look for jdk.table.xml in the IDE config directory (if accessible)
        workspace_xml = idea_path / "workspace.xml"
        if workspace_xml.exists():
            try:
                import xml.etree.ElementTree as ET

                tree = ET.parse(workspace_xml)
                root = tree.getroot()

                # Look for SDK references in workspace settings
                for component in root.findall(".//component"):
                    for property_elem in component.findall(".//property"):
                        name = property_elem.get("name", "")
                        value = property_elem.get("value", "")
                        if "sdk" in name.lower() and "python" in value.lower():
                            if value not in [sdk.split(": ", 1)[-1] for sdk in sdks]:
                                sdks.append(f"Workspace SDK: {value}")

            except (ET.ParseError, OSError):
                pass

        return sdks if sdks else ["No Python SDKs configured"]

    @staticmethod
    def list_global_sdks(jdk_table_path: Path) -> list[dict[str, str]]:
        """List all Python SDKs from a global jdk.table.xml file.

        Args:
            jdk_table_path: Path to the jdk.table.xml file

        Returns:
            List of dictionaries with 'name', 'version', and 'path' keys
        """
        if not jdk_table_path.exists():
            return [
                {
                    "name": "Error",
                    "version": "N/A",
                    "path": f"Global SDK file not found: {jdk_table_path}",
                }
            ]

        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(jdk_table_path)
            root = tree.getroot()

            sdks = []

            # Look for JDK entries in the ProjectJdkTable component
            for component in root.findall(".//component[@name='ProjectJdkTable']"):
                for jdk in component.findall(".//jdk"):
                    jdk_type = None
                    jdk_name = None
                    jdk_version = None
                    jdk_home = None

                    # Extract JDK information
                    type_elem = jdk.find("type")
                    if type_elem is not None:
                        jdk_type = type_elem.get("value", "")

                    name_elem = jdk.find("name")
                    if name_elem is not None:
                        jdk_name = name_elem.get("value", "")

                    version_elem = jdk.find("version")
                    if version_elem is not None:
                        jdk_version = version_elem.get("value", "")

                    homepath_elem = jdk.find("homePath")
                    if homepath_elem is not None:
                        jdk_home = homepath_elem.get("value", "")

                    # Only include Python SDKs
                    if jdk_type and "python" in jdk_type.lower() and jdk_name:
                        # Clean up home path for display
                        home_display = (
                            jdk_home.replace("$USER_HOME$", "~") if jdk_home else "N/A"
                        )

                        sdks.append(
                            {
                                "name": jdk_name,
                                "version": jdk_version or "Unknown",
                                "path": home_display,
                            }
                        )

            return (
                sdks
                if sdks
                else [
                    {
                        "name": "No Python SDKs",
                        "version": "N/A",
                        "path": "None found in global configuration",
                    }
                ]
            )

        except (ET.ParseError, OSError, Exception) as e:
            return [
                {
                    "name": "Error",
                    "version": "N/A",
                    "path": f"Error reading global SDK file: {e}",
                }
            ]

    @staticmethod
    def register_global_sdk(
        jdk_table_path: Path,
        sdk_name: str,
        interpreter_path: Path,
        python_version: str,
        backup: bool = True,
    ) -> None:
        """Register a Python SDK in the global jdk.table.xml file.

        Args:
            jdk_table_path: Path to the jdk.table.xml file
            sdk_name: Name for the SDK (e.g., "Python 3.12 myproject")
            interpreter_path: Path to Python interpreter
            python_version: Python version (e.g., "3.12.1")
            backup: Whether to create backup before modifying

        Raises:
            XMLParsingError: If XML cannot be parsed or written
            ConfigurationError: If configuration cannot be updated
        """
        if backup and jdk_table_path.exists():
            XMLUpdater._create_backup(jdk_table_path)

        # Parse existing jdk.table.xml or create new structure
        if jdk_table_path.exists():
            if jdk_table_path.is_dir():
                raise ConfigurationError(f"{jdk_table_path} is a directory, not a file")
            try:
                tree = ET.parse(jdk_table_path)
                root = tree.getroot()
            except ET.ParseError as e:
                raise XMLParsingError(f"Failed to parse {jdk_table_path}: {e}")
        else:
            # Create new jdk.table.xml structure
            root = ET.Element("application")
            tree = ET.ElementTree(root)

        # Find or create ProjectJdkTable component
        jdk_table_component = None
        for component in root.findall("component"):
            if component.get("name") == "ProjectJdkTable":
                jdk_table_component = component
                break

        if jdk_table_component is None:
            jdk_table_component = ET.SubElement(
                root, "component", name="ProjectJdkTable"
            )

        # Check if SDK already exists
        for jdk in jdk_table_component.findall(".//jdk"):
            name_elem = jdk.find("name")
            if name_elem is not None and name_elem.get("value") == sdk_name:
                # SDK already exists, update it
                XMLUpdater._update_jdk_entry(
                    jdk, sdk_name, interpreter_path, python_version
                )
                break
        else:
            # Create new SDK entry
            XMLUpdater._create_jdk_entry(
                jdk_table_component, sdk_name, interpreter_path, python_version
            )

        # Write the updated XML
        try:
            XMLUpdater._write_xml_with_formatting(tree, jdk_table_path)
        except OSError as e:
            raise ConfigurationError(f"Failed to write {jdk_table_path}: {e}")

    @staticmethod
    def _create_jdk_entry(
        parent: ET.Element,
        sdk_name: str,
        interpreter_path: Path,
        python_version: str,
    ) -> None:
        """Create a new JDK entry in the ProjectJdkTable."""
        # Add comment before the jdk entry to identify it was created by poetry-ide-setup
        comment = ET.Comment(f" Added by poetry-ide-setup - {sdk_name} ")
        parent.append(comment)

        jdk = ET.SubElement(parent, "jdk", version="2")

        # Name
        name_elem = ET.SubElement(jdk, "name")
        name_elem.set("value", sdk_name)

        # Type
        type_elem = ET.SubElement(jdk, "type")
        type_elem.set("value", "Python SDK")

        # Version
        version_elem = ET.SubElement(jdk, "version")
        version_elem.set("value", python_version)

        # Home path
        home_elem = ET.SubElement(jdk, "homePath")
        # Use $USER_HOME$ for paths in user's home directory
        home_path_str = str(interpreter_path)
        user_home = str(Path.home())
        if home_path_str.startswith(user_home):
            home_path_str = home_path_str.replace(user_home, "$USER_HOME$")
        home_elem.set("value", home_path_str)

        # Add roots element for completeness (can be empty)
        roots_elem = ET.SubElement(jdk, "roots")
        annotations_elem = ET.SubElement(roots_elem, "annotationsPath")
        ET.SubElement(annotations_elem, "root", type="composite")
        classpath_elem = ET.SubElement(roots_elem, "classPath")
        ET.SubElement(classpath_elem, "root", type="composite")

    @staticmethod
    def _update_jdk_entry(
        jdk: ET.Element,
        sdk_name: str,
        interpreter_path: Path,
        python_version: str,
    ) -> None:
        """Update an existing JDK entry."""
        # Update version
        version_elem = jdk.find("version")
        if version_elem is not None:
            version_elem.set("value", python_version)

        # Update home path
        home_elem = jdk.find("homePath")
        if home_elem is not None:
            home_path_str = str(interpreter_path)
            user_home = str(Path.home())
            if home_path_str.startswith(user_home):
                home_path_str = home_path_str.replace(user_home, "$USER_HOME$")
            home_elem.set("value", home_path_str)
