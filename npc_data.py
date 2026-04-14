from constants import TILE_SIZE

# =========================================================
# DONNEES DES NPC
# =========================================================

NPCS_DATA = [
    {
        "id": "bear",
        "name": "Ours protecteur",
        "image": "assets/npc_ours.png",
        "tile_x": 68,
        "tile_y": 96,
        "mission_key": "reforestation",
        "pollution_reward": 20,
        "default_lines": [
            "La foret a besoin d'aide...",
            "Parle avec les habitants et replante des pousses.",
            "Si tu reussis, la pollution baissera de 20%."
        ],
        "done_lines": [
            "Merci pour ton aide.",
            "La nature revient peu a peu.",
            "Les sapins repoussent deja."
        ],
        "reward_decor": [
            {"type": "snow_pine", "dx": -90, "dy": 6, "size": 0},
            {"type": "snow_pine", "dx": -58, "dy": 34, "size": 1},
            {"type": "snow_pine", "dx": 62, "dy": 10, "size": 0},
            {"type": "snow_pine", "dx": 96, "dy": 36, "size": 1},
        ],
    },

    {
        "id": "seal",
        "name": "Phoque du lac",
        "image": "assets/npc_phoque.png",
        "tile_x": 110,
        "tile_y": 55,
        "mission_key": "lake_cleanup",
        "pollution_reward": 10,
        "default_lines": [
            "Le lac est de plus en plus sale...",
            "Aide-moi a nettoyer cette zone.",
            "Chaque mission sauve un peu plus l'ile."
        ],
        "done_lines": [
            "Le lac respire mieux maintenant.",
            "Merci d'avoir aide les creatures du froid."
        ],
        "reward_decor": [
            {"type": "snow_pine", "dx": -40, "dy": 18, "size": 0},
            {"type": "snow_pine", "dx": 35, "dy": 24, "size": 0},
        ],
    },

    {
        "id": "fox",
        "name": "Renard eclaireur",
        "image": "assets/renard.png",
        "tile_x": 150,
        "tile_y": 110,
        "mission_key": "forest_sorting",
        "pollution_reward": 10,
        "default_lines": [
            "Cette zone est tres abimee...",
            "La pollution a envahi la neige.",
            "On doit agir vite."
        ],
        "done_lines": [
            "L'air est plus respirable maintenant.",
            "Tu as nettoye une zone critique."
        ],
        "reward_decor": [
            {"type": "snow_pine", "dx": -55, "dy": 20, "size": 1},
            {"type": "snow_pine", "dx": 50, "dy": 30, "size": 0},
        ],
    },

    {
        "id": "penguin",
        "name": "Pingouin ingenieur",
        "image": "assets/npc_pingouin.png",
        "tile_x": 160,
        "tile_y": 52,
        "mission_key": "ice_repair",
        "pollution_reward": 10,
        "default_lines": [
            "La glace se casse peu a peu.",
            "Cette zone devra etre reparee.",
            "Je te confierai une mission."
        ],
        "done_lines": [
            "La banquise tient mieux maintenant.",
            "Merci pour le coup de main."
        ],
        "reward_decor": [
            {"type": "snow_pine", "dx": -30, "dy": 18, "size": 0},
            {"type": "snow_pine", "dx": 42, "dy": 26, "size": 1},
        ],
    },
]


def tuile_vers_pixel(tile_x, tile_y):
    x = tile_x * TILE_SIZE + 4
    y = tile_y * TILE_SIZE - 8
    return x, y


def npc_tile_to_pixel(tile_x, tile_y):
    return tuile_vers_pixel(tile_x, tile_y)