"""Paste into gui.py and call before creating QApplication (macOS only).

Some synced folders (e.g. ~/Documents) give files the BSD "hidden" flag; Qt's plugin scan skips hidden files
and aborts with 'Could not find the Qt platform plugin "cocoa"'. The flag can reappear, so clear it each start.
"""
import os
import sys


def unhide_qt_plugins():
    if sys.platform != "darwin":
        return 0
    import stat
    import PySide6
    plug = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins")
    fixed = 0
    for dirpath, dirnames, filenames in os.walk(plug):
        for n in [dirpath] + [os.path.join(dirpath, x) for x in dirnames + filenames]:
            try:
                fl = os.lstat(n).st_flags
                if fl & stat.UF_HIDDEN:
                    os.chflags(n, fl & ~stat.UF_HIDDEN, follow_symlinks=False)
                    fixed += 1
            except OSError:
                pass
    return fixed
