"""Create the figure and export it to SVG and PNG."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import matplotlib
matplotlib.use("Agg")  # headless, file-only backend
import matplotlib.pyplot as plt  # noqa: E402

from .canvas import draw  # noqa: E402
from .icons import IconSet  # noqa: E402
from .model import Diagram  # noqa: E402
from .theme import Theme  # noqa: E402

# data-units -> inches, so the page scales sensibly with the canvas size
UNIT = 0.13


def render(diagram: Diagram, theme: Theme, icons: IconSet, out_dir: str | Path,
           basename: str = "espresso_flow", formats: Iterable[str] = ("svg", "png"),
           dpi: int = 150) -> List[Path]:
    """Render ``diagram`` to ``out_dir/basename.<fmt>`` for each format."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    w = (diagram.xlim[1] - diagram.xlim[0]) * UNIT
    h = (diagram.ylim[1] - diagram.ylim[0]) * UNIT
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    fig.patch.set_facecolor(theme.bg)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(theme.bg)

    draw(ax, diagram, theme, icons)

    written: List[Path] = []
    for fmt in formats:
        target = out_dir / f"{basename}.{fmt}"
        fig.savefig(target, format=fmt, dpi=dpi, facecolor=theme.bg,
                    bbox_inches="tight", pad_inches=0.15)
        written.append(target)
    plt.close(fig)
    return written
