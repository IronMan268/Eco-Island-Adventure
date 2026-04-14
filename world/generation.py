import random
import pygame
from constants import TILE_SIZE
from .decorations import generate_zone_decorations
from npc_data import NPCS_DATA


def dans_la_map(x, y, largeur, hauteur):
    return 0 <= x < largeur and 0 <= y < hauteur


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


def creer_place_depart(tiles, spawn_tile, largeur, hauteur):
    sx, sy = spawn_tile

    for y in range(sy - 6, sy + 7):
        for x in range(sx - 8, sx + 9):
            if dans_la_map(x, y, largeur, hauteur):
                tiles[y][x] = 3


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
            if not dans_la_map(x, y, largeur, hauteur):
                continue

            if tiles[y][x] != 0:
                tiles[y][x] = 4


def appliquer_zone_falaise(tiles, zone, largeur, hauteur):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if not dans_la_map(x, y, largeur, hauteur):
                continue

            if tiles[y][x] == 2 and (x + y) % 4 != 0:
                tiles[y][x] = 1


def appliquer_village(tiles, zone, largeur, hauteur):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if dans_la_map(x, y, largeur, hauteur) and tiles[y][x] != 0:
                tiles[y][x] = 3


def tracer_chemin(tiles, x1, y1, x2, y2, largeur, hauteur, epaisseur=1):
    x = x1
    y = y1

    while x != x2:
        if x2 > x:
            x += 1
        else:
            x -= 1

        for oy in range(-epaisseur, epaisseur + 1):
            for ox in range(-epaisseur, epaisseur + 1):
                tx = x + ox
                ty = y + oy
                if dans_la_map(tx, ty, largeur, hauteur) and tiles[ty][tx] != 0:
                    tiles[ty][tx] = 3

    while y != y2:
        if y2 > y:
            y += 1
        else:
            y -= 1

        for oy in range(-epaisseur, epaisseur + 1):
            for ox in range(-epaisseur, epaisseur + 1):
                tx = x + ox
                ty = y + oy
                if dans_la_map(tx, ty, largeur, hauteur) and tiles[ty][tx] != 0:
                    tiles[ty][tx] = 3


def relier_place_aux_npcs(tiles, spawn_tile, largeur, hauteur):
    sx, sy = spawn_tile

    for npc in NPCS_DATA:
        tx = npc["tile_x"]
        ty = npc["tile_y"]

        # chemin simple en L depuis la place centrale
        tracer_chemin(tiles, sx, sy, tx, sy, largeur, hauteur, epaisseur=1)
        tracer_chemin(tiles, tx, sy, tx, ty, largeur, hauteur, epaisseur=1)

        # petite place devant chaque npc
        for y in range(ty - 1, ty + 2):
            for x in range(tx - 1, tx + 2):
                if dans_la_map(x, y, largeur, hauteur) and tiles[y][x] != 0:
                    tiles[y][x] = 3


def ajouter_petit_reseau_central(tiles, spawn_tile, largeur, hauteur):
    sx, sy = spawn_tile

    tracer_chemin(tiles, sx - 10, sy, sx + 10, sy, largeur, hauteur, epaisseur=1)
    tracer_chemin(tiles, sx, sy - 8, sx, sy + 8, largeur, hauteur, epaisseur=1)


def generer_panneau_central(spawn_tile):
    sx, sy = spawn_tile
    px = sx * TILE_SIZE - 12
    py = sy * TILE_SIZE - 52

    rect_collision = pygame.Rect(px + 8, py + 26, 18, 14)

    deco = {
        "type": "pancarte_centrale",
        "x": px,
        "y": py
    }

    return deco, rect_collision


def generate_world_data(width, height, spawn_tile):
    tiles = creer_terrain_base(width, height)
    creer_place_depart(tiles, spawn_tile, width, height)

    zones = creer_zones(width, height, spawn_tile)

    appliquer_zone_lac(tiles, zones["lake"], width, height)
    appliquer_zone_falaise(tiles, zones["cliffs"], width, height)
    appliquer_zone_polluee(tiles, zones["polluted"], width, height)
    appliquer_village(tiles, zones["igloo_village"], width, height)

    ajouter_petit_reseau_central(tiles, spawn_tile, width, height)
    relier_place_aux_npcs(tiles, spawn_tile, width, height)

    decorations, collision_rects = generate_zone_decorations(
        tiles=tiles,
        zones=zones,
        width=width,
        height=height,
        spawn_tile=spawn_tile
    )

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