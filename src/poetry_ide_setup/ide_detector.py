"""Detects JetBrains IDE configurations and SDK storage locations."""

import platform
from pathlib import Path
from typing import Dict, List, Optional


class IdeConfigDetector:
    """Detects JetBrains IDE installation and configuration paths."""

    @staticmethod
    def get_jetbrains_config_base() -> Optional[Path]:
        """Get the base JetBrains configuration directory for the current platform."""
        system = platform.system().lower()

        if system == "darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "JetBrains"
        elif system == "windows":
            return Path.home() / "AppData" / "Roaming" / "JetBrains"
        elif system == "linux":
            # Check new location first
            new_path = Path.home() / ".config" / "JetBrains"
            if new_path.exists():
                return new_path
            # Fall back to old location pattern
            return Path.home()

        return None

    @staticmethod
    def find_ide_installations() -> List[Dict[str, str]]:
        """Find all installed JetBrains IDEs and their configuration directories."""
        base_path = IdeConfigDetector.get_jetbrains_config_base()
        if not base_path or not base_path.exists():
            return []

        installations = []

        # Look for IDE configuration directories
        for item in base_path.iterdir():
            if item.is_dir():
                name = item.name
                ide_type = None

                if name.startswith("IntelliJIdea"):
                    ide_type = "IntelliJ IDEA"
                elif name.startswith("PyCharm"):
                    if "CE" in name:
                        ide_type = "PyCharm Community"
                    else:
                        ide_type = "PyCharm Professional"
                elif name == "IntelliJ":
                    ide_type = "IntelliJ IDEA (Generic)"

                if ide_type:
                    installations.append(
                        {
                            "name": ide_type,
                            "version": name,
                            "config_dir": str(item),
                            "jdk_table": str(item / "options" / "jdk.table.xml"),
                        }
                    )

        return installations

    @staticmethod
    def find_global_sdk_files() -> List[Dict[str, str]]:
        """Find all jdk.table.xml files for installed IDEs."""
        installations = IdeConfigDetector.find_ide_installations()
        sdk_files = []

        for install in installations:
            jdk_table_path = Path(install["jdk_table"])
            exists = jdk_table_path.exists()

            sdk_files.append(
                {
                    "ide": install["name"],
                    "version": install["version"],
                    "path": install["jdk_table"],
                    "exists": str(exists),
                }
            )

        return sdk_files
