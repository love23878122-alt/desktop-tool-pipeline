#!/bin/zsh
# Local double-clickable launcher: build/$APP_NAME.app -> runs <project>/.venv/bin/python -m $PKG.
# For the developer only: it points at this project by absolute path, so it cannot be shared.
set -e
cd "$(dirname "$0")/.."
source scripts/config.sh
PROJ="$(pwd)"
APP="build/$APP_NAME.app"
rm -rf "$APP" && mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cat > "$APP/Contents/Info.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>$APP_NAME</string>
<key>CFBundleDisplayName</key><string>$APP_NAME</string>
<key>CFBundleIdentifier</key><string>$BUNDLE_ID</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>launcher</string>
<key>CFBundleIconFile</key><string>$APP_FILE</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PL
cat > "$APP/Contents/MacOS/launcher" <<SH
#!/bin/zsh
cd "$PROJ"
exec "$PROJ/.venv/bin/python" -m $PKG "\$@" 2>>"\$HOME/${APP_FILE}_error.log"
SH
chmod +x "$APP/Contents/MacOS/launcher"
[[ -f packaging/icons/$APP_FILE.icns ]] && cp packaging/icons/$APP_FILE.icns "$APP/Contents/Resources/"
touch "$APP"
echo "built $APP"
