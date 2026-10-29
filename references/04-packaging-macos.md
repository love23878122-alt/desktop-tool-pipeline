# 04 — macOS delivery

Two different things — explain the difference to the user, they are easy to confuse.

## A. Local launcher `.app` (developer only)

`scripts/build_macos_launcher.sh`: a tiny bundle whose executable is a shell script running
`<project>/.venv/bin/python -m <pkg>`. Double-clickable, has the icon, starts instantly — but it refers to the
project by absolute path. **Giving it to someone else does not work.** Rebuild after moving the project.
Redirect stderr to `~/<App>_error.log`.

## B. Standalone shareable `.app` (`scripts/build_macos_standalone.sh`)

PyInstaller onedir `--windowed` bundle with Python + Qt inside, zipped for sharing.

1. **Compatibility first.** Check the minimum macOS of every bundled binary:
   `scripts/check_macos_minos.sh "<App>.app"`. Recent PySide6 wheels can require a very new macOS
   (PySide6 6.12.0 → macOS 26). For sharing, build in a separate venv with an LTS release
   (PySide6-Essentials 6.8.3 → macOS 12) and run the full test + QA suite against it too.
   Architecture = build machine (arm64 on Apple Silicon → Intel Macs cannot run it; say so).
2. `--paths <project>` is required when the entry script lives outside the project root — otherwise
   PyInstaller silently misses your package and **all of PySide6** (symptom: a 20 MB app with no Qt). Check
   `Contents/Frameworks/PySide6/Qt/lib` exists after building.
3. Bundle data with `--add-data "<pkg>/assets:<pkg>/assets"` and the synthetic example the self-test uses.
4. **Sign in a temporary folder.** Files under some synced folders (e.g. `~/Documents`) repeatedly get the BSD
   `hidden` flag / Finder info, which `codesign` rejects ("resource fork, Finder information, or similar
   detritus not allowed"). Copy with `ditto --norsrc --noextattr --noqtn` to `mktemp -d`, `chflags -R nohidden`,
   `codesign --force --deep --sign -`, `codesign --verify --deep --strict`.
5. **Zip with `ditto -c -k --keepParent`**, not `zip -r` — Qt frameworks contain symlinks that plain zip breaks.
6. Include `使用說明_macOS.txt` (template) and a `範例資料（合成）` folder; never include private data.
7. Verify like a recipient: unzip to a fresh folder, rename project venvs, run `--selftest`, `open` the app,
   `codesign --verify` after unzip. Optional Gatekeeper simulation:
   `xattr -w com.apple.quarantine "0083;$(printf %x $(date +%s));Safari;" App.app && spctl --assess --type execute -vv App.app`
   → `rejected` is expected for un-notarised apps.

## First-open instructions for recipients (no Apple Developer ID / notarisation)

- macOS 15+: double-click → "cannot be opened" → System Settings → Privacy & Security → "Open Anyway".
- macOS 12–14: right-click (Control-click) → Open → Open.
- "is damaged and can't be opened": `xattr -dr com.apple.quarantine "/Applications/<App>.app"`.
- After unzipping, the zip can be deleted; move the `.app` to /Applications so it is not cleaned up with
  Downloads.

Size reference: ~78 MB app / ~28 MB zip for PySide6 Widgets + openpyxl. Too big for some mail limits →
recommend Google Drive / AirDrop.
