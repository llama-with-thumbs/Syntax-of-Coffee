"""Matplotlib drawing layer: turns a :class:`Diagram` into artists on an Axes.

Pure rendering primitives — soft cards, pills, decision diamonds, merge
circles, dashed parallel-section containers, orthogonal connectors, a legend
and a recipe chip. No espresso-specific knowledge lives here.
"""
from __future__ import annotations

from typing import Dict, Tuple

import matplotlib.image as mpimg
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon

from .icons import IconSet
from .model import Diagram, Edge, Group, Label, Node
from .theme import Theme

# z-order layers
Z_GROUP, Z_EDGE, Z_NODE, Z_ICON, Z_TEXT = 0, 1, 2, 3, 4

DASH = (0, (6, 4))


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def _text(ax, x, y, s, *, size, color, font, ha="center", va="center",
          bold=False, z=Z_TEXT, chip=None, chip_edge=None):
    bbox = None
    if chip is not None:
        bbox = dict(boxstyle="round,pad=0.4", fc=chip, ec=chip_edge or chip, lw=1.1)
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color,
            fontfamily=font, fontweight="bold" if bold else "normal",
            linespacing=1.25, bbox=bbox, zorder=z)


def _auto_sides(src: Node, dst: Node) -> Tuple[str, str]:
    dx, dy = dst.x - src.x, dst.y - src.y
    if abs(dy) >= abs(dx):
        return ("bottom", "top") if dy > 0 else ("top", "bottom")
    return ("right", "left") if dx > 0 else ("left", "right")


def _seg(ax, p0, p1, color, ls, z=Z_EDGE):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, ls=ls, lw=1.6,
            solid_capstyle="round", zorder=z)


def _arrow(ax, p0, p1, color, ls, z=Z_EDGE):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=13, lw=1.6, color=color,
        linestyle=ls, shrinkA=0, shrinkB=2, joinstyle="round",
        capstyle="round", zorder=z))


# --------------------------------------------------------------------------
# nodes
# --------------------------------------------------------------------------
def _rounded(ax, node: Node, fill, edge, theme: Theme, rounding):
    ls = DASH if node.dashed else "solid"
    patch = FancyBboxPatch(
        (node.x - node.w / 2, node.y - node.h / 2), node.w, node.h,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        linewidth=1.6, facecolor=fill, edgecolor=edge, linestyle=ls,
        joinstyle="round", mutation_aspect=1.0, zorder=Z_NODE)
    ax.add_patch(patch)


def _place_icon(ax, img, cx, cy, size):
    half = size / 2.0
    # reversed y in extent + origin='upper' keeps the icon upright on the
    # downward-growing (inverted) axis.
    ax.imshow(img, extent=[cx - half, cx + half, cy + half, cy - half],
              origin="upper", interpolation="antialiased", zorder=Z_ICON)


def _draw_card(ax, node: Node, theme: Theme, icons: IconSet, cache: Dict):
    st = theme.style(node.category)
    _rounded(ax, node, st["fill"], st["edge"], theme, theme.corner)

    icon_w = 0.0
    if node.icon and node.align == "left":
        size = theme.icon_frac * node.h
        path = icons.get(node.icon, st["icon"], theme.icon_raster_px)
        if path:
            if path not in cache:
                cache[path] = mpimg.imread(path)
            ix = node.x - node.w / 2 + 2.3 + size / 2
            _place_icon(ax, cache[path], ix, node.y, size)
            icon_w = size + 3.6

    if node.align == "center":
        _text(ax, node.x, node.y, node.text, size=theme.body_pt,
              color=st["text"], font=theme.font, ha="center")
    else:
        tx = node.x - node.w / 2 + 2.3 + icon_w
        _text(ax, tx, node.y, node.text, size=theme.body_pt,
              color=st["text"], font=theme.font, ha="left")


def _draw_pill(ax, node: Node, theme: Theme):
    st = theme.style(node.category)
    _rounded(ax, node, st["fill"], st["edge"], theme, node.h * theme.pill_corner_frac)
    _text(ax, node.x, node.y, node.text, size=theme.title_pt, bold=True,
          color=st["text"], font=theme.font)


