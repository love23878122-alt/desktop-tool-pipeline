#!/bin/zsh
# Copy this skill's build scripts and templates into a project and fill the basic placeholders.
# Usage: <skill>/scripts/init_packaging.sh <project-dir> "<App Name>" <python_pkg> <bundle.id>
# Remaining {{...}} placeholders (descriptions, usage steps, data files, QA results) are listed at the end:
# fill them by hand — they need knowledge of the actual tool.
set -e
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
PROJ="$1"; APP_NAME="$2"; PKG="$3"; BUNDLE_ID="${4:-local.${PKG//_/-}}"
[[ -n $PROJ && -n $APP_NAME && -n $PKG ]] || { echo "usage: $0 <project-dir> \"<App Name>\" <python_pkg> [bundle.id]"; exit 1; }
APP_FILE="${APP_NAME// /_}"
mkdir -p "$PROJ/scripts" "$PROJ/packaging/windows" "$PROJ/packaging/macos" "$PROJ/packaging/icons"
for f in build_macos_launcher.sh build_macos_standalone.sh build_windows_portable.sh check_macos_minos.sh \
         prune_pyside6_windows.py make_icons.py; do
  cp -n "$SKILL/scripts/$f" "$PROJ/scripts/" 2>/dev/null || true
done
if [[ ! -f "$PROJ/scripts/config.sh" ]]; then
  sed -e "s|\"My Tool\"|\"$APP_NAME\"|" -e "s|\"my_tool\"|\"$PKG\"|" -e "s|\"local.my-tool\"|\"$BUNDLE_ID\"|" \
      "$SKILL/scripts/config.sh" > "$PROJ/scripts/config.sh"
fi
fill() {  # fill <src> <dst>
  [[ -e "$2" ]] && { echo "keep existing $2"; return; }
  sed -e "s|{{APP_NAME}}|$APP_NAME|g" -e "s|{{APP_FILE}}|$APP_FILE|g" -e "s|{{PKG}}|$PKG|g" \
      -e "s|{{BUNDLE_ID}}|$BUNDLE_ID|g" -e "s|{{QT_VER}}|6.12.0|g" -e "s|{{EXTRA_PIP}}|openpyxl|g" "$1" > "$2"
}
fill "$SKILL/templates/entry.py" "$PROJ/packaging/entry.py"
for f in "$SKILL"/templates/windows/*; do
  n="$(basename "$f")"; fill "$f" "$PROJ/packaging/windows/${n//\{\{APP_FILE\}\}/$APP_FILE}"
done
for f in "$SKILL"/templates/macos/*; do fill "$f" "$PROJ/packaging/macos/$(basename "$f")"; done
[[ -f "$PROJ/scripts/gui_qa.py" ]] || fill "$SKILL/templates/qa_scenario_template.py" "$PROJ/scripts/gui_qa.py"
chmod +x "$PROJ"/scripts/*.sh
echo "initialised packaging for \"$APP_NAME\" ($PKG) in $PROJ"
echo "placeholders still to fill:"
grep -rno "{{[A-Z_]*}}" "$PROJ/packaging" "$PROJ/scripts/gui_qa.py" 2>/dev/null | sort -u || echo "  none"
