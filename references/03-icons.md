# 03 — App icon

Why it matters: without an icon, Windows shows the generic `.bat` gear and Python's taskbar icon, and the app
looks like a script rather than a product. macOS shows a generic app icon. Users notice immediately.

`scripts/make_icons.py` draws the icon with QPainter (vector, no external assets) and writes:
- `<pkg>/assets/icon_{16,32,48,64,128,256,512}.png` → `app.setWindowIcon()` (window, Dock, taskbar);
- `packaging/icons/<App>.icns` via `iconutil` (iconset with @1x/@2x);
- `packaging/icons/<App>.ico` (PNG-compressed entries 16–256, written with `struct`; works on Vista+);
- `docs/screenshots/icon_preview.png` on light and dark backgrounds.

Design guidance:
- Rounded square, the app's primary colour as a gradient, one white motif that says what the tool does
  (e.g. a log–log curve), 2–3 accent elements in the app's category colours.
- ≤ 32 px: draw a simplified variant (no grid/fine lines, thicker strokes).
- Translucent warm colours over a navy background turn brown — give each accent its own opacity
  (orange ≈ 0.9) and check the preview, don't guess.
- Look at the preview image before shipping.

Wiring:

```python
def app_icon():
    icon = QIcon()
    for s in (16, 32, 48, 64, 128, 256, 512):
        f = os.path.join(os.path.dirname(__file__), "assets", f"icon_{s}.png")
        if os.path.exists(f):
            icon.addFile(f)
    return icon

# Windows: own taskbar identity, otherwise the taskbar shows python's icon
if sys.platform.startswith("win"):
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("local.<app-id>")
app.setWindowIcon(app_icon())
```

- macOS `.app`: `CFBundleIconFile` in Info.plist + `.icns` in `Contents/Resources`; `touch` the bundle.
  Finder/Dock may cache the old icon (logout/login refreshes it) — ask the user to look; agents usually
  cannot capture Finder.
- Windows: shortcut `IconLocation` → `.ico` (see 05); PyInstaller `--icon <App>.ico`.
- Add a QA check that `app.windowIcon()` is not null and has ≥ 5 sizes.
