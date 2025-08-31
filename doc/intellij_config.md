**IntelliJ/PyCharm Global SDK Configuration**

- **Where it lives:** Global SDKs are not stored in a project’s `.idea` folder. They reside in your IDE configuration directory under `options/jdk.table.xml` in your user profile.

- **Canonical path:** `<config-dir>/options/jdk.table.xml`

**Typical Paths**

- **Windows:** `C:\\Users\\<username>\\AppData\\Roaming\\JetBrains\\IntelliJIdea<version>\\options\\jdk.table.xml`
- **macOS:** `~/Library/Application Support/JetBrains/IntelliJIdea<version>/options/jdk.table.xml`
- **Linux:** `~/.config/JetBrains/IntelliJIdea<version>/options/jdk.table.xml`
- **Linux (older):** `~/.IntelliJIdea<version>/config/options/jdk.table.xml`
- **PyCharm note:** Replace `IntelliJIdea<version>` with `PyCharm<version>` or `PyCharmCE<version>`.

**What It Contains**

- **SDK definitions:** The `jdk.table.xml` file lists the SDKs shown under File → Project Structure → SDKs.

Example (simplified):

```xml
<application>
  <component name="ProjectJdkTable">
    <jdk version="2">
      <name value="Python 3.11 (Poetry)" />
      <type value="Python SDK" />
      <version value="3.11" />
      <homePath value="/Users/sal/.cache/pypoetry/virtualenvs/myproj/bin/python" />
    </jdk>
  </component>
</application>
```

**Project Binding**

- **Reference by name:** A project’s `.idea/misc.xml` references one of these global SDKs by its name. Changing or adding SDKs in `jdk.table.xml` (or via the IDE) makes them available for projects to select.

---

