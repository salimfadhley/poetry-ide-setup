## Detecting JetBrains IDE Context (Python)

Practical options for determining whether Python code is running under a JetBrains IDE (PyCharm or IntelliJ with the Python plugin):

### 1. Environment variables (JetBrains runner/debugger)

- `PYCHARM_HOSTED=1` when started from the PyCharm/IntelliJ Python console or debugger.
- `PYCHARM_DISPLAY_PORT`, `PYCHARM_MATPLOTLIB_PORT` are often present when launched by the IDE.

Note: These indicate “JetBrains IDE Python runner” but do not distinguish PyCharm vs IntelliJ.

### 2. Process-tree inspection (distinguishes PyCharm vs IntelliJ)

Walk up parent processes and look for executables or commands containing `pycharm`, `idea`, or `intellij`.

```python
import os
import sys


def jetbrains_context():
    """Return basic info about a JetBrains IDE context.

    Attempts to identify whether the process is hosted by a JetBrains IDE and,
    if possible, which product (PyCharm vs IntelliJ IDEA).
    """

    jb_vars = {k: v for k, v in os.environ.items() if k.startswith("PYCHARM_")}
    hosted = "PYCHARM_HOSTED" in os.environ

    try:
        import psutil  # pip install psutil

        p = psutil.Process()
        trace = []
        while p:
            exe = (p.exe() or "").lower()
            name = (p.name() or "").lower()
            cmd = " ".join(p.cmdline()).lower()
            token = exe or name or cmd
            trace.append(token)
            if any(x in token for x in ("pycharm", "idea", "intellij")):
                if "pycharm" in token:
                    return {"ide": "PyCharm", "hosted": hosted, "env": jb_vars, "trace": trace}
                if "idea" in token or "intellij" in token:
                    return {"ide": "IntelliJ IDEA", "hosted": hosted, "env": jb_vars, "trace": trace}
            p = p.parent()
    except Exception:
        pass

    # Fallback: could still be JetBrains runner, but IDE unknown
    if hosted or any(k.startswith("PYCHARM_") for k in os.environ):
        return {"ide": "JetBrains (unknown product)", "hosted": hosted, "env": jb_vars}

    return {"ide": None, "hosted": False, "env": {}}
```

### 3. Debugger probe

If `sys.gettrace()` is non-None and `pydevd`/`pydevd_pycharm` is in `sys.modules`, you are likely under the JetBrains debugger. This does not distinguish specific IDE products.

## Summary

- To detect “running under a JetBrains IDE”: check `PYCHARM_HOSTED`, JetBrains-specific env vars, and/or presence of `pydevd*`.
- To distinguish PyCharm vs IntelliJ: inspect parent process names using `psutil` as shown above.
