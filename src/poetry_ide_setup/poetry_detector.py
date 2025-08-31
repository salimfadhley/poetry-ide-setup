"""Poetry environment detection utilities."""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from .exceptions import InterpreterNotFoundError, PoetryNotFoundError


class PoetryDetector:
    """Detects Poetry environment and Python interpreter information."""

    @staticmethod
    def get_interpreter_path() -> Path:
        """
        Get the Python interpreter path from the active Poetry environment.
        
        Returns:
            Path to the Python interpreter
            
        Raises:
            PoetryNotFoundError: If Poetry is not available
            InterpreterNotFoundError: If Python interpreter cannot be found
        """
        # First try to get environment info from Poetry
        try:
            result = subprocess.run(
                ["poetry", "env", "info", "--path"],
                capture_output=True,
                text=True,
                check=True,
            )
            env_path = Path(result.stdout.strip())
            
            # Construct interpreter path based on platform
            if sys.platform == "win32":
                interpreter_path = env_path / "Scripts" / "python.exe"
            else:
                interpreter_path = env_path / "bin" / "python"
                
            if interpreter_path.exists() and interpreter_path.is_file():
                return interpreter_path
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback: try poetry run which python
        try:
            result = subprocess.run(
                ["poetry", "run", "which", "python"] if sys.platform != "win32" 
                else ["poetry", "run", "where", "python"],
                capture_output=True,
                text=True,
                check=True,
            )
            interpreter_path = Path(result.stdout.strip().split('\n')[0])
            
            if interpreter_path.exists() and interpreter_path.is_file():
                return interpreter_path
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # If we get here, Poetry might not be available
        try:
            subprocess.run(["poetry", "--version"], capture_output=True, check=True)
            raise InterpreterNotFoundError(
                "Poetry is available but no Python interpreter could be detected. "
                "Make sure you're in a Poetry project directory and run 'poetry install' first."
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise PoetryNotFoundError(
                "Poetry is not available. Make sure Poetry is installed and in your PATH."
            )

    @staticmethod
    def get_environment_info() -> Tuple[Path, str]:
        """
        Get Poetry environment information.
        
        Returns:
            Tuple of (interpreter_path, environment_name)
            
        Raises:
            PoetryNotFoundError: If Poetry is not available
            InterpreterNotFoundError: If Python interpreter cannot be found
        """
        interpreter_path = PoetryDetector.get_interpreter_path()
        
        # Try to get environment name from Poetry
        try:
            result = subprocess.run(
                ["poetry", "env", "info"],
                capture_output=True,
                text=True,
                check=True,
            )
            
            # Parse environment name from output
            for line in result.stdout.split('\n'):
                if line.strip().startswith('Name:'):
                    env_name = line.split(':', 1)[1].strip()
                    return interpreter_path, env_name
                    
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback: derive name from interpreter path
        if sys.platform == "win32":
            # On Windows: C:\Users\user\AppData\Local\pypoetry\Cache\virtualenvs\project-name-hash\Scripts\python.exe
            env_name = interpreter_path.parent.parent.name
        else:
            # On Unix: /path/to/virtualenvs/project-name-hash/bin/python
            env_name = interpreter_path.parent.parent.name
        
        return interpreter_path, env_name

    @staticmethod
    def is_poetry_available() -> bool:
        """Check if Poetry is available in the current environment."""
        try:
            subprocess.run(
                ["poetry", "--version"], 
                capture_output=True, 
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def is_in_poetry_project(project_path: Optional[Path] = None) -> bool:
        """
        Check if the current or specified directory is a Poetry project.
        
        Args:
            project_path: Path to check (defaults to current directory)
            
        Returns:
            True if pyproject.toml exists with Poetry configuration
        """
        path = project_path or Path.cwd()
        pyproject_path = path / "pyproject.toml"
        
        if not pyproject_path.exists():
            return False
        
        try:
            content = pyproject_path.read_text(encoding='utf-8')
            return '[tool.poetry]' in content
        except (OSError, UnicodeDecodeError):
            return False