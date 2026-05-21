"""Visual theme: palette, fonts and sizes.

Everything that controls *how the diagram looks* lives here. Edit the
``CATEGORIES`` colours to re-skin the whole infographic; the keys match the
legend in the reference design.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


# Soft, infographic palette. Each category = a pastel card:
#   fill (background) / edge (border) / text / icon (stroke colour).
CATEGORIES: Dict[str, Dict[str, str]] = {
    "machine":     {"fill": "#FCF3DC", "edge": "#E6C56B", "text": "#6B5320", "icon": "#B68A2E"},
    "beans":       {"fill": "#E7EEF8", "edge": "#B6CAE8", "text": "#2C3E5C", "icon": "#3E5F95"},
    "portafilter": {"fill": "#E4F0E3", "edge": "#B2D4AE", "text": "#2C4A2A", "icon": "#4E8C49"},
    "extraction":  {"fill": "#FBE5E5", "edge": "#EDB6B6", "text": "#5C2A2A", "icon": "#C25555"},
    "grinder":     {"fill": "#E9E2F2", "edge": "#C8BAE2", "text": "#3D2E5A", "icon": "#7E62A8"},
    "process":     {"fill": "#FFFFFF", "edge": "#C7CCD3", "text": "#34383F", "icon": "#5A6068"},
    "startend":    {"fill": "#CFE8CF", "edge": "#7CB97C", "text": "#234923", "icon": "#3C7A3C"},
}

DECISION = {"fill": "#FFFFFF", "edge": "#AEB4BC", "text": "#34383F", "icon": "#5A6068"}
CIRCLE = {"fill": "#FFFFFF", "edge": "#7C858F", "text": "#34383F"}


@dataclass
class Theme:
    # Typography. "Segoe UI" ships with Windows; swap for "Inter", "Arial", etc.
    font: str = "Segoe UI"
    title_pt: float = 11.0
    body_pt: float = 9.0
    small_pt: float = 8.0

    # Icon sizing/quality.
    icon_frac: float = 0.62        # icon height as a fraction of card height
    icon_raster_px: int = 160      # rasterization resolution

    # Geometry.
    corner: float = 1.6            # card corner radius (data units)
    pill_corner_frac: float = 0.5  # stadium rounding for start/end pills

    categories: Dict[str, Dict[str, str]] = field(default_factory=lambda: dict(CATEGORIES))
    decision: Dict[str, str] = field(default_factory=lambda: dict(DECISION))
    circle: Dict[str, str] = field(default_factory=lambda: dict(CIRCLE))

    bg: str = "#FCFCFD"
    edge_color: str = "#5B6770"

    def style(self, category: str) -> Dict[str, str]:
        return self.categories.get(category, self.categories["process"])
