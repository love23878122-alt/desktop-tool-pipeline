"""Entry point for PyInstaller builds (macOS standalone app and Windows .exe)."""
import sys

from {{PKG}}.gui import main

if __name__ == "__main__":
    sys.exit(main())
