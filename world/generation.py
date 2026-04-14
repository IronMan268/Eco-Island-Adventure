import random
import pygame
from constants import TILE_SIZE
from .decorations import generate_zone_decorations
from npc_data import NPCS_DATA


def dans_la_map(x, y, largeur, hauteur):
    return 0 <= x < largeur and 0 <= y < hauteur


def mettre_chemin(tiles, x, y, largeur, hauteur):
    if dans_la_map(x, y, largeur, hauteur) and tiles[y][x] != 0:
        tiles[y][x] = 3


def remplir_zone(tiles, x1, y1, x2, y2, largeur, hauteur, valeur):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if dans_la_map(x, y, largeur, hauteur) and tiles[y][x] != 0:
                tiles[y][x] = valeur


def creer_terrain_base(largeur, hauteur):
    random.seed(19)

    tiles = [[0 for _ in range(largeur)] for _ in range(hauteur)]
    centre_x = largeur / 2
    centre_y = hauteur / 2

    for y in range(hauteur):
        for x in range(largeur):
            dx = (x - centre_x) / (largeur * 0.42)
            dy = (y - centre_y) / (hauteur * 0.40)
            distance = dx * dx + dy * dy
            bruit = random.uniform(-0.08, 0.08)

            if distance < 0.67 + bruit:
                tiles[y][x] = 2
            elif distance < 0.82 + bruit:
                tiles[y][x] = 1
            else:
                tiles[y][x] = 0

    return tiles


def creer_zones(largeur, hauteur, spawn_tile):
    sx, sy = spawn_tile

    return {
        "spawn": pygame.Rect(sx - 12, sy - 12, 24, 24),
        "forest": pygame.Rect(22, 72, 55, 42),
        "lake": pygame.Rect(90, 26, 42, 26),
        "cliffs": pygame.Rect(145, 26, 42, 34),
        "polluted": pygame.Rect(135, 94, 42, 28),
        "igloo_village": pygame.Rect(sx - 16, sy - 12, 32, 24),
    }


def appliquer_zone_lac(tiles, zone, largeur, hauteur):
    cx = zone.left + zone.width / 2
    cy = zone.top + zone.height / 2

    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if not dans_la_map(x, y, largeur, hauteur):
                continue

            dx = (x - cx) / (zone.width * 0.45)
            dy = (y - cy) / (zone.height * 0.45)
            distance = dx * dx + dy * dy

            if distance < 0.95:
                tiles[y][x] = 1


def appliquer_zone_polluee(tiles, zone, largeur, hauteur):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if dans_la_map(x, y, largeur, hauteur) and tiles[y][x] != 0:
                tiles[y][x] = 4


def appliquer_zone_falaise(tiles, zone, largeur, hauteur):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if dans_la_map(x, y, largeur, hauteur):
                if tiles[y][x] == 2 and (x + y) % 4 != 0:
                    tiles[y][x] = 1


def appliquer_village(tiles, zone, largeur, hauteur):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if dans_la_map(x, y, largeur, hauteur) and tiles[y][x] != 0:
                tiles[y][x] = 3


def tracer_ligne_horizontale(tiles, x1, x2, y, largeur, hauteur, epaisseur=1):
    if x1 > x2:
        x1, x2 = x2, x1

    for x in range(x1, x2 + 1):
        for oy in range(-epaisseur, epaisseur + 1):
            for ox in range(-epaisseur, epaisseur + 1):
                mettre_chemin(tiles, x + ox, y + oy, largeur, hauteur)


def tracer_ligne_verticale(tiles, x, y1, y2, largeur, hauteur, epaisseur=1):
    if y1 > y2:
        y1, y2 = y2, y1

    for y in range(y1, y2 + 1):
        for oy in range(-epaisseur, epaisseur + 1):
            for ox in range(-epaisseur, epaisseur + 1):
                mettre_chemin(tiles, x + ox, y + oy, largeur, hauteur)


def tracer_chemin_L(tiles, x1, y1, x2, y2, largeur, hauteur, epaisseur=1):
    tracer_ligne_horizontale(tiles, x1, x2, y1, largeur, hauteur, epaisseur)
    tracer_ligne_verticale(tiles, x2, y1, y2, largeur, hauteur, epaisseur)


def tracer_chemin_points(tiles, points, largeur, hauteur, epaisseur=1):
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        tracer_chemin_L(tiles, x1, y1, x2, y2, largeur, hauteur, epaisseur)


