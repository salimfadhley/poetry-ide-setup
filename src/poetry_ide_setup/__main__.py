"""Main entry point for poetry-ide-setup CLI."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .core import setup_ide_configuration
from .exceptions import PoetryIdeSetupError

console = Console()


@click.group(invoke_without_command=True)
@click.option(
    "--project-path",
    "-p",
    type=str,
    help="Path to IntelliJ IDEA/PyCharm project directory (defaults to current directory)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be changed without making any modifications",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing IDE configuration without confirmation",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def main(
    ctx: click.Context,
    project_path: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
    verbose: bool = False,
) -> None:
    """Configure IntelliJ IDEA and PyCharm to use Poetry's Python interpreter."""
    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["project_path"] = project_path
    ctx.obj["dry_run"] = dry_run
    ctx.obj["force"] = force
    ctx.obj["verbose"] = verbose

    # If no subcommand was provided, run the default setup behavior
    if ctx.invoked_subcommand is None:
        _run_setup(project_path, dry_run, force, verbose)


def _run_setup(
    project_path: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
    verbose: bool = False,
) -> None:
    """Run the default IDE setup configuration."""

    if verbose:
        console.print("[dim]poetry-ide-setup starting...[/dim]")

    try:
        # Use current directory if no project path specified
        target_path = Path(project_path) if project_path else Path.cwd()

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
            console.print(
                Panel.fit(
                    f"[yellow]DRY RUN - No files were modified[/yellow]\n\n"
                    f"Would update: {result.config_file}\n"
                    f"Python interpreter: {result.interpreter_path}\n"
                    f"Python SDK name: {result.python_sdk_name}\n"
                    f"Project name: {result.project_name}",
                    title="Configuration Preview",
                )
            )
        else:
            console.print(
                Panel.fit(
                    f"[green]✓ IDE configuration updated successfully[/green]\n\n"
                    f"Updated: {result.config_file}\n"
                    f"Python interpreter: {result.interpreter_path}\n"
                    f"Python SDK name: {result.python_sdk_name}\n"
                    f"Project name: {result.project_name}",
                    title="Success",
                )
            )

    except PoetryIdeSetupError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List all Python SDKs from the currently running IDE."""
    project_path = ctx.obj.get("project_path")
    verbose = ctx.obj.get("verbose", False)

    try:
        from .runtime_detector import RuntimeIdeDetector
        from .xml_updater import XMLUpdater
        from .project_detector import ProjectDetector

        # Detect the currently running IDE
        context = RuntimeIdeDetector.detect_jetbrains_context()

        if not context["ide"] or context["ide"] == "JetBrains (unknown product)":
            console.print("[yellow]⚠️  Not running in a detected JetBrains IDE[/yellow]")
            console.print("Falling back to project-level SDK detection...")

            # Fallback: show project-level SDKs (legacy string format)
            target_path = Path(project_path) if project_path else Path.cwd()
            idea_path = ProjectDetector.find_idea_directory(target_path)
            sdk_strings = XMLUpdater.list_all_sdks(idea_path)

            # Convert legacy format to table format for consistency
            table_sdks = []
            for sdk_str in sdk_strings:
                table_sdks.append({"name": sdk_str, "version": "N/A", "path": "N/A"})
            title = "Project Python SDKs"
        else:
            console.print(f"🔍 Listing Python SDKs from {context['ide']}...")

            if verbose:
                console.print(
                    f"[dim]IDE config directory: {context['config_dir']}[/dim]"
                )

            # Get SDKs from the active IDE's global configuration
            jdk_table_path = Path(context["config_dir"]) / "options" / "jdk.table.xml"
            table_sdks = XMLUpdater.list_global_sdks(jdk_table_path)
            title = f"{context['ide']} Python SDKs"

            # Add current project SDK if available
            try:
                target_path = Path(project_path) if project_path else Path.cwd()
                idea_path = ProjectDetector.find_idea_directory(target_path)
                current_sdk = XMLUpdater.get_current_interpreter(idea_path / "misc.xml")
                if current_sdk:
                    # Insert project SDK at the beginning
                    table_sdks.insert(
                        0,
                        {
                            "name": f"{current_sdk}",  # Current project SDK
                            "version": "Current Project",
                            "path": "Configured in misc.xml",
                        },
                    )
            except (OSError, PoetryIdeSetupError):
                pass  # Ignore project detection errors

        # Create and populate table
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=False)
        table.add_column("Version", style="green", max_width=20)
        table.add_column("Path", style="yellow", no_wrap=False)

        # Add rows to table using Text objects to avoid markup interpretation
        for sdk in table_sdks:
            table.add_row(Text(sdk["name"]), Text(sdk["version"]), Text(sdk["path"]))

        console.print(table)

    except (PoetryIdeSetupError, OSError) as e:
        # Use markup=False to prevent Rich markup errors with paths containing brackets
        console.print("Error listing SDKs:", str(e), style="red", markup=False)
        if verbose:
            console.print_exception()
        sys.exit(1)
    except ImportError as e:
        console.print("Missing dependency:", str(e), style="red", markup=False)
        sys.exit(1)


@main.command()
@click.pass_context
def files(ctx: click.Context) -> None:
    """Show the location of IDE configuration files."""
    project_path = ctx.obj.get("project_path")
    verbose = ctx.obj.get("verbose", False)

    try:
        from .project_detector import ProjectDetector
        from .ide_detector import IdeConfigDetector

        target_path = Path(project_path) if project_path else Path.cwd()

        if verbose:
            console.print(
                f"[dim]Searching for IDE configuration in: {target_path}[/dim]"
            )

        # Project-level configuration
        idea_path = ProjectDetector.find_idea_directory(target_path)
        misc_xml_path = idea_path / "misc.xml"
        workspace_xml_path = idea_path / "workspace.xml"

        project_files = [
            f"Project Directory: {idea_path}",
            f"Project Config: {misc_xml_path} {'(exists)' if misc_xml_path.exists() else '(missing)'}",
            f"Workspace Config: {workspace_xml_path} {'(exists)' if workspace_xml_path.exists() else '(missing)'}",
        ]

        # Global SDK configuration
        global_sdk_files = IdeConfigDetector.find_global_sdk_files()

        # Display project-level files
        console.print(
            Panel.fit(
                "\n".join([f"• {file_info}" for file_info in project_files]),
                title="Project Configuration Files",
                title_align="left",
            )
        )

        # Display global SDK files
        if global_sdk_files:
            global_info = []
            for sdk_file in global_sdk_files:
                status = "exists" if sdk_file["exists"] else "missing"
                global_info.append(f"{sdk_file['ide']}: {sdk_file['path']} ({status})")

            console.print(
                Panel.fit(
                    "\n".join([f"• {info}" for info in global_info]),
                    title="Global SDK Configuration Files",
                    title_align="left",
                )
            )
        else:
            console.print("[yellow]No JetBrains IDE installations detected[/yellow]")

    except Exception as e:
        console.print(f"[red]Error finding configuration files: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
