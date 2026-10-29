#!/bin/zsh
# Print the highest minimum-macOS version among all Mach-O files in a bundle (= what the target Mac needs).
# Usage: scripts/check_macos_minos.sh "build/My Tool.app" [-v]
APP="$1"
find "$APP" -type f \( -name "*.so" -o -name "*.dylib" -o -perm -u+x \) | while read -r f; do
  m=$(vtool -show-build "$f" 2>/dev/null | awk '/minos/{print $2; exit}')
  [[ -n $m ]] && echo "$m $(basename "$f")"
done | sort -V | { if [[ "$2" == "-v" ]]; then cat; else tail -1; fi; }
echo "architectures: $(lipo -archs "$APP/Contents/MacOS/"* 2>/dev/null | head -1)"
