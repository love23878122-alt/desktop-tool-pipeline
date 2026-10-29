# 01 — Project scaffold, core design, UI pass

## Layout

```
<project>/
  <pkg>/                 # Python package, e.g. my_tool
    __init__.py          # __version__
    __main__.py          # from .gui import main; sys.exit(main())
    importer.py          # file formats -> dataclasses (keeps source row numbers, raw signs, metadata)
    core.py / analysis.py# State dataclass + analyze(data, state) -> Result (pure, no Qt)
    fitting.py           # formulas, SI units, explicit conversion constants
    export.py            # CSV / JSON (+ provenance), copies inputs
    plotwidget.py        # QPainter plot if interaction is needed (drag ranges, zoom); export PNG/SVG
    theme.py             # design tokens + QSS
    gui.py               # MainWindow; make_app(); main(); selftest()
    assets/icon_*.png
  tests/                 # unit tests (real-data importer tests separate from synthetic physics tests)
  scripts/               # QA scenario, fixtures, icons, build scripts
  packaging/windows/     # .bat launchers, README_Windows.txt, task file, entry.py
  packaging/macos/       # user guide for the standalone app
  packaging/icons/       # .icns, .ico
  docs/                  # verification_report.md, design_notes.md, screenshots/, qa/
  examples/              # SYNTHETIC_* only — never measured/private data
  requirements.txt  run_tests.sh  README.md  .gitignore (.venv/ build/ __pycache__/)
```

Dependencies: prefer `PySide6-Essentials` (not full PySide6 — smaller, enough for Widgets/Svg/Test) plus
small pure-Python libs (e.g. `openpyxl`). Avoid numpy/matplotlib unless really needed; a custom QPainter plot
is small, fully controllable (drag handles, zoom) and keeps the Windows zip ~35 MB.

## Core pattern: state -> result

```python
@dataclass
class State:            # everything the user can change, as raw text where it is typed
    d_nm: str = ""
    vbi_V: str = ""     # "" means "not provided" — never silently 0
    regions: dict = field(default_factory=lambda: {"a": None, "b": None})

def analyze(data, st: State) -> Result:
    # parse inputs -> field_errors (shown inline next to the field)
    # compute what is possible; for what is not, store a human-readable reason ("需要 d、εr")
    # collect messages [(level, scope, text)] — warnings never block looking at the data
```

GUI rules that follow from this:
- Every edit / drag / combo change → update `State` → `refresh()` → `analyze()` → redraw everything.
  No "Calculate" button needed; results can never be stale.
- Keep one `State` per dataset/curve; switching datasets shows that dataset's state, not leftovers.
- Show inline errors under the field (red border + text) and a sorted message list (error/warning/info,
  each with a text tag, not colour only).
- Exports call `refresh()` first and write exactly what is on screen; include source file SHA-256,
  parameters with their source, conventions/formulas, warnings.

## Importer rules

- Keep raw values, signs and 1-based source row numbers; no sorting, de-duplication or abs() at import.
- Stop at explicit end markers (e.g. a `=====` row before a statistics table); text inside a numeric data
  block is an error with its row number, not something to skip silently.
- Handle UTF-8 with BOM, tab/comma, scientific notation (`10E+6`), unit parsing from headers
  (`Current (mA)` → factor). Reject `.xls` with a clear message (suggest .xlsx/CSV).
- Test on the user's real files: counts per group, first/last values, TXT vs CSV equality, units.

## UI pass (if a UI/UX skill such as ui-ux-pro-max is available)

1. Run its design-system query for the product type (e.g. "scientific data analysis desktop tool",
   dense dashboard). Landing-page patterns returned for a desktop tool are not applicable — say so and
   re-query a single domain (`--domain color "analytics dashboard"`).
2. Targeted UX queries: drag alternatives (WCAG: every drag needs a typed/button alternative), inline
   validation, colour-blind-safe categorical colours, mode/active-state indication, zoom/pan reset.
3. Record queries, adopted results and deliberate deviations in `docs/design_notes.md`
   (e.g. web fonts not available offline → system fonts: macOS system font + PingFang TC; Windows Segoe UI +
   Microsoft JhengHei UI; numbers in Menlo/Consolas).

Design defaults that worked: Fusion style + explicit light palette (consistent on both OSes and in exported
figures), 14 px base / 12 px minimum, monospace numbers, tokens in `theme.py`, Okabe–Ito colours for
categories with darker "ink" variants for text (≥ 4.5:1), vector icons drawn with QPainter (no emoji).

## Layout checks that caught real bugs

- Narrow line edits showing only the tail of a number ("0.02" → "2").
- Word-wrapped `QLabel`s inside a `QScrollArea` make the layout underestimate height → rows get squeezed.
  Fix: fixed minimum heights + `QSizePolicy.Fixed` vertically for key/value rows.
- Long hint labels in a toolbar row wrap into a tall column at the minimum window size → own row,
  `QSizePolicy.Ignored` horizontally (elides) + tooltip with full text.
- Toolbar buttons truncated at minimum width → `QSizePolicy.Fixed` on buttons, icon-only for secondary
  actions (with tooltip + accessible name).
- Give the main plot a minimum height so secondary panels shrink first.
- Check both default size and `setMinimumSize` size on screenshots, at Retina DPR 2.
