"""Core functionality for poetry-ide-setup."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rich.console import Console

from .exceptions import ConfigurationError, IdeaDirectoryNotFoundError
from .poetry_detector import PoetryDetector
from .project_detector import ProjectDetector
from .xml_updater import XMLUpdater

console = Console()


@dataclass
class SetupResult:
    """Result of IDE setup operation."""
    
    interpreter_path: Path
    project_name: str
    environment_name: str
    config_file: Path
    was_updated: bool
    previous_interpreter: Optional[str] = None


def setup_ide_configuration(
    project_path: Path,
    dry_run: bool = False,
    force: bool = False,
    verbose: bool = False,
) -> SetupResult:
    """
    Set up IDE configuration for Poetry project.
    
    Args:
        project_path: Path to the project directory
        dry_run: If True, don't make any changes
        force: If True, overwrite existing configuration
        verbose: If True, show detailed output
        
    Returns:
        SetupResult with details of the operation
        
    Raises:
        PoetryIdeSetupError: If setup fails for any reason
    """
    if verbose:
        console.print(f"[dim]Setting up IDE configuration for: {project_path}[/dim]")
    
    # Validate Poetry availability
    if not PoetryDetector.is_poetry_available():
        from .exceptions import PoetryNotFoundError
        raise PoetryNotFoundError(
            "Poetry is not available. Make sure Poetry is installed and in your PATH."
        )
    
    # Check if we're in a Poetry project
    if not PoetryDetector.is_in_poetry_project(project_path):
        if verbose:
            console.print("[yellow]Warning: No pyproject.toml with Poetry configuration found[/yellow]")
    
    # Detect Poetry environment
    if verbose:
        console.print("[dim]Detecting Poetry environment...[/dim]")
    
    interpreter_path, environment_name = PoetryDetector.get_environment_info()
    
    if verbose:
        console.print(f"[dim]Found interpreter: {interpreter_path}[/dim]")
        console.print(f"[dim]Environment name: {environment_name}[/dim]")
    
    # Find .idea directory
    if verbose:
        console.print("[dim]Looking for .idea directory...[/dim]")
    
    try:
        idea_path = ProjectDetector.find_idea_directory(project_path)
    except IdeaDirectoryNotFoundError as e:
        raise e
    
    # Get project information
    project_name = ProjectDetector.get_project_name(idea_path)
    misc_xml_path = ProjectDetector.get_misc_xml_path(idea_path)
    
    if verbose:
        console.print(f"[dim]Project name: {project_name}[/dim]")
        console.print(f"[dim]Configuration file: {misc_xml_path}[/dim]")
    
    # Validate project structure
    if not ProjectDetector.validate_project_structure(project_path):
        if verbose:
            console.print("[yellow]Warning: Project structure validation failed[/yellow]")
    
    # Check if this appears to be a Python project
    if not ProjectDetector.is_python_project(idea_path):
        if verbose:
            console.print("[yellow]Warning: Project doesn't appear to be configured for Python[/yellow]")
    
    # Check current configuration
    current_interpreter = XMLUpdater.get_current_interpreter(misc_xml_path)
    if verbose and current_interpreter:
        console.print(f"[dim]Current interpreter: {current_interpreter}[/dim]")
    
    # Check if we need to update (unless force is specified)
    expected_sdk_name = f"Poetry ({environment_name})"
    needs_update = (
        force or 
        current_interpreter != expected_sdk_name or
        not misc_xml_path.exists()
    )
    
    if not needs_update:
        if verbose:
            console.print("[green]Configuration is already up to date[/green]")
        return SetupResult(
            interpreter_path=interpreter_path,
            project_name=project_name,
            environment_name=environment_name,
            config_file=misc_xml_path,
            was_updated=False,
            previous_interpreter=current_interpreter,
        )
    
    # Update configuration (unless dry run)
    if not dry_run:
        if verbose:
            console.print("[dim]Updating IDE configuration...[/dim]")
        
        # Validate XML before attempting update
        if misc_xml_path.exists() and not XMLUpdater.validate_misc_xml(misc_xml_path):
            raise ConfigurationError(
                f"Existing {misc_xml_path} appears to be corrupted. "
                "Please fix or delete the file and try again."
            )
        
        try:
            XMLUpdater.update_misc_xml(
                misc_xml_path=misc_xml_path,
                interpreter_path=interpreter_path,
                project_name=project_name,
                environment_name=environment_name,
                backup=True,
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to update IDE configuration: {e}")
    
    return SetupResult(
        interpreter_path=interpreter_path,
        project_name=project_name,
        environment_name=environment_name,
        config_file=misc_xml_path,
        was_updated=True,
        previous_interpreter=current_interpreter,
    )