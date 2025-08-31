Here’s the revised specification with poetry-ide-setup as the project name, plus your requirements about Poetry build and Python version support:

⸻

Project Specification: poetry-ide-setup

1. Overview

poetry-ide-setup is a Python package and command-line utility that ensures IntelliJ IDEA and PyCharm projects use the same Python interpreter as the currently active Poetry environment. It eliminates the need for manual SDK configuration in JetBrains IDEs, enabling developers to open a Poetry-managed project in IntelliJ/PyCharm and have it ready to run instantly.

⸻

2. Objectives
   •	Detect the Python interpreter path of the active Poetry environment.
   •	Update IntelliJ IDEA or PyCharm project configuration files to use this interpreter.
   •	Provide a simple CLI entry point (poetry ide-setup) to run inside a Poetry shell.
   •	Operate independently of the IDE GUI (script-based, no plugin installation required).
   •	Support IntelliJ IDEA Ultimate with Python plugin and PyCharm Professional/Community.

⸻

3. Scope

In Scope
•	A Poetry-managed Python package (poetry-ide-setup).
•	A CLI command that:
1.	Queries Poetry for the current environment’s Python interpreter path.
2.	Locates the .idea/ directory of the project.
3.	Updates relevant IDE configuration files (.idea/misc.xml, .idea/.name, possibly .idea/workspace.xml) with the interpreter path.
•	Cross-platform support (Windows, macOS, Linux).
•	Schema-safe XML updates that avoid corrupting IDE configuration.

Out of Scope
•	Configuring global interpreters.
•	Supporting non-Poetry virtual environments (Conda, venv).
•	Live IDE integration while running.

⸻

4. Functional Requirements
    1.	Interpreter Detection
          •	Run poetry env info --path or poetry run which python to obtain interpreter path.
          •	Verify interpreter exists and is executable.
    2.	Project Identification
          •	Confirm .idea/ directory exists.
          •	Derive project name from .idea/.name or folder name.
    3.	Configuration Update
          •	Modify .idea/misc.xml to include correct <component name="ProjectRootManager" …> with interpreter path.
          •	Insert or replace interpreter definition under <project-jdk-name> with a label like Poetry: <env-name>.
          •	Support multiple updates safely (replace if already present).
    4.	CLI Tooling
          •	Installed command: poetry ide-setup.
          •	Optional arguments:
          •	--project-path <path>: specify IntelliJ/PyCharm project location.
          •	--dry-run: show changes without writing.
          •	--force: overwrite existing configuration.
    5.	Validation & Feedback
          •	Print interpreter path and updated configuration file.
          •	Fail with descriptive errors if .idea missing, Poetry not active, or interpreter not found.

⸻

5. Non-Functional Requirements
   •	Language: Python ≥ 3.11.
   •	Package Management: Poetry (build, dependency management, publishing).
   •	Portability: Windows, macOS, Linux.
   •	Compatibility: IntelliJ IDEA 2022+ and PyCharm 2022+.
   •	Reliability: No corruption of .idea files; XML handling must be schema-compliant.
   •	Performance: Run time < 500 ms.

⸻

6. Implementation Details
   •	CLI Framework: typer (preferred) or click.
   •	XML Handling: xml.etree.ElementTree or lxml.
   •	Testing: pytest with fixtures for .idea mock directories.
   •	CI: GitHub Actions running tests on Linux, macOS, Windows.
   •	Distribution: Publish to PyPI under poetry-ide-setup.

⸻

7. Deliverables
    1.	Poetry-managed Python package (pyproject.toml with correct metadata).
    2.	CLI tool poetry ide-setup.
    3.	Documentation and usage examples.
    4.	Automated test suite.
