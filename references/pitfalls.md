# Pitfalls (each one cost real time once)

| Symptom | Cause | Fix |
|---|---|---|
| `Could not find the Qt platform plugin "cocoa"` / `"offscreen"` although the dylibs exist | Files under some synced folders (e.g. `~/Documents`) carry the BSD **hidden** flag (`ls -lO` shows `hidden`); Qt's plugin scan skips hidden files. The flag can come back later. | Clear it at startup before creating `QApplication` (`templates/unhide_qt_plugins.py`), and before builds. |
| `codesign`: "resource fork, Finder information, or similar detritus not allowed"; `xattr -cr` does not help | same hidden flag / Finder info on files under that folder | assemble and sign in `mktemp -d` after `ditto --norsrc --noextattr --noqtn` + `chflags -R nohidden` |
| Standalone app is ~20 MB and crashes / has no Qt | PyInstaller did not find the package (entry script outside project) | `--paths <project-root>`; check `Contents/Frameworks/PySide6` |
| Shared app won't start on a colleague's Mac | PySide6 wheel built for a newer macOS (6.12.0 → `minos 26.0`) | `vtool -show-build` all binaries (`scripts/check_macos_minos.sh`); build with PySide6-Essentials 6.8.3 (macOS 12+) in a separate venv; retest |
| Qt frameworks broken after unzip | `zip -r` dropped framework symlinks | `ditto -c -k --keepParent` |
| Mac standalone rejected on first open | not notarised (`spctl` → rejected) | give first-open steps (Privacy & Security → Open Anyway; right-click → Open; `xattr -dr com.apple.quarantine`) |
| Excel fixture: a row like `==========` became empty | openpyxl stores strings starting with `=` as formulas | set `cell.data_type = "s"`; importer also accepts a second end marker (stats header row) |
| Data path works on Mac, not on Windows | Windows forbids folder names ending with a space | configurable data dir (env var), tell user to rename |
| Windows taskbar shows Python icon | no AppUserModelID | `SetCurrentProcessExplicitAppUserModelID` before creating windows |
| `.bat` / README garbled on Windows | LF line endings / UTF-8 without BOM / non-ASCII in .bat | CRLF everywhere; README UTF-8 with BOM; ASCII-only .bat |
| Zip too big to email | ~35 MB with Qt | Google Drive / USB; Gmail limit 25 MB |
| QTest drag recreated/moved the wrong range | pressing inside an existing region moves it; near another region's edge resized it | only the *active* item reacts to the mouse; in tests clear before redrawing |
| Results panel values clipped | word-wrapped labels in scroll areas under-report height | fixed row heights, wrap only explanatory text |
| Narrow log-axis zoom shows 1–2 tick labels | decade-only ticks | label 1–9 mantissas below ~0.7 decade; linear "nice" steps when very narrow; unit-test tick generation |
| "Zoom changed the result" false alarm | pixel quantisation of drags | compare invariance with typed values and `==`; test drag precision separately with px tolerance |
| `screencapture` fails from the agent shell | no Screen Recording permission | `QWidget.grab()` of the real window; say "no OS title bar" |
| Finder/Dock still shows the old icon | icon cache | `touch` the bundle; logout/login; ask the user to look |
