from constants import TILE_SIZE

# =========================================================
# CONFIG FACILE DES NPC
# - id : identifiant unique
# - name : nom affiché
# - image : image du npc
# - tile_x / tile_y : position sur la map en tuiles
# - mission_key : identifiant du mini-jeu / mission
# - pollution_reward : combien de pollution on enlève
# - default_lines : dialogue avant mission
# - done_lines : dialogue après mission
# - reward_decor : décor affiché après mission
# =========================================================

NPCS_DATA = [
    {
        "id": "bear",
        "name": "Ours protecteur",
        "image": "assets/npc_ours.png",
        "tile_x": 42,
        "tile_y": 92,
        "mission_key": "reforestation",
        "pollution_reward": 20,
        "default_lines": [
            "Cette partie de l'ile est encore fragile...",
            "Veux-tu m'aider a replanter des pousses ?",
            "Si tu reussis, la pollution baissera de 20%."
        ],
        "done_lines": [
            "Merci pour ton aide.",
            "Regarde, la nature revient deja.",
            "De nouveaux sapins ont pousse ici."
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
        "tile_y": 38,
        "mission_key": "lake_cleanup",
        "pollution_reward": 10,
        "default_lines": [
            "Le lac devient de plus en plus froid et sale...",
            "J'aurais besoin d'aide pour nettoyer cette zone.",
            "Une mission ici pourrait reduire la pollution."
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
        "image": "assets/npc_ours.png",
        "tile_x": 28,
        "tile_y": 36,
        "mission_key": "forest_sorting",
        "pollution_reward": 10,
        "default_lines": [
            "La foret garde encore ses secrets...",
            "Il faudrait la remettre en ordre.",
            "Tu peux m'aider quand tu veux."
        ],
        "done_lines": [
            "La foret est plus calme maintenant.",
            "Tu as bien travaille."
        ],
        "reward_decor": [
            {"type": "snow_pine", "dx": -55, "dy": 20, "size": 1},
            {"type": "snow_pine", "dx": 50, "dy": 30, "size": 0},
        ],
    },

    {
        "id": "penguin",
        "name": "Pingouin ingenieur",
        "image": "assets/npc_ours.png",
        "tile_x": 176,
        "tile_y": 42,
        "mission_key": "ice_repair",
        "pollution_reward": 10,
        "default_lines": [
            "Les falaises gelees s'abiment peu a peu.",
            "Il faudra reparer cette zone plus tard.",
            "Je pourrai te confier une mission."
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


def npc_tile_to_pixel(tile_x, tile_y):
    x = tile_x * TILE_SIZE + 4
    y = tile_y * TILE_SIZE - 8
    return x, y