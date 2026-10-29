"""Draw an app icon with QPainter and write every size/format the launchers need.

Usage (from the project root, inside its venv):
    python scripts/make_icons.py --app-file My_Tool --pkg my_tool [--primary "#2547C4" --primary-dark "#172554"]

Edit draw_motif() to show what *your* tool does (default: a white data curve over three coloured bands, which
suits plotting / fitting tools). Sizes <= 32 px get a simplified drawing so they stay legible.

Outputs:
  <pkg>/assets/icon_{16..512}.png      window / Dock / taskbar icon (app.setWindowIcon)
  packaging/icons/<app-file>.icns      macOS bundle icon (via iconutil)
  packaging/icons/<app-file>.ico       Windows shortcut / exe icon (PNG-compressed entries 16–256)
  docs/screenshots/icon_preview.png    all sizes on light and dark backgrounds — look at it before shipping
"""
import argparse
import os
import shutil
import stat
import struct
import subprocess
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen  # noqa: E402

# accent bands: (colour, x-start, x-end, opacity). Warm colours need high opacity over navy or they turn brown.
BANDS = (("#56B4E9", 0.20, 0.47, 0.55), ("#F5A524", 0.54, 0.68, 0.88), ("#22C493", 0.71, 0.84, 0.72))


def draw_motif(p: QPainter, small: bool):
    """Drawn in a 1024×1024 coordinate system, clipped to the rounded square. Replace for your own tool."""
    if not small:
        p.setPen(QPen(QColor(255, 255, 255, 26), 6))
        for k in range(1, 6):
            x = 170 + k * 115
            p.drawLine(QPointF(x, 180), QPointF(x, 850))
        for y in (300, 520, 740):
            p.drawLine(QPointF(180, y), QPointF(850, y))
    for col, a, b, alpha in BANDS:
        c = QColor(col)
        c.setAlphaF(min(1.0, alpha + (0.08 if small else 0)))
        p.fillRect(QRectF(150 + a * 724, 170, (b - a) * 724, 690), c)
    path = QPainterPath(QPointF(170, 800))
    path.lineTo(QPointF(500, 600))
    path.cubicTo(QPointF(560, 565), QPointF(600, 470), QPointF(640, 360))
    path.cubicTo(QPointF(670, 280), QPointF(720, 240), QPointF(860, 175))
    p.setPen(QPen(QColor("white"), 64 if small else 40, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(path)
    cx, cy, r = 548, 572, (70 if small else 52)
    d = QPainterPath(QPointF(cx, cy - r))
    for x, y in ((cx + r, cy), (cx, cy + r), (cx - r, cy)):
        d.lineTo(QPointF(x, y))
    d.closeSubpath()
    p.setPen(QPen(QColor("white"), 16 if small else 12))
    p.setBrush(QColor("#E58AC0"))
    p.drawPath(d)


def draw(size, primary, primary_dark):
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(size / 1024, size / 1024)
    small = size <= 32
    bg = QPainterPath()
    m = 8 if small else 24
    bg.addRoundedRect(QRectF(m, m, 1024 - 2 * m, 1024 - 2 * m), 220, 220)
    g = QLinearGradient(0, 0, 0, 1024)
    g.setColorAt(0, QColor(primary))
    g.setColorAt(1, QColor(primary_dark))
    p.fillPath(bg, g)
    p.setClipPath(bg)
    draw_motif(p, small)
    p.end()
    return img


def write_ico(path, images):
    blobs = []
    for img in images:
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        img.save(tmp, "PNG")
        with open(tmp, "rb") as f:
            blobs.append((img.width(), f.read()))
        os.remove(tmp)
    offset = 6 + 16 * len(blobs)
    entries, data = b"", b""
    for w, blob in blobs:
        dim = 0 if w >= 256 else w
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(blob), offset + len(data))
        data += blob
    with open(path, "wb") as f:
        f.write(struct.pack("<HHH", 0, 1, len(blobs)) + entries + data)


def unhide_qt_plugins():
    import PySide6
    plug = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins")
    for d, ds, fs in os.walk(plug):
        for n in [d] + [os.path.join(d, x) for x in ds + fs]:
            try:
                fl = os.lstat(n).st_flags
                if fl & stat.UF_HIDDEN:
                    os.chflags(n, fl & ~stat.UF_HIDDEN, follow_symlinks=False)
            except (OSError, AttributeError):
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-file", required=True, help="file-name form of the app name, e.g. My_Tool")
    ap.add_argument("--pkg", required=True, help="Python package folder that gets assets/icon_*.png")
    ap.add_argument("--primary", default="#2547C4")
    ap.add_argument("--primary-dark", default="#172554")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    unhide_qt_plugins()
    app = QGuiApplication([])  # noqa: F841
    assets = os.path.join(a.root, a.pkg, "assets")
    icons = os.path.join(a.root, "packaging", "icons")
    shots = os.path.join(a.root, "docs", "screenshots")
    for d in (assets, icons, shots):
        os.makedirs(d, exist_ok=True)
    sizes = (16, 24, 32, 48, 64, 128, 256, 512, 1024)
    imgs = {s: draw(s, a.primary, a.primary_dark) for s in sizes}
    for s in (16, 32, 48, 64, 128, 256, 512):
        imgs[s].save(os.path.join(assets, f"icon_{s}.png"))
    write_ico(os.path.join(icons, f"{a.app_file}.ico"), [imgs[s] for s in (16, 24, 32, 48, 64, 128, 256)])
    tmp = tempfile.mkdtemp()
    iconset = os.path.join(tmp, f"{a.app_file}.iconset")
    os.makedirs(iconset)
    for s in (16, 32, 128, 256, 512):
        imgs[s].save(os.path.join(iconset, f"icon_{s}x{s}.png"))
        imgs[s * 2].save(os.path.join(iconset, f"icon_{s}x{s}@2x.png"))
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", os.path.join(icons, f"{a.app_file}.icns")], check=True)
    shutil.rmtree(tmp)
    prev = QImage(1500, 620, QImage.Format_ARGB32)
    prev.fill(QColor("#F1F5F9"))
    p = QPainter(prev)
    p.fillRect(QRectF(0, 310, 1500, 310), QColor("#1F2937"))
    for y0 in (30, 340):
        x = 30
        for s in (16, 24, 32, 48, 64, 128, 256):
            p.drawImage(QPointF(x, y0 + (256 - s) / 2), imgs[s])
            x += s + 40
    p.end()
    prev.save(os.path.join(shots, "icon_preview.png"))
    print("icons written to", assets, "and", icons)


if __name__ == "__main__":
    main()
