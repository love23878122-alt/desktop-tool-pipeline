#!/bin/zsh
# Shareable macOS app (Python + Qt inside): build/${APP_FILE}_macOS.zip
# - separate build venv with an LTS PySide6 so older macOS can run it (check with check_macos_minos.sh)
# - assembled and ad-hoc signed in a temp folder (synced folders add flags that codesign rejects)
# - zipped with ditto (keeps Qt framework symlinks). Not notarised: recipients need first-open steps.
set -e
cd "$(dirname "$0")/.."
source scripts/config.sh
P="$(pwd)"
VENV=build/venv_mac_compat
if [[ ! -x $VENV/bin/python ]]; then
  $HOST_PYTHON -m venv $VENV
  $VENV/bin/pip install -q "PySide6-Essentials==$QT_VER_MAC_COMPAT" ${=EXTRA_PIP} pyinstaller
fi
PY=$VENV/bin/python
OUT=build/mac_standalone
rm -rf $OUT build/pyi_work && mkdir -p $OUT
"$PY" - <<'PYEOF'
import os, stat, PySide6
plug = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins")
for d, ds, fs in os.walk(plug):
    for n in [d] + [os.path.join(d, x) for x in ds + fs]:
        fl = os.lstat(n).st_flags
        if fl & stat.UF_HIDDEN:
            os.chflags(n, fl & ~stat.UF_HIDDEN, follow_symlinks=False)
PYEOF
ADD_DATA=(--add-data "${P}/${PKG}/assets:${PKG}/assets")
# braces matter: zsh would read "$f:examples" as $f with the :e modifier
for f in examples/SYNTHETIC_*(N); do ADD_DATA+=(--add-data "${P}/${f}:examples"); done
$VENV/bin/pyinstaller --noconfirm --clean --windowed --name "$APP_NAME" \
  --icon "$P/packaging/icons/$APP_FILE.icns" --osx-bundle-identifier "$BUNDLE_ID" \
  --paths "$P" "${ADD_DATA[@]}" --exclude-module tkinter --exclude-module PySide6.QtTest \
  --distpath "$OUT/dist" --workpath build/pyi_work --specpath build/pyi_work \
  "$P/packaging/entry.py" > build/pyi_build.log 2>&1 || { tail -30 build/pyi_build.log; exit 1; }
[[ -d "$OUT/dist/$APP_NAME.app/Contents/Frameworks/PySide6" ]] || { echo "PySide6 missing from bundle (check --paths)"; exit 1; }
STAGE="$(mktemp -d)/${APP_FILE}_macOS"
mkdir -p "$STAGE"
APP="$STAGE/$APP_NAME.app"
ditto --norsrc --noextattr --noqtn "$OUT/dist/$APP_NAME.app" "$APP"
chflags -R nohidden "$APP"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP" && echo "signature verified"
[[ -d packaging/macos ]] && cp packaging/macos/*.txt "$STAGE/" 2>/dev/null || true
if ls examples/SYNTHETIC_* >/dev/null 2>&1; then mkdir -p "$STAGE/範例資料（合成）" && cp examples/SYNTHETIC_* "$STAGE/範例資料（合成）/"; fi
rm -f build/${APP_FILE}_macOS.zip
ditto -c -k --keepParent "$STAGE" build/${APP_FILE}_macOS.zip
echo "minimum macOS: $(zsh scripts/check_macos_minos.sh "$APP" | head -1 | cut -d" " -f1)"
ls -lh build/${APP_FILE}_macOS.zip
