---
name: desktop-tool-pipeline
description: >-
  End-to-end workflow for building a small cross-platform desktop tool (Python + PySide6) on a Mac and
  delivering it to macOS and Windows users: project scaffold with a state→result core decoupled from the GUI,
  UI/UX-driven styling, real-window QA with real data and screenshots, a vector app icon (.icns/.ico/.png),
  a local macOS launcher app, a standalone shareable macOS app (PyInstaller, signed, compatible with older
  macOS), a portable Windows zip (embedded Python, no install), and a handoff file so an agent on a real
  Windows PC can verify it and build a .exe. Use this skill whenever the user wants a desktop app / GUI tool /
  calculator / data-analysis window that should open by double-click, wants to package or share a Python tool
  with classmates or colleagues, asks for a Mac App, .app, .exe, Windows version, portable zip, app icon, or
  says things like 做桌面工具, 做成 App, 打包, 給 Windows 用, 給同學用, 做成 exe, 好看的圖示 — even if they do not
  mention PySide6 or packaging explicitly.
compatibility: >-
  Host: macOS with Xcode command line tools (xcrun llvm-objdump, iconutil, codesign, vtool, ditto) and
  Python 3.10+. Python packages: PySide6-Essentials, PyInstaller (installed into project venvs only).
  Windows steps run on a real Windows 10/11 PC by a second agent (Claude Code, Codex, …).
---

# Desktop tool pipeline (Mac first, Windows verified on a real PC)

This skill captures a workflow that worked well in practice: develop and verify a PySide6 desktop tool on
macOS, ship three deliverables, and hand the Windows-only steps to an agent running on a real Windows machine.
The domain logic (what the tool calculates) changes every time; the scaffolding, verification and packaging
below do not — and they are where most of the time is lost if you rediscover the pitfalls.

## Principles (why the steps look the way they do)

- **One source of truth.** All code changes happen in the Mac project. The Windows agent verifies, packages
  and reports, but does not edit app code — otherwise two diverging copies appear and the next rebuild
  silently overwrites the Windows fixes.
- **Core decoupled from GUI.** The GUI only edits a state object; every change re-runs one pure function
  `analyze(data, state) -> result`. Plots, numbers and exports then can never disagree, the core is unit
  testable without a display, and missing optional parameters degrade gracefully instead of blocking.
- **Verify with real data in a real window, report honestly.** Unit tests on parsers are not GUI tests.
  Drive the actual window with Qt events, save screenshots, look at them, and in reports distinguish
  "Qt-simulated input" from "physical mouse" and "macOS tested" from "Windows not yet tested".
- **Never modify the user's originals.** Record SHA-256 of prototypes and data before starting, check again
  at the end. Write fixtures and outputs elsewhere.
- **Ask before installing**, say what is downloaded from where (PyPI, python.org), keep installs inside
  project venvs.

## Workflow

Work through the phases in order; each has a reference file with details, commands and code. Read the
reference when you reach the phase, not all up front.

| Phase | What you produce | Read |
|---|---|---|
| 1. Scaffold | project layout, venv, importer / core / export / GUI modules, theme tokens | `references/01-project-setup.md` |
| 2. UI/UX pass | design direction from a UI/UX skill if available, documented choices | `references/01-project-setup.md` §UI |
| 3. Real-window QA | QA scenario script with assertions + screenshots, `--selftest` entry | `references/02-qa-real-window.md` |
| 4. Icon | `assets/icon_*.png`, `.icns`, `.ico`, preview strip | `references/03-icons.md` |
| 5. macOS delivery | local launcher `.app` (personal) + standalone `.app` zip (shareable) | `references/04-packaging-macos.md` |
| 6. Windows delivery | portable zip: embedded Python, `.bat` launchers, shortcut creator, README | `references/05-packaging-windows.md` |
| 7. Windows handoff | `WINDOWS_AGENT_TASK.md` + QA scripts inside the zip; report comes back | `references/06-windows-handoff.md` |
| Always | known pitfalls and their fixes | `references/pitfalls.md` |

Scripts in `scripts/` are generic and parameterised (`scripts/config.sh`: app name, Python package, bundle id,
Qt versions). `scripts/init_packaging.sh <project> "<App Name>" <pkg> [bundle.id]` copies them into the
project, fills the basic placeholders in the templates and lists the ones that still need tool-specific text. Templates in `templates/` are user-facing
documents (currently Traditional Chinese, the original users' language — translate to the user's language).

### Phase checklist

1. Read the user's spec / prototype / sample data. Hash originals (`shasum -a 256 … > docs/originals_sha256_before.txt`).
2. Create the project (`references/01`): `python3 -m venv .venv`, install `PySide6-Essentials` + needed libs.
   Call `unhide_qt_plugins()` before creating the QApplication (see pitfalls — macOS "hidden" flag).
3. Write importer → core (`analyze`) → export → plot widget → GUI. Unit-test importer on the **real** files
   and the core on **synthetic data with independently known answers**; keep the two kinds of tests separate.
4. Run the QA scenario in a real window (`references/02`), inspect every screenshot yourself, fix layout
   issues (truncated fields, squeezed panels, overlapping labels) at the default and the minimum window size.
5. Make the icon (`scripts/make_icons.py`), wire it with `app.setWindowIcon(...)`.
6. Build: `scripts/build_macos_launcher.sh` (for the developer), `scripts/build_macos_standalone.sh`
   (for sharing), `scripts/build_windows_portable.sh` (zip). Run the standalone app's `--selftest` from an
   unzipped copy with the project venvs temporarily renamed, to prove it is self-contained.
7. Fill the remaining placeholders in `packaging/windows/WINDOWS_AGENT_TASK.md` (data files, Mac QA counts);
   the Windows build script copies it and `scripts/*_qa.py` into the zip.
8. Write README + verification report: commands, results, real-data numbers, screenshot paths, tested vs
   untested platforms. Re-check the originals' hashes.

## Deliverables and what to tell the user

| File | For whom | Notes to tell the user |
|---|---|---|
| `build/<App>.app` (launcher) | the developer only | points at the project venv by absolute path — **cannot be given to others** |
| `build/<App>_macOS.zip` | other Mac users | self-contained; Apple Silicon only if built on arm64; minimum macOS = highest `minos` of bundled binaries; first open needs Gatekeeper steps (template) |
| `build/<App>_Windows.zip` | Windows users | unzip first, run the shortcut creator once; built on a Mac → "not verified on Windows" until the handoff report says otherwise |

If the user wants files on the Desktop, copy them there and verify with `cmp`; after every rebuild, update the
Desktop copies too so nobody keeps an outdated zip.

## Reporting template (end of each phase or task)

- What was built / changed (files with paths).
- Test evidence: exact commands, pass counts, key numbers on real data, screenshot paths.
- Platform status, explicitly: "macOS: tested in a real Cocoa window (Qt-simulated input)"; "Windows: not
  tested on a real machine" until the Windows report arrives.
- Known limitations and anything the user must check by eye (e.g. Finder/Dock icon appearance).
