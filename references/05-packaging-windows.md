# 05 — Windows portable zip (built on the Mac)

`scripts/build_windows_portable.sh` assembles a folder that runs on Windows 10/11 x64 without installing
anything, then zips it:

```
<App>_Windows/
  python/                    # python.org "embeddable" Python 3.13 + site-packages (PySide6-Essentials, …)
  python/python313._pth      # python313.zip . Lib\site-packages ..\app import site   (CRLF)
  app/<pkg>/                 # the application package (no __pycache__)
  <App>.bat                  # start "" python\pythonw.exe -X utf8 -m <pkg>     (no console)
  <App>_debug.bat            # python.exe -X utf8 -m <pkg> + pause                (shows errors)
  Create_Desktop_Shortcut.bat# PowerShell WScript.Shell → .lnk on Desktop + Start menu with the .ico
  <App>.ico
  README_Windows.txt         # UTF-8 *with BOM*, CRLF (Notepad shows Chinese correctly)
  WINDOWS_AGENT_TASK.md      # handoff for the Windows agent (see 06)
  qa/                        # the QA scenario scripts (run by the Windows agent)
  entry.py                   # PyInstaller entry for the .exe build on Windows
  examples/                  # SYNTHETIC_* only
```

Steps the script performs:
1. Download (or reuse a cache of) `python-<ver>-embed-amd64.zip` and Windows wheels:
   `pip download --only-binary=:all: --platform win_amd64 --python-version 3.13 --implementation cp …`.
2. Unzip wheels into `python/Lib/site-packages`.
3. Prune PySide6 with `scripts/prune_pyside6_windows.py` (walks PE import tables with `xcrun llvm-objdump`
   from the Qt modules you import; removes unused DLLs, QML, translations, tools; drops plugins whose
   Qt dependency is missing). Set `ROOT_MODULES` to the Qt modules the app imports
   (e.g. QtCore, QtGui, QtWidgets, QtSvg). Expect "unresolved" to list only system DLLs
   (`icuuc.dll`, `mscms.dll`, `uiautomationcore.dll` are fine).
4. Write `._pth`, copy app, bat files (convert to CRLF), README (BOM + CRLF), task file, QA scripts.
5. Zip and check: no measured data inside (`unzip -l | grep -i <data names>` → 0), required `.pyd` files and
   `plugins/platforms/qwindows.dll` present, the app code in the zip equals the project (`diff`).

Notes:
- The embedded Python has no pip and the pruned PySide6 has no QtTest → automated QA and PyInstaller run in a
  separate venv on Windows (06).
- Batch files: keep them ASCII (messages in English) to avoid code-page issues; Chinese goes in the README.
- Shortcut script: `%~dp0` gives the folder; use `[Environment]::GetFolderPath('Desktop')` (handles
  OneDrive-redirected desktops); rerun it if the folder moves. Cannot be tested on a Mac without PowerShell —
  report as untested.
- Tell users: unblock the downloaded zip (Properties → Unblock), extract before running, SmartScreen
  "More info → Run anyway" for the unsigned launcher.
- Windows forbids folder names ending with a space — data folders copied from a Mac may need renaming;
  make data paths configurable.
- ~35 MB zip: above Gmail's 25 MB attachment limit → Google Drive / USB.
