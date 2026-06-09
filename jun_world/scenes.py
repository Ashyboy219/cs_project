"""Act One map definitions, built programmatically so grids stay rectangular.

Each scene returns a dict the Game turns into a live TileMap plus actors.
Coordinates in `spawns`, `checkpoints` and `transitions` are in TILE units.
"""
from . import settings as S


# ---- small grid builders ---------------------------------------------------
def blank(w, h, fill="."):
    return [[fill for _ in range(w)] for _ in range(h)]


def ring(g, ch):
    h, w = len(g), len(g[0])
    for x in range(w):
        g[0][x] = ch
        g[h - 1][x] = ch
    for y in range(h):
        g[y][0] = ch
        g[y][w - 1] = ch


def hline(g, y, x0, x1, ch):
    for x in range(x0, x1 + 1):
        g[y][x] = ch


def vline(g, x, y0, y1, ch):
    for y in range(y0, y1 + 1):
        g[y][x] = ch


def fill_rect(g, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = ch


def poke(g, pts, ch):
    for (x, y) in pts:
        g[y][x] = ch


def rows_to_str(g):
    return ["".join(r) for r in g]


# ---------------------------------------------------------------------------
# SCENE 1: The Fall  (landing road outside the kingdom)
# ---------------------------------------------------------------------------
def scene_fall():
    w, h = 26, 16
    g = blank(w, h, ",")
    ring(g, "T")
    # extra tree depth in corners
    for (x, y) in [(1, 1), (2, 1), (1, 2), (24, 1), (23, 1), (24, 2),
                   (1, 14), (2, 14), (1, 13), (24, 14), (23, 14), (24, 13)]:
        g[y][x] = "T"
    # cracked road across the middle, gate to the village on the right
    hline(g, 8, 1, 24, "P")
    g[8][25] = "g"
    # rubble + bushes scattered to feel ruined
    poke(g, [(5, 3), (6, 3), (5, 4), (19, 3), (20, 3), (20, 4),
             (4, 12), (5, 12), (20, 12), (21, 12)], "r")
    poke(g, [(8, 6), (9, 6), (16, 6), (17, 6), (8, 11), (9, 11),
             (16, 11), (17, 11), (12, 12), (13, 12)], "b")
    return dict(
        name="fall",
        tiles=rows_to_str(g),
        buildings=[],
        decos=[("rubblepile", 6, 4), ("rubblepile", 20, 12), ("mark", 22, 6)],
        checkpoints=[(12, 5)],
        spawns={"start": (12, 9), "from_village": (23, 8)},
        transitions=[dict(x=25, y=7, w=1, h=3, to="village", spawn="from_fall")],
        tint=S.GRASS,
    )


# ---------------------------------------------------------------------------
# SCENE 2: The Ruined Village  (Act One hub)
# ---------------------------------------------------------------------------
def scene_village():
    w, h = 34, 22
    g = blank(w, h, ".")
    ring(g, "T")
    # side walls of rubble for a hemmed-in feel
    vline(g, 1, 1, 20, "r")
    vline(g, 32, 1, 20, "r")
    # gates: left back to fall, right onward to the guard depot
    g[11][0] = "g"
    g[11][1] = "g"
    g[11][33] = "g"
    g[11][32] = "g"
    # main road + a branch up to the plaza/well
    hline(g, 11, 1, 32, "P")
    vline(g, 16, 7, 15, "P")
    hline(g, 7, 13, 19, "P")
    # grass patches and garden bushes
    fill_rect(g, 3, 16, 7, 19, ",")
    fill_rect(g, 25, 16, 30, 19, ",")
    poke(g, [(4, 17), (6, 18), (26, 17), (28, 18), (27, 16), (5, 16)], "b")
    poke(g, [(20, 4), (21, 4), (12, 17), (13, 17), (20, 17), (21, 17)], "b")
    poke(g, [(11, 16), (12, 16), (22, 5), (10, 5)], "T")
    # a little broken inner wall
    poke(g, [(22, 8), (22, 9), (23, 9)], "r")

    buildings = [
        dict(x=3, y=4, w=4, h=4, door=(1, 3), roof=S.ROOF, roof_d=S.ROOF_DK),
        dict(x=9, y=3, w=5, h=4, door=(2, 3), roof=(120, 96, 78),
             roof_d=(92, 72, 58), ruined=True),
        dict(x=25, y=4, w=4, h=4, door=(1, 3), roof=(110, 84, 92),
             roof_d=(84, 62, 70)),
        dict(x=27, y=13, w=4, h=4, door=(1, 0), roof=S.ROOF, roof_d=S.ROOF_DK),
        dict(x=4, y=14, w=4, h=4, door=(2, 0), roof=(96, 96, 110),
             roof_d=(72, 72, 86)),
    ]
    decos = [
        ("well", 16, 8),
        ("banner", 30, 9), ("banner", 30, 12),
        ("mark", 19, 13),
        ("cart", 8, 13), ("barrel", 9, 14), ("barrel", 24, 13),
        ("sign", 14, 10),
        ("flower", 5, 18), ("flower", 27, 18),
        ("rubblepile", 22, 6),
    ]
    return dict(
        name="village",
        tiles=rows_to_str(g),
        buildings=buildings,
        decos=decos,
        checkpoints=[(16, 13)],
        spawns={
            "from_fall": (3, 11),
            "from_depot": (30, 11),
            "plaza": (16, 12),
        },
        transitions=[
            dict(x=0, y=10, w=1, h=3, to="fall", spawn="from_village"),
            dict(x=33, y=10, w=1, h=3, to="depot", spawn="from_village",
                 needs_brief=True),
        ],
        tint=S.DUST,
    )


# ---------------------------------------------------------------------------
# SCENE 3: The Guard Depot  (stealth supply mission)
# ---------------------------------------------------------------------------
def scene_depot():
    w, h = 30, 20
    g = blank(w, h, ",")
    ring(g, "T")
    # outer ground is dust inside the tree ring
    fill_rect(g, 2, 2, 27, 17, ".")
    # the walled compound
    fill_rect(g, 5, 3, 24, 15, ".")
    # compound walls
    hline(g, 3, 5, 24, "#")
    hline(g, 15, 5, 24, "#")
    vline(g, 5, 3, 15, "#")
    vline(g, 24, 3, 15, "#")
    # entrance gap at the bottom (from the village side)
    g[15][14] = "g"
    g[15][15] = "g"
    g[16][14] = "P"
    g[16][15] = "P"
    g[17][14] = "P"
    g[17][15] = "P"
    g[18][14] = "g"   # exit threshold back to village
    g[18][15] = "g"
    # interior cover: crate stacks and supply nooks
    poke(g, [(8, 6), (9, 6), (8, 7), (20, 6), (21, 6), (21, 7),
             (12, 11), (13, 11), (17, 11), (18, 11),
             (7, 12), (22, 12)], "C")
    # bushes to hide in
    poke(g, [(10, 9), (11, 9), (19, 9), (20, 9), (14, 5), (15, 5),
             (6, 10), (23, 10)], "b")
    # broken patch
    poke(g, [(14, 8), (15, 8)], "r")

    decos = [
        ("banner", 6, 4), ("banner", 23, 4),
        ("mark", 14, 13),
        ("barrel", 6, 6), ("barrel", 23, 13),
        ("cart", 11, 13),
    ]
    return dict(
        name="depot",
        tiles=rows_to_str(g),
        buildings=[],
        decos=decos,
        checkpoints=[(14, 17)],
        # supply crate + guard placement consumed by the Game
        supplies=[(8, 9, "food"), (22, 8, "medicine"), (15, 6, "food")],
        guards=[
            dict(x=9, y=5, path=[(9, 5), (20, 5), (20, 13), (9, 13)]),
            dict(x=18, y=10, path=[(18, 10), (11, 10), (11, 6), (18, 6)]),
            dict(x=14, y=12, path=[(8, 12), (22, 12), (22, 7), (14, 7), (8, 7)]),
        ],
        spawns={"from_village": (14, 16), "exit": (14, 18)},
        transitions=[
            dict(x=13, y=18, w=3, h=2, to="village", spawn="from_depot"),
        ],
        tint=(150, 150, 160),
    )


# ---------------------------------------------------------------------------
# SCENE 4: The East Road  (Act One finale — the raid escape / pursuit boss)
# ---------------------------------------------------------------------------
def scene_escape():
    w, h = 48, 13
    g = blank(w, h, ".")
    ring(g, "#")
    fill_rect(g, 1, 1, w - 2, h - 2, ".")
    # the road
    for y in (5, 6, 7):
        hline(g, y, 1, w - 2, "P")
    # cover + rubble to break sightlines and give the Sling targets
    poke(g, [(8, 3), (8, 9), (14, 4), (14, 8), (30, 3), (34, 9), (40, 4), (44, 9)], "r")
    poke(g, [(11, 5), (28, 7), (36, 5), (42, 6)], "C")
    poke(g, [(6, 4), (6, 8), (18, 3), (18, 9), (33, 4)], "b")
    # the GATE wall at column 22 — solid above and below; the road gap (rows 5-7)
    # is held shut by a barrier the player must open.
    for yy in range(1, 5):
        g[yy][22] = "#"
    for yy in range(8, h - 1):
        g[yy][22] = "#"
    # the far gate (exit)
    g[6][w - 1] = "g"
    return dict(
        name="escape",
        tiles=rows_to_str(g),
        buildings=[],
        decos=[("banner", 4, 2), ("banner", 4, 10), ("mark", 24, 6),
               ("cart", 21, 8), ("barrel", 20, 8), ("rubblepile", 30, 3),
               ("banner", 45, 2), ("banner", 45, 10)],
        checkpoints=[],
        spawns={"start": (3, 6), "from_village": (3, 6)},
        gate=dict(col=22, rows=(5, 7)),
        captain=(3, 9),
        caged=(20, 5),
        guards=[
            dict(x=30, y=6, path=[(26, 5), (34, 5), (34, 7), (26, 7)]),
            dict(x=40, y=6, path=[(38, 4), (44, 4), (44, 8), (38, 8)]),
        ],
        exit_x=45,
        tint=(120, 108, 120),
    )


def all_scenes():
    return {
        "fall": scene_fall(),
        "village": scene_village(),
        "depot": scene_depot(),
        "escape": scene_escape(),
    }
