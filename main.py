"""Generate the espresso-making infographic flowchart.

Usage:
    python main.py                 # render SVG + PNG into ./output
    python main.py --no-icons      # skip icons (fastest, fully offline)
    python main.py --formats svg   # only SVG
    python main.py --dpi 200       # higher-resolution PNG
    python main.py --open          # open the PNG when done (Windows)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make ``src`` importable without installing the package.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from espresso_flow import IconSet, Theme, build_workflow, render  # noqa: E402

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "output"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the espresso flowchart.")
    parser.add_argument("--formats", nargs="+", default=["svg", "png"],
                        help="output formats (default: svg png)")
    parser.add_argument("--basename", default="espresso_flow",
                        help="output file base name")
    parser.add_argument("--dpi", type=int, default=150,
                        help="raster resolution for PNG (default: 150)")
    parser.add_argument("--no-icons", action="store_true",
                        help="render text-only cards (no download/rasterization)")
    parser.add_argument("--open", action="store_true",
                        help="open the rendered PNG afterwards (Windows)")
    args = parser.parse_args()

    print("Building espresso workflow...")
    theme = Theme()
    diagram = build_workflow()

    if args.no_icons:
        for node in diagram.nodes:
            node.icon = None
        icons = IconSet(ASSETS, verbose=False)
    else:
        print("Resolving icons (downloads + caches on first run)...")
        icons = IconSet(ASSETS, size=theme.icon_raster_px)

    print("Rendering...")
    written = render(diagram, theme, icons, OUTPUT, basename=args.basename,
                     formats=args.formats, dpi=args.dpi)

    print("\nDone. Wrote:")
    for path in written:
        print(f"  - {path}")

    if args.open:
        png = OUTPUT / f"{args.basename}.png"
        if png.exists() and hasattr(os, "startfile"):
            os.startfile(png)  # type: ignore[attr-defined]

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
