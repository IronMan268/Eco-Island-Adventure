import os

# =========================
# IGLOO
# =========================

IGLOO_IMAGE_PATH = os.path.join("assets", "decor", "igloo.png")

IGLOO_SIZES = {
    0: (70, 60),
    1: (80, 68),
    2: (104, 88),
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
# IMAGES DE DECOR
# =========================

SNOW_PINE_IMAGE_PATH = os.path.join("assets", "decor", "arbre.png")
POLLUTED_TREE_IMAGE_PATH = os.path.join("assets", "decor", "arbre_pollue.png")
POLLUTED_SIGN_IMAGE_PATH = os.path.join("assets", "decor", "poubelle.png")

# =========================
# CHANCES D'APPARITION
# =========================

FOREST_PINE_CHANCE = 0.14
FOREST_ROCK_CHANCE = 0.00

LAKE_BIG_CRACK_CHANCE = 0.20
LAKE_ICE_CHUNK_CHANCE = 0.28

CLIFF_ICE_CHANCE = 0.14
CLIFF_SNOW_CRACK_CHANCE = 0.22

# On coupe les vieux decors moches de la zone polluee
POLLUTED_BARREL_CHANCE = 0.00
POLLUTED_TRASH_CHANCE = 0.00
POLLUTED_OIL_CHANCE = 0.00

# Nouveau decor plus propre
POLLUTED_TREE_CHANCE = 0.08
POLLUTED_SIGN_CHANCE = 0.03

VILLAGE_PINE_CHANCE = 0.03
VILLAGE_ROCK_CHANCE = 0.00

GLOBAL_ROCK_CHANCE = 0.00
GLOBAL_PINE_CHANCE = 0.025
GLOBAL_SNOW_CRACK_CHANCE = 0.08
GLOBAL_ICE_CRACK_CHANCE = 0.02

# =========================
# POSITIONS FIXES
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

# Arbres pollues fixes autour de l'ours
BEAR_POLLUTED_TREES = [
    (63, 92),
    (66, 98),
    (72, 93),
    (74, 99),
]