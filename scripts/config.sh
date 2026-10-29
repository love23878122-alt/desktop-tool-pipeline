# Shared settings for the build scripts. Copy into <project>/scripts/ and edit, or export before running.
: ${APP_NAME:="My Tool"}            # display name, e.g. "Fit Lab" (spaces allowed)
: ${APP_FILE:="${APP_NAME// /_}"}  # file-name form, e.g. Fit_Lab
: ${PKG:="my_tool"}                # Python package run as `python -m $PKG`
: ${BUNDLE_ID:="local.my-tool"}    # macOS bundle id / Windows AppUserModelID
: ${HOST_PYTHON:="python3"}        # Python used to create venvs on the Mac
: ${QT_VER_DEV:="6.12.0"}          # PySide6-Essentials in the dev venv and the Windows zip
: ${QT_VER_MAC_COMPAT:="6.8.3"}    # LTS PySide6 for the shareable Mac app (macOS 12+)
: ${PY_EMBED_VER:="3.13.14"}       # python.org embeddable build for Windows
: ${EXTRA_PIP:="openpyxl"}         # extra runtime packages (space separated)
: ${QT_MODULES:="QtCore QtGui QtWidgets QtSvg"}   # Qt modules the app imports (Windows pruning roots)
