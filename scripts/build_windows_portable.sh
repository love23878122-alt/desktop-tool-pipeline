#!/bin/zsh
# Portable Windows folder + zip built on macOS: build/${APP_FILE}_Windows.zip (needs a Windows PC to test).
set -e
cd "$(dirname "$0")/.."
source scripts/config.sh
BUILD=build
OUT=$BUILD/${APP_FILE}_Windows
HOSTPY=.venv/bin/python
PYMM=${PY_EMBED_VER%.*}; PYTAG=${PYMM//./}          # 3.13 -> 313
mkdir -p $BUILD/dl/wheels
[[ -f $BUILD/dl/python-$PY_EMBED_VER-embed-amd64.zip ]] || curl -sSfL -o $BUILD/dl/python-$PY_EMBED_VER-embed-amd64.zip \
  https://www.python.org/ftp/python/$PY_EMBED_VER/python-$PY_EMBED_VER-embed-amd64.zip
$HOSTPY -m pip download -q --only-binary=:all: --platform win_amd64 --python-version $PYMM --implementation cp \
  PySide6-Essentials==$QT_VER_DEV ${=EXTRA_PIP} -d $BUILD/dl/wheels
rm -rf $OUT && mkdir -p $OUT/python $OUT/app
unzip -q $BUILD/dl/python-$PY_EMBED_VER-embed-amd64.zip -d $OUT/python
mkdir -p $OUT/python/Lib/site-packages
for w in $BUILD/dl/wheels/*.whl; do unzip -q -o "$w" -d $OUT/python/Lib/site-packages; done
$HOSTPY scripts/prune_pyside6_windows.py $OUT/python/Lib/site-packages ${=QT_MODULES}
printf "python$PYTAG.zip\r\n.\r\nLib\\\\site-packages\r\n..\\\\app\r\nimport site\r\n" > $OUT/python/python$PYTAG._pth
rsync -a --exclude '__pycache__' $PKG $OUT/app/
mkdir -p $OUT/examples && cp examples/SYNTHETIC_* $OUT/examples/ 2>/dev/null || true   # synthetic only
cp packaging/windows/*.bat $OUT/
for f in $OUT/*.bat; do sed -i '' 's/\r*$/\r/' "$f"; done
cp packaging/icons/$APP_FILE.ico packaging/entry.py $OUT/ 2>/dev/null || true
[[ -f packaging/windows/WINDOWS_AGENT_TASK.md ]] && cp packaging/windows/WINDOWS_AGENT_TASK.md $OUT/
mkdir -p $OUT/qa && cp scripts/*_qa.py $OUT/qa/ 2>/dev/null || true
printf '\xef\xbb\xbf' > $OUT/README_Windows.txt && sed 's/$/\r/' packaging/windows/README_Windows.txt >> $OUT/README_Windows.txt
cd $BUILD && rm -f ${APP_FILE}_Windows.zip && zip -qr -X ${APP_FILE}_Windows.zip ${APP_FILE}_Windows && ls -lh ${APP_FILE}_Windows.zip