def _draw_decision(ax, node: Node, theme: Theme):
    st = theme.decision
    hw, hh = node.w / 2, node.h / 2
    pts = [(node.x, node.y - hh), (node.x + hw, node.y),
           (node.x, node.y + hh), (node.x - hw, node.y)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=st["fill"],
                         edgecolor=st["edge"], linewidth=1.6,
                         joinstyle="round", zorder=Z_NODE))
    _text(ax, node.x, node.y, node.text, size=theme.body_pt,
          color=st["text"], font=theme.font)


def _draw_circle(ax, node: Node, theme: Theme):
    st = theme.circle
    ax.add_patch(Circle((node.x, node.y), node.w / 2, facecolor=st["fill"],
                        edgecolor=st["edge"], linewidth=1.8, zorder=Z_NODE))


def _draw_node(ax, node: Node, theme: Theme, icons: IconSet, cache: Dict):
    if node.kind == "pill":
        _draw_pill(ax, node, theme)
    elif node.kind == "decision":
        _draw_decision(ax, node, theme)
    elif node.kind == "circle":
        _draw_circle(ax, node, theme)
    else:
        _draw_card(ax, node, theme, icons, cache)


# --------------------------------------------------------------------------
# edges
# --------------------------------------------------------------------------
def _draw_edge(ax, edge: Edge, nodes: Dict[str, Node], theme: Theme):
    src, dst = nodes[edge.src], nodes[edge.dst]
    auto_s, auto_d = _auto_sides(src, dst)
    p0 = src.point(edge.src_side or auto_s)
    p1 = dst.point(edge.dst_side or auto_d)
    color = edge.color or theme.edge_color
    ls = DASH if edge.style == "dashed" else "solid"

    label_pt = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    if edge.route in ("v", "h"):
        _arrow(ax, p0, p1, color, ls)
    elif edge.route == "vhv":
        my = edge.midy if edge.midy is not None else (p0[1] + p1[1]) / 2
        c1, c2 = (p0[0], my), (p1[0], my)
        _seg(ax, p0, c1, color, ls)
        _seg(ax, c1, c2, color, ls)
        _arrow(ax, c2, p1, color, ls)
    elif edge.route == "hvh":
        mx = edge.midx if edge.midx is not None else (p0[0] + p1[0]) / 2
        c1, c2 = (mx, p0[1]), (mx, p1[1])
        _seg(ax, p0, c1, color, ls)
        _seg(ax, c1, c2, color, ls)
        _arrow(ax, c2, p1, color, ls)
    elif edge.route == "vh":
        c = (p0[0], p1[1])
        _seg(ax, p0, c, color, ls)
        _arrow(ax, c, p1, color, ls)
        label_pt = (p0[0], (p0[1] + p1[1]) / 2)
    elif edge.route == "hv":
        c = (p1[0], p0[1])
        _seg(ax, p0, c, color, ls)
        _arrow(ax, c, p1, color, ls)
        label_pt = ((p0[0] + p1[0]) / 2, p0[1])

    if edge.label:
        _text(ax, label_pt[0], label_pt[1] - 1.2, edge.label,
              size=theme.small_pt, color="#55606B", font=theme.font,
              chip="#FCFCFD", chip_edge="#FCFCFD")