def creer_place_depart(tiles, spawn_tile, largeur, hauteur):
    sx, sy = spawn_tile
    remplir_zone(tiles, sx - 8, sy - 6, sx + 8, sy + 6, largeur, hauteur, 3)


def creer_chemins_centre(tiles, spawn_tile, largeur, hauteur):
    sx, sy = spawn_tile

    tracer_ligne_horizontale(tiles, sx - 18, sx + 18, sy, largeur, hauteur, 1)
    tracer_ligne_verticale(tiles, sx, sy - 12, sy + 12, largeur, hauteur, 1)
    tracer_ligne_horizontale(tiles, sx - 8, sx + 8, sy - 8, largeur, hauteur, 1)


def faire_place_npc(tiles, tx, ty, largeur, hauteur):
    remplir_zone(tiles, tx - 1, ty - 1, tx + 1, ty + 1, largeur, hauteur, 3)
    remplir_zone(tiles, tx - 2, ty + 1, tx + 2, ty + 2, largeur, hauteur, 3)


def chemins_npc(spawn_tile):
    sx, sy = spawn_tile

    return {
        "bear": [
            (sx, sy),
            (sx - 14, sy),
            (sx - 22, sy + 10),
            (sx - 32, sy + 20),
            (68, 96),
        ],
        "seal": [
            (sx, sy),
            (sx, sy - 18),
            (sx + 6, sy - 24),
            (102, 55),
            (110, 55),
        ],
        "fox": [
            (sx, sy),
            (sx + 18, sy),
            (sx + 26, sy + 12),
            (145, 110),
            (150, 110),
        ],
        "penguin": [
            (sx, sy),
            (sx + 18, sy),
            (sx + 28, sy - 12),
            (150, 52),
            (160, 52),
        ],
    }


def relier_npcs(tiles, spawn_tile, largeur, hauteur):
    chemins = chemins_npc(spawn_tile)

    for npc in NPCS_DATA:
        route = chemins.get(npc["id"])

        if route is None:
            route = [spawn_tile, (npc["tile_x"], npc["tile_y"])]

        tracer_chemin_points(tiles, route, largeur, hauteur, 1)
        faire_place_npc(tiles, npc["tile_x"], npc["tile_y"], largeur, hauteur)


def generer_panneau_central(spawn_tile):
    sx, sy = spawn_tile

    panneau_tile_x = sx
    panneau_tile_y = sy - 3

    px = panneau_tile_x * TILE_SIZE
    py = panneau_tile_y * TILE_SIZE - 22

    rect_collision = pygame.Rect(px + 8, py + 24, 16, 18)

    deco = {
        "type": "pancarte_centrale",
        "x": px,
        "y": py,
    }

    return deco, rect_collision


def marquer_arbres_autour_ours(decorations):
    for deco in decorations:
        if deco.get("type") != "snow_pine":
            continue

        tile_x = deco["x"] // TILE_SIZE
        tile_y = deco["y"] // TILE_SIZE

        if 60 <= tile_x <= 76 and 88 <= tile_y <= 102:
            deco["type"] = "polluted_tree"
            deco["zone_tag"] = "bear_forest"


def generate_world_data(width, height, spawn_tile):
    tiles = creer_terrain_base(width, height)
    zones = creer_zones(width, height, spawn_tile)

    appliquer_zone_lac(tiles, zones["lake"], width, height)
    appliquer_zone_falaise(tiles, zones["cliffs"], width, height)
    appliquer_zone_polluee(tiles, zones["polluted"], width, height)

    creer_place_depart(tiles, spawn_tile, width, height)
    appliquer_village(tiles, zones["igloo_village"], width, height)
    creer_chemins_centre(tiles, spawn_tile, width, height)
    relier_npcs(tiles, spawn_tile, width, height)

    decorations, collision_rects = generate_zone_decorations(
        tiles=tiles,
        zones=zones,
        width=width,
        height=height,
        spawn_tile=spawn_tile
    )

    marquer_arbres_autour_ours(decorations)

    deco_panneau, rect_panneau = generer_panneau_central(spawn_tile)
    decorations.append(deco_panneau)
    collision_rects.append(rect_panneau)

    return {
        "tiles": tiles,
        "decorations": decorations,
        "collision_rects": collision_rects,
        "zones": zones,
        "sign_rect": rect_panneau,
    }