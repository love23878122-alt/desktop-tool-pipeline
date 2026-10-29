# 06 — Handoff to an agent on a real Windows PC

The Mac agent cannot run Windows. A second agent (Claude Code, Codex, …) on the user's Windows PC does the
Windows-only work. The handoff is a file inside the zip, so nothing needs to be installed in that agent first.

## Division of labour

| Mac agent (this skill) | Windows agent |
|---|---|
| all code changes, icon, builds, docs | real-machine verification (launch, shortcut, taskbar icon, fonts, DPI) |
| QA scripts + `--selftest` | run the same QA scripts in a real Windows window |
| portable zip | build the `.exe` with PyInstaller + `--icon` (cannot be done on macOS) |
| fixes from the Windows report, rebuild | write `WINDOWS_REPORT.md` with evidence, no edits to app code |

## Preparing the zip

1. Fill `templates/windows/WINDOWS_AGENT_TASK.md` (app name, package, data files the user must copy, expected QA
   check counts from the Mac run, the PyInstaller command) and copy it into the zip root.
2. Copy `scripts/gui_qa.py` (and other scenario scripts) to `qa/`; they read `APP_DATA_DIR` and find
   `app/<pkg>` automatically.
3. Copy `templates/entry.py` (PyInstaller entry, filled into `packaging/entry.py`) and the `.ico`.
4. Test the zip's own layout on the Mac: run `qa/*.py` from the unzipped folder with a data folder **without**
   a trailing space and confirm it imports `app/<pkg>` from the zip (print `<pkg>.__file__`).

## What to tell the user

1. Copy the zip and their data files to Windows (folder name without trailing space).
2. Unzip, open the folder in the Windows agent, and say: "請閱讀並執行 WINDOWS_AGENT_TASK.md"
   (or the English equivalent).
3. Bring back `WINDOWS_REPORT.md` + screenshots; fixes happen on the Mac; then rebuild and repeat.

Until that report exists, every summary says "Windows: built on macOS, not yet verified on a real machine".
