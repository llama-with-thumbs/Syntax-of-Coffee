"""Icon acquisition and rasterization.

Icons come from the Lucide icon set (https://lucide.dev, MIT licensed). SVGs
are downloaded on first use and cached on disk, then recoloured to match the
theme and rasterized to PNG so Graphviz can embed them reliably on every
platform.

Design goals:
* **Offline-friendly** — once cached, no network is needed.
* **Graceful** — if an icon can't be fetched/rendered, ``get`` returns ``None``
  and the diagram simply falls back to a text-only card. The build never fails
  because of icons.

Rasterization backends (auto-detected, best first):
  1. ``cairosvg``  — cleanest output and true transparency (needs Cairo libs).
  2. ``svglib`` + ``reportlab`` — pure-pip, works on Windows out of the box.
"""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path
from typing import Optional


LUCIDE_SOURCES = (
    "https://unpkg.com/lucide-static@latest/icons/{name}.svg",
    "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg",
)


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    h = color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _detect_backend() -> Optional[str]:
    try:
        import cairosvg  # noqa: F401
        return "cairosvg"
    except Exception:
        pass
    try:
        import svglib  # noqa: F401
        import reportlab  # noqa: F401
        return "svglib"
    except Exception:
        pass
    return None


class IconSet:
    """Resolves icon names to local PNG paths, downloading + caching as needed."""

    def __init__(self, assets_dir: str | Path, size: int = 128, verbose: bool = True):
        assets_dir = Path(assets_dir)
        self.svg_dir = assets_dir / "icons"
        self.png_dir = assets_dir / "icons_png"
        self.svg_dir.mkdir(parents=True, exist_ok=True)
        self.png_dir.mkdir(parents=True, exist_ok=True)
        self.size = size
        self.verbose = verbose
        self.backend = _detect_backend()
        self._unavailable: set[str] = set()
        if self.backend is None:
            self._log("  ! no SVG rasterizer found (install svglib+reportlab or "
                      "cairosvg) — rendering text-only cards")

    # -- public API ----------------------------------------------------------
    def get(self, name: Optional[str], color: str = "#333333",
            size: Optional[int] = None) -> Optional[str]:
        """Return an absolute PNG path for ``name`` recoloured to ``color``.

        Returns ``None`` (and logs why) if the icon can't be produced.
        """
        if not name or self.backend is None:
            return None
        size = size or self.size
        out = self.png_dir / f"{name}__{color.lstrip('#')}_{size}.png"
        if out.exists():
            return str(out.resolve())

        svg_path = self._ensure_svg(name)
        if svg_path is None:
            return None

        recoloured = self.svg_dir / f"_{name}__{color.lstrip('#')}.svg"
        try:
            text = svg_path.read_text(encoding="utf-8").replace("currentColor", color)
            recoloured.write_text(text, encoding="utf-8")
            self._rasterize(recoloured, out, size, color)
        except Exception as exc:  # pragma: no cover - defensive
            self._log(f"  ! could not render icon '{name}': {exc}")
            return None
        return str(out.resolve()) if out.exists() else None

    # -- internals -----------------------------------------------------------
    def _ensure_svg(self, name: str) -> Optional[Path]:
        path = self.svg_dir / f"{name}.svg"
        if path.exists():
            return path
        if name in self._unavailable:
            return None
        for template in LUCIDE_SOURCES:
            url = template.format(name=name)
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "espresso-flow/0.1"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                if b"<svg" not in data[:512]:
                    continue
                path.write_bytes(data)
                self._log(f"  ↓ downloaded icon '{name}'")
                return path
            except Exception:
                continue
        self._unavailable.add(name)
        self._log(f"  ! icon '{name}' unavailable (offline or renamed) — text only")
        return None

    def _rasterize(self, svg_path: Path, out_path: Path, size: int, color: str) -> None:
        if self.backend == "cairosvg":
            import cairosvg
            cairosvg.svg2png(url=str(svg_path), write_to=str(out_path),
                             output_width=size, output_height=size)
        elif self.backend == "svglib":
            self._rasterize_svglib(svg_path, out_path, size, color)

    def _rasterize_svglib(self, svg_path: Path, out_path: Path, size: int,
                          color: str) -> None:
        """Render with svglib/reportlab (white background), then reconstruct a
        clean alpha channel from the known stroke ``color`` so the icon is
        transparent with smooth, fully-saturated anti-aliased edges."""
        import tempfile

        import numpy as np
        from PIL import Image
        from reportlab.graphics import renderPM
        from svglib.svglib import svg2rlg

        drawing = svg2rlg(str(svg_path))
        if drawing is None:
            raise RuntimeError("svglib could not parse the SVG")
        base = drawing.width or 24
        scale = size / base
        drawing.scale(scale, scale)
        drawing.width = base * scale
        drawing.height = (drawing.height or 24) * scale

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            renderPM.drawToFile(drawing, tmp_path, fmt="PNG", bg=0xFFFFFF)
            rgb = np.asarray(Image.open(tmp_path).convert("RGB")).astype(np.float32)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        cr, cg, cb = _hex_to_rgb(color)
        target = np.array([cr, cg, cb], dtype=np.float32)
        # Pick the channel that contrasts most with white for a stable estimate
        # of coverage:  pixel = a*color + (1-a)*white  ->  a = (255-p)/(255-c).
        k = int(np.argmax(255.0 - target))
        denom = max(255.0 - target[k], 1.0)
        alpha = np.clip((255.0 - rgb[:, :, k]) / denom, 0.0, 1.0)

        out = np.zeros((rgb.shape[0], rgb.shape[1], 4), dtype=np.uint8)
        out[:, :, 0], out[:, :, 1], out[:, :, 2] = cr, cg, cb
        out[:, :, 3] = (alpha * 255.0).astype(np.uint8)
        Image.fromarray(out, "RGBA").save(out_path)

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)
