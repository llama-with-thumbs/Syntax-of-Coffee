"""The espresso workflow as a positioned :class:`Diagram`.

This is the file you edit to change *what the flowchart says and where things
sit*. Coordinates use a 0..110 wide canvas with y growing downward. Columns:

    LEFT branch  ~ x=26      CENTER spine ~ x=52..56      RIGHT branch ~ x=85

Icon names refer to Lucide icons (https://lucide.dev/icons).
"""
from __future__ import annotations

from .model import Diagram, Edge, Group, Label, Node

# Center spine x for the upper / lower sections.
CX = 52
CXL = 56  # lower spine (after the first merge), nudged to balance legend/recipe


def build_workflow() -> Diagram:
    d = Diagram(xlim=(0, 110), ylim=(0, 304))

    # ---- top: machine setup (yellow) ------------------------------------
    d.nodes += [
        Node("start", "START", CX, 7, w=24, h=8, kind="pill",
             category="startend", align="center"),
        Node("n1", "1.  Press the power button (left side).\nLeft LED will turn on.",
             CX, 21, w=42, h=11, category="machine", icon="power"),
        Node("n2", "2.  Wait for the machine to finish\npreheating. Center LED will light\nup when ready.",
             CX, 35, w=42, h=13, category="machine", icon="sun"),
        Node("n3", "3.  Check that the rotary knob (right side)\nis in default position — fully turned\ncounterclockwise to the stop.",
             CX, 50, w=42, h=13, category="machine", icon="circle-dot"),
    ]

    # ---- PARALLEL SECTION 1 ---------------------------------------------
    d.groups.append(Group(
        "PARALLEL SECTION 1", "(While the machine is preheating)",
        x0=6, y0=59, x1=104, y1=154, color="#6B5B95"))
    d.labels += [
        Label("A.  PREPARE BEANS", 26, 69, size=9.5, bold=True,
              color="#2C3E5C", chip="#E7EEF8", chip_edge="#B6CAE8"),
        Label("B.  PREPARE PORTAFILTER  (EARLY STEPS)", 85, 69, size=9.0, bold=True,
              color="#2C4A2A", chip="#E4F0E3", chip_edge="#B2D4AE"),
    ]

    # Branch A: beans (blue)
    d.nodes += [
        Node("n4", "4.  Place the espresso cup on the\nscale and weigh 18 g of beans.",
             26, 81, w=36, h=12, category="beans", icon="scale"),
        Node("n5", "5.  Lightly spray the beans\nwith water.",
             26, 95, w=36, h=10, category="beans", icon="spray-can"),
        Node("n6", "6.  Pour the beans into the grinder\nand grind into the metal dosing cup.",
             26, 108, w=36, h=12, category="beans", icon="funnel"),
        Node("d7", "7.  Beans stuck to the\nsides of the grinder?",
             26, 125, w=30, h=17, kind="decision", category="process"),
        Node("p7", "Open the plastic grinder lid (grinder\npauses automatically). Push the beans\ndown into the grinder mouth, then\nclose the lid.",
             64, 124, w=34, h=20, category="grinder", align="center"),
        Node("nA", "(A)  Grinding complete. Metal dosing\ncup with ground coffee is ready.",
             26, 145, w=36, h=12, category="beans", icon="package"),
    ]

    # Branch B: portafilter early steps (green)
    d.nodes += [
        Node("n8", "8.  Place the plastic dosing\ncone onto the portafilter.",
             85, 81, w=34, h=11, category="portafilter", icon="traffic-cone"),
        Node("n9", "9.  Transfer the ground coffee from\nthe metal dosing cup into the\nportafilter through the cone.",
             85, 96, w=34, h=14, category="portafilter", icon="coffee"),
        Node("n10", "10.  Use a WDT tool (thin metal needles)\nto break up clumps and evenly\ndistribute the coffee grounds.",
             85, 113, w=34, h=14, category="portafilter", icon="wand-2"),
    ]

    # ---- first synchronization ------------------------------------------
    d.nodes.append(Node("m1", "", CXL, 162, w=6, h=6, kind="circle", category="process"))

    # ---- center: finish the puck (green) --------------------------------
    d.nodes += [
        Node("n11", "11.  Remove the dosing cone.",
             CXL, 173, w=38, h=10, category="portafilter", icon="traffic-cone"),
        Node("n12", "12.  Evenly distribute the\ncoffee grounds.",
             CXL, 185, w=38, h=11, category="portafilter", icon="target"),
        Node("n13", "13.  Tamp the coffee firmly and evenly.\nDo not press with your wrist — use your\nforearm to apply straight downward pressure.",
             CXL, 199, w=38, h=15, category="portafilter", icon="stamp"),
    ]

    # ---- PARALLEL SECTION 2 (left) --------------------------------------
    d.groups.append(Group(
        "PARALLEL SECTION 2", "(Finalize machine & cup prep)",
        x0=3, y0=166, x1=35, y1=205, color="#3E5F95"))
    d.nodes += [
        Node("n14a", "14a.  Place the espresso cup on\nthe scale under the portafilter.",
             19, 178, w=30, h=12, category="beans", icon="scale"),
        Node("n14b", "14b.  (Optional) Warm the cup with hot\nwater, then empty it onto the scale.",
             19, 192, w=30, h=12, category="beans", icon="droplet"),
    ]

    # ---- second synchronization -----------------------------------------
    d.nodes.append(Node("m2", "", CXL, 211, w=6, h=6, kind="circle", category="process"))

    # ---- center: lock + extraction --------------------------------------
    d.nodes += [
        Node("n15", "15.  Lock the portafilter into\nthe espresso machine.",
             CXL, 221, w=40, h=11, category="portafilter", icon="lock"),
        Node("n16", "16.  Press the center button\nto start extraction.",
             CXL, 234, w=40, h=11, category="extraction", icon="circle-play"),
        Node("n17", "17.  Slowly turn the right-side rotary knob\nclockwise to gradually increase pressure.",
             CXL, 248, w=40, h=12, category="extraction", icon="rotate-cw"),
        Node("n18", "18.  Stop the shot at ~36 g output (~30 sec),\nthen return the rotary knob to its default\nposition – fully counterclockwise.",
             CXL, 264, w=40, h=15, category="extraction", icon="circle-stop"),
        Node("n19", "19.  Press the left power button\nto turn off the machine.",
             CXL, 280, w=40, h=11, category="machine", icon="power"),
        Node("end", "END", CXL, 294, w=24, h=8, kind="pill",
             category="startend", align="center"),
        Node("serve", "Serve immediately.", 90, 294, w=28, h=9, kind="card",
             category="process", align="center", icon=None, dashed=True),
    ]

    # ---- PARALLEL SECTION 3 (right pointer) -----------------------------
    d.groups.append(Group(
        "PARALLEL SECTION 3", "(Ends when extraction starts)",
        x0=80, y0=228, x1=108, y1=243, color="#3E5F95",
        arrow_to="n16", arrow_side="left"))

    # ---- edges ----------------------------------------------------------
    e = d.edges
    e += [
        Edge("start", "n1"), Edge("n1", "n2"), Edge("n2", "n3"),
        # fork from step 3 into both branches
        Edge("n3", "n4", route="vhv", midy=65),
        Edge("n3", "n8", route="vhv", midy=65),
        # branch A
        Edge("n4", "n5"), Edge("n5", "n6"), Edge("n6", "d7"),
        Edge("d7", "p7", route="hv", label="YES", src_side="right", dst_side="left"),
        Edge("d7", "nA", label="NO"),
        Edge("p7", "nA", route="vh", src_side="bottom", dst_side="right", color="#7E62A8"),
        # branch B
        Edge("n8", "n9"), Edge("n9", "n10"),
        # both branches synchronize at m1
        Edge("nA", "m1", route="vhv", midy=158),
        Edge("n10", "m1", route="vhv", midy=158),
        # center spine
        Edge("m1", "n11"), Edge("n11", "n12"), Edge("n12", "n13"),
        Edge("n13", "m2"),
        # parallel section 2 merges in (dashed)
        Edge("n14a", "n14b", style="dashed", color="#3E5F95"),
        Edge("n14b", "m2", route="vh", style="dashed",
             src_side="bottom", dst_side="left", color="#3E5F95"),
        # lock + extraction
        Edge("m2", "n15"), Edge("n15", "n16"), Edge("n16", "n17"),
        Edge("n17", "n18"), Edge("n18", "n19"), Edge("n19", "end"),
        Edge("end", "serve", route="h", style="dashed",
             src_side="right", dst_side="left"),
    ]

    # ---- legend + recipe ------------------------------------------------
    d.legend = [
        ("machine", "Setup / Machine"),
        ("beans", "Beans Preparation"),
        ("portafilter", "Portafilter Preparation"),
        ("extraction", "Extraction"),
        ("grinder", "Grinder Handling (if needed)"),
        ("process", "Process (Action)"),
        ("decision", "Decision"),
        ("circle", "Merge / Synchronization"),
        ("startend", "Start / End"),
    ]
    d.recipe = ("RECIPE", "18 g  →  36 g  in  30 s")

    return d
