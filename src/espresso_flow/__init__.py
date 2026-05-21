"""Espresso workflow infographic generator.

A small, modular toolkit that turns a declarative, positioned espresso-making
workflow (see :mod:`espresso_flow.workflow`) into a soft, modern infographic
flowchart drawn with matplotlib and exported to SVG and PNG.
"""

from .theme import Theme
from .icons import IconSet
from .model import Diagram, Edge, Group, Label, Node
from .workflow import build_workflow
from .canvas import draw
from .render import render

__all__ = [
    "Theme",
    "IconSet",
    "Diagram",
    "Node",
    "Edge",
    "Group",
    "Label",
    "build_workflow",
    "draw",
    "render",
]

__version__ = "0.2.0"
