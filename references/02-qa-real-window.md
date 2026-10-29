# 02 — Real-window QA, screenshots, self-test

## QA scenario script (`scripts/gui_qa.py`)

One script, many asserts, runs on whatever Qt platform is active:
- `cocoa` (default on macOS) = a real window → screenshots for docs and visual review;
- `QT_QPA_PLATFORM=offscreen` → headless, called from `tests/test_gui.py` in a subprocess (a missing
  platform plugin aborts the interpreter, so isolate it).

Skeleton: `templates/qa_scenario_template.py`. Key techniques:

```python
from PySide6.QtTest import QTest
QTest.mouseClick(window.some_button, Qt.LeftButton)          # click real buttons, not just call slots
QTest.mousePress(plot, Qt.LeftButton, Qt.NoModifier, p0)     # drags: press -> several moves -> release
QTest.mouseMove(plot, p_mid)                                 # check live updates between moves
QTest.mouseRelease(plot, Qt.LeftButton, Qt.NoModifier, p1)
QTest.qWait(50)                                              # let layouts/repaints settle
window.grab().save("docs/screenshots/03_state.png")          # real rendering of the real window
```

- Compute pixel positions from the widget's own data→pixel mapping (`plot.x_to_px(v)`), never hard-code.
- Separate **precision** from **correctness**: drags have ±1 px quantisation, so check drag results with a
  pixel-derived tolerance, and check numeric invariance (e.g. "zoom does not change results") with values
  typed into fields and compared with `==`.
- Write a JSON log (`{"check": ..., "ok": ..., <numbers>}`) — it becomes the evidence table in the report.
- Read data from an env var with the Mac path as default (`DATA = os.environ.get("APP_DATA_DIR", ...)`) and
  add `<root>/app` to `sys.path` if present, so the same script runs inside the Windows zip.
- Clear a dedicated `QSettings` scope at the start so runs are reproducible.

What to cover: load each real file format; every interaction path by mouse *and* by typing; invalid/empty
inputs (inline error, stale results invalidated); switching datasets; parameter changes; export contents
equal what is displayed; window at default and minimum size; any navigation (zoom/pan) leaving results
unchanged.

Look at every screenshot yourself before reporting — several real layout bugs were only visible there.
`screencapture` usually fails from an agent shell (no Screen Recording permission); `QWidget.grab()` of the
real Cocoa window is the fallback (no OS title bar — say so in the report).

## `--selftest` for packaged builds

Packaged apps (PyInstaller) usually exclude QtTest, so give the app its own check: `gui.main()` handles
`--selftest <report.json> [data-file]` → builds the window, loads a file (bundled synthetic example by
default), sets known inputs programmatically, checks results / icon / export, writes JSON, exit code 0/1.
Snippet: `templates/selftest_snippet.py`.

Prove the standalone app is self-contained:

```bash
ditto -x -k build/App_macOS.zip /tmp/check && mv .venv .venv_off      # (and any build venv)
env -i HOME=$HOME PATH=/usr/bin:/bin "/tmp/check/App_macOS/App.app/Contents/MacOS/App" --selftest /tmp/st.json
mv .venv_off .venv                                                     # always restore
```

The JSON should show `"frozen": true` and the same key numbers as the development build.

## Reporting

- Name the platform and input kind: "macOS Cocoa real window, Qt-simulated mouse events (QTest)".
- Physical mouse/trackpad feel and other users' machines are "not verified" unless someone actually did it.
- Keep `docs/qa/test_run.txt` (full output), `docs/qa/*_log.json`, and list screenshot files.
