import os

# =========================
# IGLOO
# =========================

IGLOO_IMAGE_PATH = os.path.join("assets", "decor", "igloo.png")

IGLOO_SIZES = {
    0: (34, 26),
    1: (46, 34),
    2: (58, 42),
}

IGLOO_DRAW_OFFSET_X = 0
IGLOO_DRAW_OFFSET_Y = 0

IGLOO_COLLISIONS = {
    0: {"rect_offset": (8, 18), "rect_size": (18, 10), "deco_offset": (-2, -6)},
    1: {"rect_offset": (10, 22), "rect_size": (24, 12), "deco_offset": (-6, -12)},
    2: {"rect_offset": (14, 28), "rect_size": (34, 14), "deco_offset": (-12, -18)},
}

IGLOO_VILLAGE_LAYOUT = [
    (-8, -4, 1),
    (-2, -6, 2),
    (5, -4, 1),
    (-9, 3, 0),
    (7, 3, 0),
    (-2, 5, 1),
]

# =========================
# SPAWN CHANCES
# =========================

FOREST_PINE_CHANCE = 0.28
FOREST_ROCK_CHANCE = 0.36

LAKE_BIG_CRACK_CHANCE = 0.20
LAKE_ICE_CHUNK_CHANCE = 0.28

CLIFF_ICE_CHANCE = 0.17
CLIFF_SNOW_CRACK_CHANCE = 0.24

POLLUTED_BARREL_CHANCE = 0.09
POLLUTED_TRASH_CHANCE = 0.18
POLLUTED_OIL_CHANCE = 0.28

VILLAGE_PINE_CHANCE = 0.06
VILLAGE_ROCK_CHANCE = 0.10

GLOBAL_ROCK_CHANCE = 0.040
GLOBAL_PINE_CHANCE = 0.085
GLOBAL_SNOW_CRACK_CHANCE = 0.11
GLOBAL_ICE_CRACK_CHANCE = 0.025

# =========================
# FIXED POSITIONS
# =========================

EDGE_ICEBERG_POSITIONS = [
    (12, 16), (18, 31), (28, 84),
    (130, 18), (141, 35), (136, 82),
    (62, 11), (88, 12), (70, 94),
    (40, 14), (117, 92),
]

POLLUTION_WARNING_OFFSETS = [
    (5, 5),
    (9, 9),
    (12, 6),
]