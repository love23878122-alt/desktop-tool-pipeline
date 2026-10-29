"""GUI acceptance scenario on REAL data (copy to <project>/scripts/gui_qa.py and adapt).

  python scripts/gui_qa.py --out <export dir> [--shots docs/screenshots] [--log docs/qa/gui_qa_log.json]

Runs on the active Qt platform: cocoa/windows = real window (screenshots), offscreen = headless test.
Input = Qt-simulated mouse/keyboard events (QTest), not a physical mouse — say so in reports.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# inside the Windows zip the package lives in <root>/app/
sys.path.insert(0, os.path.join(ROOT, "app") if os.path.isdir(os.path.join(ROOT, "app", "{{PKG}}")) else ROOT)

from PySide6.QtCore import QPoint, QSettings, Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from {{PKG}} import gui  # noqa: E402

DATA = os.environ.get("APP_DATA_DIR", "<default data folder on the Mac>")   # Windows: folder without trailing space
LOG = []


def check(cond, what, **info):
    LOG.append({"check": what, "ok": bool(cond), **info})
    if not cond:
        raise AssertionError(f"{what} {info}")


def wait(ms=50):
    QTest.qWait(ms)


def drag(widget, p0: QPoint, p1: QPoint, steps=6):
    QTest.mousePress(widget, Qt.LeftButton, Qt.NoModifier, p0)
    for k in range(1, steps + 1):
        QTest.mouseMove(widget, QPoint(p0.x() + (p1.x() - p0.x()) * k // steps, p0.y() + (p1.y() - p0.y()) * k // steps))
    QTest.mouseRelease(widget, Qt.LeftButton, Qt.NoModifier, p1)
    wait()


def shot(w, shots, name):
    if shots:
        wait(120)
        path = os.path.join(shots, name)
        w.grab().save(path)
        LOG.append({"screenshot": path})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--shots")
    ap.add_argument("--log")
    a = ap.parse_args()
    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
    app = gui.make_app([])
    QSettings("{{PKG}}", "qa").clear()
    w = gui.MainWindow(QSettings("{{PKG}}", "qa"))
    w.resize(1480, 920)
    w.show()
    wait(300)
    LOG.append({"platform": app.platformName(), "os": sys.platform, "dpr": w.devicePixelRatioF()})
    check(not app.windowIcon().isNull(), "app icon loaded")
    shot(w, a.shots, "01_empty.png")

    # ---- adapt below: load each real file format, drive every interaction by mouse AND by typing,
    #      invalid inputs, dataset switching, parameter changes, export == screen, min window size ----
    # check(w.load_file(os.path.join(DATA, "sample.txt")), "load sample.txt")
    # QTest.mouseClick(w.some_button, Qt.LeftButton)
    # drag(w.plot, QPoint(...), QPoint(...)); check(w.result.x is not None, "drag updates result")

    for size, name in (((1180, 720), "90_min_size.png"), ((1920, 1080), "91_large.png")):
        w.resize(*size)
        wait(200)
        shot(w, a.shots, name)
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            json.dump(LOG, f, ensure_ascii=False, indent=1, default=str)
    print(f"GUI_QA_OK {sum(1 for x in LOG if 'check' in x)} checks on {app.platformName()}")
    w.close()


if __name__ == "__main__":
    main()
