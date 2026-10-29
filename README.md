# desktop-tool-pipeline

An agent skill (Claude Code, Codex, or any agent that reads `SKILL.md` skills) for building a small
**Python + PySide6 desktop tool on a Mac** and delivering it to **macOS and Windows** users — including the
parts that usually go wrong: real-window QA, app icons, a shareable signed `.app` that runs on older macOS,
a portable Windows zip with no installer, and a handoff file so an agent on a real Windows PC can verify the
build and produce a `.exe`.

一個給 AI 程式助理（Claude Code、Codex 等）用的 skill：在 Mac 上用 Python + PySide6 開發桌面小工具，
用真實資料在真實視窗驗證，做好看的圖示，再交付三種版本（自己用的 Mac 捷徑 App、可分享的獨立 Mac App、
免安裝的 Windows 可攜版），並產生一份任務檔，讓 Windows 電腦上的 AI 助理做實機驗收與 .exe 打包。

![icon preview](docs/icon_preview.png)

## What it covers

| Phase | Output |
|---|---|
| Scaffold | importer / pure `analyze(data, state)` core / export / GUI, theme tokens, UI/UX pass |
| Real-window QA | QA scenario driving the real window with Qt events, screenshots, JSON evidence, `--selftest` |
| Icon | QPainter-drawn icon → `.png` set, `.icns`, `.ico`, preview strip |
| macOS | local launcher `.app` (developer) and standalone PyInstaller `.app` zip (sharing; macOS 12+) |
| Windows | portable zip: python.org embeddable Python, pruned PySide6, `.bat` launchers, shortcut creator |
| Handoff | `WINDOWS_AGENT_TASK.md` + QA scripts in the zip; the Windows agent verifies, builds `.exe`, reports |

`references/pitfalls.md` lists the problems this workflow solves (macOS "hidden" file flag breaking Qt and
codesign, PySide6 wheels requiring a very new macOS, `zip` breaking framework symlinks, Windows folder names,
taskbar icon identity, CRLF/BOM, …).

## Install

Claude Code (user-level):

```bash
git clone https://github.com/love23878122-alt/desktop-tool-pipeline ~/.claude/skills/desktop-tool-pipeline
```

Codex: clone into your Codex skills folder (e.g. `~/.codex/skills/desktop-tool-pipeline`).
Other agents: point them at `SKILL.md`.

## Quick start (inside a project)

```bash
<skill>/scripts/init_packaging.sh . "My Tool" my_tool local.my-tool   # copies scripts + fills templates
.venv/bin/python scripts/make_icons.py --app-file My_Tool --pkg my_tool
zsh scripts/build_macos_launcher.sh        # build/My Tool.app (developer only)
zsh scripts/build_macos_standalone.sh      # build/My_Tool_macOS.zip (shareable)
zsh scripts/build_windows_portable.sh      # build/My_Tool_Windows.zip (verify on Windows!)
```

Requirements on the Mac: Xcode command line tools (`xcrun`, `iconutil`, `codesign`, `vtool`, `ditto`),
Python 3.10+. Packages are installed into project virtual environments only.

## Layout

```
SKILL.md                     workflow, principles, deliverables, reporting
references/01…06, pitfalls   details per phase
scripts/                     config.sh, init_packaging.sh, make_icons.py, build_*.sh, check_macos_minos.sh,
                             prune_pyside6_windows.py
templates/                   entry.py, selftest/QA/unhide snippets, Windows .bat + README + agent task,
                             macOS user guide (Traditional Chinese; translate as needed)
```

## Status

Distilled from a real project (a scientific data-analysis tool) that was built, verified and packaged with
this workflow on macOS. The generic scripts were re-tested end to end on a demo project on macOS
(launcher, standalone app with self-test from an unzipped copy, Windows zip assembly). The Windows-side steps
are designed to be executed by an agent on a real Windows PC and are not verified by the macOS run.
