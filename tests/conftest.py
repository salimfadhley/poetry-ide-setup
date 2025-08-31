"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_poetry_project(temp_dir: Path) -> Path:
    """Create a mock Poetry project structure."""
    # Create pyproject.toml with Poetry config
    pyproject_content = """[tool.poetry]
name = "test-project"
version = "0.1.0"
description = "A test project"

[tool.poetry.dependencies]
python = "^3.11"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
    (temp_dir / "pyproject.toml").write_text(pyproject_content)
    return temp_dir


@pytest.fixture
def mock_idea_project(temp_dir: Path) -> Path:
    """Create a mock IntelliJ IDEA project structure."""
    idea_dir = temp_dir / ".idea"
    idea_dir.mkdir()
    
    # Create .name file
    (idea_dir / ".name").write_text("test-project")
    
    # Create modules.xml
    modules_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/test-project.iml" filepath="$PROJECT_DIR$/.idea/test-project.iml" />
    </modules>
  </component>
</project>"""
    (idea_dir / "modules.xml").write_text(modules_content)
    
    # Create workspace.xml
    workspace_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="PropertiesComponent">
    <property name="settings.editor.selected.configurable" value="preferences.general" />
  </component>
</project>"""
    (idea_dir / "workspace.xml").write_text(workspace_content)
    
    # Create .gitignore
    (idea_dir / ".gitignore").write_text("""shelf/
workspace.xml
""")
    
    return temp_dir


@pytest.fixture
def mock_idea_python_project(mock_idea_project: Path) -> Path:
    """Create a mock IntelliJ IDEA Python project structure."""
    idea_dir = mock_idea_project / ".idea"
    
    # Create modules.xml with Python module type
    modules_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/test-project.iml" filepath="$PROJECT_DIR$/.idea/test-project.iml" />
    </modules>
  </component>
</project>"""
    (idea_dir / "modules.xml").write_text(modules_content)
    
    # Create test-project.iml with Python module type
    iml_content = """<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$" />
    <orderEntry type="inheritedJdk" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
</module>"""
    (idea_dir / "test-project.iml").write_text(iml_content)
    
    return mock_idea_project


@pytest.fixture
def mock_misc_xml(temp_dir: Path) -> Path:
    """Create a mock misc.xml file."""
    idea_dir = temp_dir / ".idea"
    idea_dir.mkdir(exist_ok=True)
    
    misc_content = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" languageLevel="JDK_11" project-jdk-name="Python 3.11" project-jdk-type="Python SDK">
    <output url="file://$PROJECT_DIR$/out" />
  </component>
</project>"""
    misc_xml_path = idea_dir / "misc.xml"
    misc_xml_path.write_text(misc_content)
    
    return misc_xml_path


@pytest.fixture
def mock_interpreter_path(temp_dir: Path) -> Path:
    """Create a mock Python interpreter."""
    venv_dir = temp_dir / "venv"
    bin_dir = venv_dir / "bin"
    bin_dir.mkdir(parents=True)
    
    python_path = bin_dir / "python"
    python_path.write_text("#!/usr/bin/env python3\nprint('Mock Python interpreter')")
    python_path.chmod(0o755)
    
    return python_path