# --------------------------------------------------------------------------
# groups, legend, recipe
# --------------------------------------------------------------------------
def _draw_group(ax, g: Group, theme: Theme, nodes: Dict[str, Node]):
    w, h = g.x1 - g.x0, g.y1 - g.y0
    ax.add_patch(FancyBboxPatch(
        (g.x0, g.y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
        linewidth=1.6, facecolor="none", edgecolor=g.color, linestyle=DASH,
        zorder=Z_GROUP))
    title = f"{g.title}\n{g.subtitle}"
    _text(ax, (g.x0 + g.x1) / 2, g.y0, title, size=theme.small_pt, bold=True,
          color=g.color, font=theme.font, chip="#FCFCFD", chip_edge=g.color,
          z=Z_TEXT)
    if g.arrow_to and g.arrow_to in nodes:
        dst = nodes[g.arrow_to]
        if g.arrow_side == "left":
            start = (g.x0, (g.y0 + g.y1) / 2)
            end = dst.right
        else:
            start = (g.x1, (g.y0 + g.y1) / 2)
            end = dst.left
        c = (end[0], start[1])
        _seg(ax, start, c, g.color, DASH)
        _arrow(ax, c, end, g.color, DASH)


def _swatch(ax, kind, x, y, theme: Theme):
    """Draw a small legend marker centered at (x, y)."""
    r = 1.5
    if kind == "decision":
        st = theme.decision
        pts = [(x, y - r), (x + r * 1.3, y), (x, y + r), (x - r * 1.3, y)]
        ax.add_patch(Polygon(pts, closed=True, facecolor=st["fill"],
                             edgecolor=st["edge"], linewidth=1.4, zorder=Z_TEXT))
    elif kind == "circle":
        st = theme.circle
        ax.add_patch(Circle((x, y), r, facecolor=st["fill"],
                            edgecolor=st["edge"], linewidth=1.4, zorder=Z_TEXT))
    else:
        st = theme.style(kind)
        rounding = r if kind != "startend" else r * 1.6
        ax.add_patch(FancyBboxPatch(
            (x - r * 1.8, y - r), r * 3.6, r * 2,
            boxstyle=f"round,pad=0,rounding_size={rounding}",
            facecolor=st["fill"], edgecolor=st["edge"], linewidth=1.4,
            zorder=Z_TEXT))


def _draw_legend(ax, diagram: Diagram, theme: Theme, box):
    x0, y0, x1, y1 = box
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=2",
        facecolor="#FFFFFF", edgecolor="#C7CCD3", linewidth=1.4, zorder=Z_NODE))
    _text(ax, (x0 + x1) / 2, y0 + 4, "LEGEND", size=theme.title_pt, bold=True,
          color="#34383F", font=theme.font)
    sx = x0 + 6
    tx = x0 + 12
    top = y0 + 10
    step = (y1 - y0 - 13) / max(len(diagram.legend) - 1, 1)
    for i, (kind, label) in enumerate(diagram.legend):
        y = top + i * step
        _swatch(ax, kind, sx, y, theme)
        _text(ax, tx, y, label, size=theme.small_pt, color="#3A3F46",
              font=theme.font, ha="left")


def _draw_recipe(ax, diagram: Diagram, theme: Theme, box):
    if not diagram.recipe:
        return
    x0, y0, x1, y1 = box
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=2",
        facecolor="#FFFFFF", edgecolor="#9AA0A8", linewidth=1.6, zorder=Z_NODE))
    cx = (x0 + x1) / 2
    _text(ax, cx, y0 + (y1 - y0) * 0.34, diagram.recipe[0], size=theme.body_pt,
          bold=True, color="#34383F", font=theme.font)
    _text(ax, cx, y0 + (y1 - y0) * 0.68, diagram.recipe[1], size=theme.title_pt,
          bold=True, color="#5C2A2A", font=theme.font)


# --------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------
def draw(ax, diagram: Diagram, theme: Theme, icons: IconSet):
    nodes = diagram.by_key()
    cache: Dict = {}

    for g in diagram.groups:
        _draw_group(ax, g, theme, nodes)
    for e in diagram.edges:
        _draw_edge(ax, e, nodes, theme)
    for n in diagram.nodes:
        _draw_node(ax, n, theme, icons, cache)
    for lab in diagram.labels:
        _text(ax, lab.x, lab.y, lab.text, size=lab.size, bold=lab.bold,
              color=lab.color, font=theme.font, ha=lab.ha, va=lab.va,
              chip=lab.chip, chip_edge=lab.chip_edge)

    # legend (bottom-left) and recipe (bottom-right)
    _draw_legend(ax, diagram, theme, box=(3, 232, 35, 300))
    _draw_recipe(ax, diagram, theme, box=(80, 272, 108, 288))

    ax.set_xlim(*diagram.xlim)
    ax.set_ylim(diagram.ylim[1], diagram.ylim[0])  # invert: y grows downward
    ax.set_aspect("equal")
    ax.axis("off")
