"""Main entry point for poetry-ide-setup CLI."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .core import setup_ide_configuration
from .exceptions import PoetryIdeSetupError

app = typer.Typer(
    name="ide-setup",
    help="Configure IntelliJ IDEA and PyCharm to use Poetry's Python interpreter",
    add_completion=False,
)
console = Console()


@app.command()
def main(
    project_path: Optional[Path] = typer.Option(
        None,
        "--project-path",
        "-p",
        help="Path to IntelliJ IDEA/PyCharm project directory (defaults to current directory)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be changed without making any modifications",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing IDE configuration without confirmation",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """Configure IntelliJ IDEA and PyCharm to use Poetry's Python interpreter."""
    
    if verbose:
        console.print("[dim]poetry-ide-setup starting...[/dim]")
    
    try:
        # Use current directory if no project path specified
        target_path = project_path or Path.cwd()
        
        if verbose:
            console.print(f"[dim]Target project path: {target_path}[/dim]")
        
        # Setup IDE configuration
        result = setup_ide_configuration(
            project_path=target_path,
            dry_run=dry_run,
            force=force,
            verbose=verbose,
        )
        
        # Display results
        if dry_run:
            console.print(Panel.fit(
                f"[yellow]DRY RUN - No files were modified[/yellow]\n\n"
                f"Would update: {result.config_file}\n"
                f"Python interpreter: {result.interpreter_path}\n"
                f"Project name: {result.project_name}",
                title="Configuration Preview"
            ))
        else:
            console.print(Panel.fit(
                f"[green]✓ IDE configuration updated successfully[/green]\n\n"
                f"Updated: {result.config_file}\n"
                f"Python interpreter: {result.interpreter_path}\n"
                f"Project name: {result.project_name}",
                title="Success"
            ))
        
    except PoetryIdeSetupError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()