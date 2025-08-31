"""Detects the currently running JetBrains IDE and its configuration directory."""

import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class RuntimeIdeDetector:
    """Detects which JetBrains IDE is currently running this process."""

    @staticmethod
    def detect_jetbrains_context() -> Dict[str, Any]:
        """Detect if running under a JetBrains IDE and identify which one.

        Returns:
            Dictionary with detection results containing:
            - ide: IDE name (PyCharm, IntelliJ IDEA, or None)
            - hosted: Whether running under PYCHARM_HOSTED
            - env: JetBrains-related environment variables
            - trace: Process trace (if psutil available)
            - config_dir: Path to the IDE's configuration directory (if detected)
        """
        # Check JetBrains environment variables
        jb_vars = {k: v for k, v in os.environ.items() if k.startswith("PYCHARM_")}
        hosted = "PYCHARM_HOSTED" in os.environ

        result: Dict[str, Any] = {
            "ide": None,
            "hosted": hosted,
            "env": jb_vars,
            "trace": [],
            "config_dir": None,
        }

        # Try process tree inspection if psutil is available
        if PSUTIL_AVAILABLE:
            try:
                p: Optional[Any] = psutil.Process()
                trace = []

                while p:
                    exe = (p.exe() or "").lower()
                    name = (p.name() or "").lower()
                    try:
                        cmd = " ".join(p.cmdline()).lower()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        cmd = ""

                    token = exe or name or cmd
                    trace.append(token)

                    # Check for IDE-specific patterns
                    if any(x in token for x in ("pycharm", "idea", "intellij")):
                        if "pycharm" in token:
                            result["ide"] = "PyCharm"
                            result["config_dir"] = (
                                RuntimeIdeDetector._find_pycharm_config()
                            )
                            break
                        elif "idea" in token or "intellij" in token:
                            result["ide"] = "IntelliJ IDEA"
                            result["config_dir"] = (
                                RuntimeIdeDetector._find_intellij_config()
                            )
                            break

                    try:
                        p = p.parent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break

                result["trace"] = trace

            except Exception:
                # If process inspection fails, continue with fallback detection
                pass

        # Fallback: could still be JetBrains runner, but IDE unknown
        if not result["ide"] and (hosted or jb_vars):
            result["ide"] = "JetBrains (unknown product)"

        return result

    @staticmethod
    def _find_pycharm_config() -> Optional[str]:
        """Find PyCharm configuration directory."""
        base_path = RuntimeIdeDetector._get_jetbrains_config_base()
        if not base_path:
            return None

        # Look for PyCharm directories, prefer newer versions
        pycharm_dirs = []
        for item in base_path.iterdir():
            if item.is_dir() and item.name.startswith("PyCharm"):
                pycharm_dirs.append(item)

        if pycharm_dirs:
            # Sort by name to get the latest version
            pycharm_dirs.sort(key=lambda x: x.name, reverse=True)
            return str(pycharm_dirs[0])

        return None

    @staticmethod
    def _find_intellij_config() -> Optional[str]:
        """Find IntelliJ IDEA configuration directory."""
        base_path = RuntimeIdeDetector._get_jetbrains_config_base()
        if not base_path:
            return None

        # Look for IntelliJ directories, prefer newer versions
        intellij_dirs = []
        for item in base_path.iterdir():
            if item.is_dir() and (
                item.name.startswith("IntelliJIdea") or item.name == "IntelliJ"
            ):
                intellij_dirs.append(item)

        if intellij_dirs:
            # Sort by name to get the latest version, with specific version numbers first
            intellij_dirs.sort(key=lambda x: (len(x.name), x.name), reverse=True)
            return str(intellij_dirs[0])

        return None

    @staticmethod
    def _get_jetbrains_config_base() -> Optional[Path]:
        """Get the base JetBrains configuration directory for the current platform."""
        system = platform.system().lower()

        if system == "darwin":  # macOS
            path = Path.home() / "Library" / "Application Support" / "JetBrains"
        elif system == "windows":
            path = Path.home() / "AppData" / "Roaming" / "JetBrains"
        elif system == "linux":
            # Check new location first
            new_path = Path.home() / ".config" / "JetBrains"
            if new_path.exists():
                path = new_path
            else:
                # Fall back to old location - return home for old-style detection
                path = Path.home()
        else:
            return None

        return path if path.exists() else None

    @staticmethod
    def get_active_ide_sdk_file() -> Optional[str]:
        """Get the jdk.table.xml path for the currently active IDE.

        Returns:
            Path to jdk.table.xml for the active IDE, or None if not detected.
        """
        context = RuntimeIdeDetector.detect_jetbrains_context()

        if context["config_dir"]:
            sdk_file = Path(context["config_dir"]) / "options" / "jdk.table.xml"
            return (
                str(sdk_file) if sdk_file.exists() else str(sdk_file)
            )  # Return path even if doesn't exist yet

        return None

    @staticmethod
    def is_running_in_jetbrains_ide() -> bool:
        """Check if currently running in any JetBrains IDE."""
        context = RuntimeIdeDetector.detect_jetbrains_context()
        return (
            context["ide"] is not None
            and context["ide"] != "JetBrains (unknown product)"
        )
