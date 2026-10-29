"""Add to gui.py. Packaged apps (PyInstaller) have no QtTest, so the app checks itself:

    "<App>.app/Contents/MacOS/<App>" --selftest report.json [data-file]
    "<App>.exe" --selftest report.json [data-file]

Exit code 0 = all checks passed. Adapt the marked block to your tool's inputs and outputs.
"""
import json
import os
import sys
import tempfile


def selftest(out_json, data_path=None):
    from PySide6.QtCore import QSettings
    app = make_app([sys.argv[0]])                       # noqa: F821  (your existing factory)
    w = MainWindow(QSettings("{{PKG}}", "selftest"))    # noqa: F821
    w.show()
    app.processEvents()
    checks = []

    def ok(cond, what):
        checks.append({"check": what, "ok": bool(cond)})
        return bool(cond)

    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.join(here, "..", "examples", "SYNTHETIC_example.xlsx")    # bundled with --add-data
    path = data_path or default
    info = {"frozen": bool(getattr(sys, "frozen", False)), "platform": app.platformName(), "os": sys.platform,
            "python": sys.version.split()[0], "file": path}
    if ok(os.path.exists(path), "input file found") and ok(w.load_file(path), "file loaded"):
        # ---- adapt: set known inputs exactly as a user would type them, then check results ----
        # w.some_field.setText("500"); app.processEvents()
        # ok(w.result.value is not None, "main result computed"); info["value"] = w.result.value
        ok(not app.windowIcon().isNull(), "window icon loaded")
        out = w.export_to(tempfile.mkdtemp())
        ok(os.path.isdir(out), "export written")
    info["checks"] = checks
    info["passed"] = all(c["ok"] for c in checks)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    w.close()
    return 0 if info["passed"] else 1

# in main():
#     argv = list(sys.argv if argv is None else argv)
#     if "--selftest" in argv:
#         rest = argv[argv.index("--selftest") + 1:]
#         return selftest(rest[0] if rest else os.path.expanduser("~/selftest.json"), rest[1] if len(rest) > 1 else None)
