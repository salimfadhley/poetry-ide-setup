"""IntelliJ IDEA/PyCharm project detection utilities."""

from pathlib import Path
from typing import Optional

from .exceptions import IdeaDirectoryNotFoundError


class ProjectDetector:
    """Detects IntelliJ IDEA/PyCharm project configuration."""

    @staticmethod
    def find_idea_directory(project_path: Path) -> Path:
        """
        Find the .idea directory in the project.

        Args:
            project_path: Path to search for .idea directory

        Returns:
            Path to the .idea directory

        Raises:
            IdeaDirectoryNotFoundError: If .idea directory is not found
        """
        idea_path = project_path / ".idea"

        if not idea_path.exists():
            raise IdeaDirectoryNotFoundError(
                f"No .idea directory found in {project_path}. "
                "Make sure this is an IntelliJ IDEA or PyCharm project."
            )

        if not idea_path.is_dir():
            raise IdeaDirectoryNotFoundError(
                f".idea exists but is not a directory in {project_path}"
            )

        return idea_path

    @staticmethod
    def get_project_name(idea_path: Path) -> str:
        """
        Get the project name from IDE configuration.

        Args:
            idea_path: Path to the .idea directory

        Returns:
            Project name (from .idea/.name or parent directory name)
        """
        # Try to get name from .idea/.name file
        name_file = idea_path / ".name"
        if name_file.exists() and name_file.is_file():
            try:
                project_name = name_file.read_text(encoding="utf-8").strip()
                if project_name:
                    return project_name
            except (OSError, UnicodeDecodeError):
                pass

        # Fallback to parent directory name
        return idea_path.parent.name

    @staticmethod
    def get_misc_xml_path(idea_path: Path) -> Path:
        """
        Get the path to misc.xml configuration file.

        Args:
            idea_path: Path to the .idea directory

        Returns:
            Path to misc.xml file (may not exist yet)
        """
        return idea_path / "misc.xml"

    @staticmethod
    def validate_project_structure(project_path: Path) -> bool:
        """
        Validate that the project has a proper IntelliJ/PyCharm structure.

        Args:
            project_path: Path to the project directory

        Returns:
            True if the project structure looks valid
        """
        try:
            idea_path = ProjectDetector.find_idea_directory(project_path)

            # Check for some common .idea files that indicate a valid project
            expected_files = [
                "modules.xml",
                "workspace.xml",
                ".gitignore",
            ]

            # At least one of these should exist
            for file_name in expected_files:
                if (idea_path / file_name).exists():
                    return True

            # If none of the expected files exist, it might be a new/minimal project
            # but the .idea directory exists, so we'll consider it valid
            return True

        except IdeaDirectoryNotFoundError:
            return False

    @staticmethod
    def is_python_project(idea_path: Path) -> bool:
        """
        Check if this appears to be a Python project.

        Args:
            idea_path: Path to the .idea directory

        Returns:
            True if project appears to be configured for Python development
        """
        # Check modules.xml for Python module type
        modules_xml = idea_path / "modules.xml"
        if modules_xml.exists():
            try:
                content = modules_xml.read_text(encoding="utf-8")
                if 'type="PYTHON_MODULE"' in content:
                    return True
            except (OSError, UnicodeDecodeError):
                pass

        # Check workspace.xml for Python-related settings
        workspace_xml = idea_path / "workspace.xml"
        if workspace_xml.exists():
            try:
                content = workspace_xml.read_text(encoding="utf-8")
                python_indicators = [
                    "PythonLanguage",
                    "Python SDK",
                    "PyInterpreter",
                    "python-ce",
                ]
                if any(indicator in content for indicator in python_indicators):
                    return True
            except (OSError, UnicodeDecodeError):
                pass

        # Check misc.xml for Python SDK configuration
        misc_xml = idea_path / "misc.xml"
        if misc_xml.exists():
            try:
                content = misc_xml.read_text(encoding="utf-8")
                if "Python SDK" in content or "python" in content.lower():
                    return True
            except (OSError, UnicodeDecodeError):
                pass

        # If we can't determine from IDE files, assume it could be Python
        # (user might be setting up a new project)
        return True
