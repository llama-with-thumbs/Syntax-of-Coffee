"""Data model for the infographic.

These are plain, position-aware dataclasses. A :class:`Diagram` is just four
lists (nodes, groups, edges, labels) plus the legend and recipe content. The
coordinate system is "y grows downward" (top of the page is y=0); the canvas
inverts the axis so the data reads top-to-bottom like the diagram.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Node:
    key: str
    text: str
    x: float                       # center x
    y: float                       # center y (grows downward)
    w: float = 30.0
    h: float = 11.0
    kind: str = "card"             # card | decision | circle | pill
    category: str = "process"      # colour key in theme.CATEGORIES
    icon: Optional[str] = None     # Lucide icon name, or None
    align: str = "left"            # text alignment inside card: left | center
    dashed: bool = False           # draw the border dashed (e.g. the "serve" note)

    # --- geometry helpers (centre-based, y downward) ---
    @property
    def top(self) -> Tuple[float, float]:
        return (self.x, self.y - self.h / 2)

    @property
    def bottom(self) -> Tuple[float, float]:
        return (self.x, self.y + self.h / 2)

    @property
    def left(self) -> Tuple[float, float]:
        return (self.x - self.w / 2, self.y)

    @property
    def right(self) -> Tuple[float, float]:
        return (self.x + self.w / 2, self.y)

    def point(self, side: str) -> Tuple[float, float]:
        return {"top": self.top, "bottom": self.bottom,
                "left": self.left, "right": self.right}[side]


@dataclass
class Group:
    """A dashed, labelled container marking a parallel section."""
    title: str
    subtitle: str
    x0: float
    y0: float
    x1: float
    y1: float
    color: str = "#6B5B95"
    arrow_to: Optional[str] = None   # node key to point a dashed arrow at
    arrow_side: str = "left"         # which side of the group the arrow leaves


@dataclass
class Label:
    """Free-standing text, optionally inside a small filled chip."""
    text: str
    x: float
    y: float
    size: float = 9.0
    bold: bool = False
    color: str = "#33373D"
    ha: str = "center"
    va: str = "center"
    chip: Optional[str] = None     # fill colour for a rounded chip, or None
    chip_edge: Optional[str] = None


@dataclass
class Edge:
    src: str
    dst: str
    style: str = "solid"           # solid | dashed
    route: str = "v"               # v | h | vhv | hvh | vh | hv
    label: str = ""
    src_side: Optional[str] = None
    dst_side: Optional[str] = None
    midy: Optional[float] = None    # bend coordinate for vhv
    midx: Optional[float] = None    # bend coordinate for hvh
    color: str = "#5B6770"


@dataclass
class Diagram:
    nodes: List[Node] = field(default_factory=list)
    groups: List[Group] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    labels: List[Label] = field(default_factory=list)
    legend: List[Tuple[str, str]] = field(default_factory=list)  # (kind/category, text)
    recipe: Optional[Tuple[str, str]] = None                     # (title, body)
    xlim: Tuple[float, float] = (0, 110)
    ylim: Tuple[float, float] = (0, 280)                         # (top, bottom)

    def by_key(self) -> dict[str, Node]:
        return {n.key: n for n in self.nodes}
