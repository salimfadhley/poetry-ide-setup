# poetry-ide-setup

Automatically configure IntelliJ IDEA and PyCharm to use Poetry's Python interpreter.

## Overview

`poetry-ide-setup` eliminates the manual process of configuring Python interpreters in JetBrains IDEs when working with Poetry-managed projects. Simply run `poetry run ide-setup` and your IDE will be configured to use the correct Python interpreter from your Poetry environment.

## Features

- 🔍 **Automatic Detection**: Finds your Poetry environment and Python interpreter
- 🛠️ **IDE Configuration**: Updates IntelliJ IDEA and PyCharm project settings
- 🔒 **Safe Updates**: Creates backups and validates XML before modification  
- 🚀 **Cross-Platform**: Works on Windows, macOS, and Linux
- 💡 **Smart Defaults**: Minimal configuration required
- 🔄 **Idempotent**: Safe to run multiple times

## Installation

**Important**: This tool must be installed within a Poetry project as it requires access to Poetry's environment information.

Add to your Poetry project as a development dependency:

```bash
poetry add --group dev poetry-ide-setup
```

**Note**: Do not install globally with `pipx` as the tool needs to run within your Poetry project's context to detect the correct Python interpreter and environment.

## Usage

### Basic Usage

Navigate to your Poetry project directory and run:

```bash
poetry run ide-setup
```

This will:
1. Detect your Poetry environment's Python interpreter
2. Find your IDE project configuration in `.idea/`
3. Update `.idea/misc.xml` with the correct interpreter settings

### Command Options

```bash
# Specify a different project directory
poetry run ide-setup --project-path /path/to/your/project

# Preview changes without making modifications
poetry run ide-setup --dry-run

# Force update even if configuration appears current
poetry run ide-setup --force

# Show detailed output
poetry run ide-setup --verbose

# Get help
poetry run ide-setup --help
```

### Example Output

```bash
$ poetry run ide-setup --verbose
poetry-ide-setup starting...
Detecting Poetry environment...
Found interpreter: /home/user/.cache/pypoetry/virtualenvs/myproject-abc123/bin/python
Environment name: myproject-abc123
Looking for .idea directory...
Project name: myproject
Configuration file: /home/user/myproject/.idea/misc.xml
Updating IDE configuration...

✓ IDE configuration updated successfully

Updated: /home/user/myproject/.idea/misc.xml
Python interpreter: /home/user/.cache/pypoetry/virtualenvs/myproject-abc123/bin/python  
Project name: myproject
```

## Requirements

- Python ≥ 3.11
- Poetry installed and available in PATH
- IntelliJ IDEA Ultimate (with Python plugin) or PyCharm Professional/Community
- An existing Poetry project with `.idea/` directory

## How It Works

1. **Poetry Detection**: Runs `poetry env info --path` to locate your virtual environment
2. **Project Discovery**: Finds the `.idea/` directory and validates project structure
3. **Configuration Update**: Safely modifies `.idea/misc.xml` to reference the Poetry interpreter
4. **Backup & Validation**: Creates backups and ensures XML remains valid

The tool updates the `ProjectRootManager` component in your IDE configuration:

```xml
<component name="ProjectRootManager" 
           version="2" 
           languageLevel="JDK_11" 
           project-jdk-name="Poetry (myproject-abc123)" 
           project-jdk-type="Python SDK">
  <output url="file://$PROJECT_DIR$/out" />
</component>
```

## Troubleshooting

### Common Issues

**"Poetry is not available"**
- Ensure Poetry is installed: `poetry --version`
- Make sure Poetry is in your PATH
- Try running from your project directory

**"No .idea directory found"**  
- Open your project in IntelliJ IDEA or PyCharm first
- Ensure you're in the correct project directory
- Use `--project-path` to specify the location

**"No Python interpreter could be detected"**
- Run `poetry install` to set up your environment
- Ensure you're in a Poetry project directory
- Check that `poetry env info` shows your environment

### Getting Help

- Use `--verbose` flag for detailed output
- Check the generated backup files (`.xml.backup`)
- Ensure your `.idea/misc.xml` is not corrupted

## Development

See [CLAUDE.md](CLAUDE.md) for development setup and contribution guidelines.

## License

MIT License

## Related Projects

- [Poetry](https://python-poetry.org/) - Python dependency management
- [IntelliJ IDEA](https://www.jetbrains.com/idea/) - JetBrains IDE
- [PyCharm](https://www.jetbrains.com/pycharm/) - Python IDE