"""Remove PySide6 parts the desktop tool never loads, using the PE import tables (llvm-objdump).

Roots: the Qt modules the app imports (command-line arguments) + the plugin folders a Widgets app needs.
Anything (DLL/PYD) outside the import closure of those roots is removed, as are tools and dev files.
Usage: python scripts/prune_pyside6_windows.py <site-packages dir> [QtCore QtGui QtWidgets QtSvg ...]
Runs on macOS (needs Xcode command line tools for `xcrun llvm-objdump`).
"""
import os
import re
import shutil
import subprocess
import sys

OBJDUMP = subprocess.run(["xcrun", "-f", "llvm-objdump"], capture_output=True, text=True).stdout.strip()
DEFAULT_MODULES = ["QtCore", "QtGui", "QtWidgets", "QtSvg"]
KEEP_PLUGIN_DIRS = ["platforms", "styles", "imageformats", "iconengines", "generic", "platforminputcontexts"]
DROP_DIRS = ["qml", "translations", "metatypes", "include", "typesystems", "glue", "scripts", "examples",
             "doc"]  # resources/icudtl.dat kept: cannot verify on Windows that Qt never needs it


def imports(path):
    out = subprocess.run([OBJDUMP, "-p", path], capture_output=True, text=True).stdout
    return [m.lower() for m in re.findall(r"DLL Name:\s*(\S+)", out)]


def main(sp, modules=None):
    pyside = os.path.join(sp, "PySide6")
    shib = os.path.join(sp, "shiboken6")
    python_dir = os.path.dirname(os.path.dirname(sp))
    local = {}
    for d in (pyside, shib, python_dir):
        for n in os.listdir(d):
            if n.lower().endswith((".dll", ".pyd")):
                local.setdefault(n.lower(), os.path.join(d, n))
    roots = [os.path.join(pyside, m + ".pyd") for m in (modules or DEFAULT_MODULES)]
    roots += [os.path.join(shib, n) for n in os.listdir(shib) if n.lower().endswith((".pyd", ".dll"))]
    for pd in KEEP_PLUGIN_DIRS:
        d = os.path.join(pyside, "plugins", pd)
        if os.path.isdir(d):
            roots += [os.path.join(d, n) for n in os.listdir(d) if n.lower().endswith(".dll")]
    need, todo, missing = set(), list(roots), set()
    while todo:
        p = todo.pop()
        key = os.path.abspath(p)
        if key in need:
            continue
        need.add(key)
        for dep in imports(p):
            if dep in local:
                todo.append(local[dep])
            elif not dep.startswith(("api-ms-", "ext-ms-")) and dep not in (
                    "kernel32.dll", "user32.dll", "gdi32.dll", "shell32.dll", "ole32.dll", "oleaut32.dll",
                    "advapi32.dll", "ws2_32.dll", "winmm.dll", "version.dll", "dwmapi.dll", "uxtheme.dll",
                    "imm32.dll", "shlwapi.dll", "comdlg32.dll", "netapi32.dll", "userenv.dll", "d3d11.dll",
                    "dxgi.dll", "d3d9.dll", "dwrite.dll", "d2d1.dll", "setupapi.dll", "authz.dll", "mpr.dll",
                    "wtsapi32.dll", "crypt32.dll", "bcrypt.dll", "secur32.dll", "ncrypt.dll", "iphlpapi.dll",
                    "dnsapi.dll", "winhttp.dll", "rpcrt4.dll", "comctl32.dll", "opengl32.dll", "d3d12.dll",
                    "dcomp.dll", "cfgmgr32.dll", "propsys.dll", "shcore.dll", "mf.dll", "mfplat.dll",
                    "user32", "ntdll.dll", "dbghelp.dll", "d3dcompiler_47.dll", "powrprof.dll", "hid.dll",
                    "wininet.dll", "msimg32.dll", "usp10.dll", "gdiplus.dll", "winspool.drv", "oleacc.dll",
                    "comdlg32", "credui.dll", "wldap32.dll", "normaliz.dll"):
                missing.add(dep)
    removed = 0
    for n in os.listdir(pyside):
        p = os.path.join(pyside, n)
        low = n.lower()
        if low.endswith((".dll", ".pyd")) and os.path.abspath(p) not in need:
            os.remove(p)
            removed += 1
        elif low.endswith(".exe"):
            os.remove(p)
            removed += 1
    for d in DROP_DIRS:
        p = os.path.join(pyside, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    plug = os.path.join(pyside, "plugins")
    for d in os.listdir(plug):
        if d not in KEEP_PLUGIN_DIRS:
            shutil.rmtree(os.path.join(plug, d))
    for d in ("include",):
        p = os.path.join(shib, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    # plugins that link a Qt DLL this wheel does not ship (e.g. Qt6Pdf, Qt6VirtualKeyboard) cannot load anyway
    for d in os.listdir(plug):
        for n in os.listdir(os.path.join(plug, d)):
            f = os.path.join(plug, d, n)
            bad = [x for x in imports(f) if x.startswith("qt6") and x not in local]
            if bad:
                os.remove(f)
                print("removed plugin", f"{d}/{n}", "(needs", ", ".join(bad) + ")")
    kept = sorted(os.path.basename(p) for p in need if os.path.dirname(p) == os.path.abspath(pyside))
    print("kept PySide6 binaries:", kept)
    print("removed files:", removed)
    print("unresolved non-system imports:", sorted(missing) or "none")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or None)
