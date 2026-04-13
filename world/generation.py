import random
import pygame
from .decorations import generate_zone_decorations
from npc_data import NPCS_DATA


def in_bounds(x, y, width, height):
    return 0 <= x < width and 0 <= y < height


def generate_base_tiles(width, height):
    random.seed(19)

    tiles = [[0 for _ in range(width)] for _ in range(height)]
    cx = width / 2
    cy = height / 2

    for y in range(height):
        for x in range(width):
            dx = (x - cx) / (width * 0.42)
            dy = (y - cy) / (height * 0.40)
            dist = dx * dx + dy * dy
            noise = random.uniform(-0.08, 0.08)

            if dist < 0.67 + noise:
                tiles[y][x] = 2
            elif dist < 0.82 + noise:
                tiles[y][x] = 1
            else:
                tiles[y][x] = 0

    return tiles


def carve_spawn_zone(tiles, spawn_tile, width, height):
    sx, sy = spawn_tile

    for y in range(sy - 5, sy + 6):
        for x in range(sx - 6, sx + 7):
            if in_bounds(x, y, width, height):
                tiles[y][x] = 3

    for y in range(sy - 15, sy + 16):
        for x in range(sx - 1, sx + 2):
            if in_bounds(x, y, width, height):
                tiles[y][x] = 3

    for x in range(sx - 20, sx + 21):
        for y in range(sy - 1, sy + 2):
            if in_bounds(x, y, width, height):
                tiles[y][x] = 3


def create_zones(width, height, spawn_tile):
    sx, sy = spawn_tile

    zones = {
        "spawn": pygame.Rect(sx - 12, sy - 12, 24, 24),
        "forest": pygame.Rect(18, 18, 42, 40),
        "lake": pygame.Rect(sx - 20, sy - 38, 40, 20),
        "cliffs": pygame.Rect(width - 56, 18, 34, 44),
        "polluted": pygame.Rect(width - 64, height - 44, 34, 26),
        "igloo_village": pygame.Rect(sx - 14, sy - 10, 28, 20),
    }

    return zones


def apply_lake_zone(tiles, zone, width, height):
    cx = zone.left + zone.width / 2
    cy = zone.top + zone.height / 2

    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if not in_bounds(x, y, width, height):
                continue

            dx = (x - cx) / (zone.width * 0.45)
            dy = (y - cy) / (zone.height * 0.45)
            dist = dx * dx + dy * dy

            if dist < 0.95:
                tiles[y][x] = 1


def apply_polluted_zone(tiles, zone, width, height):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if not in_bounds(x, y, width, height):
                continue

            if tiles[y][x] != 0:
                tiles[y][x] = 4


def apply_cliff_zone(tiles, zone, width, height):
    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if not in_bounds(x, y, width, height):
                continue

            if tiles[y][x] == 2 and (x + y) % 4 != 0:
                tiles[y][x] = 1


def apply_igloo_village_zone(tiles, zone, width, height, spawn_tile):
    sx, sy = spawn_tile

    for y in range(zone.top, zone.bottom):
        for x in range(zone.left, zone.right):
            if not in_bounds(x, y, width, height):
                continue

            if tiles[y][x] == 0:
                continue

            if abs(x - sx) <= 4 and abs(y - sy) <= 3:
                tiles[y][x] = 3
            else:
                tiles[y][x] = 3


def carve_path_line(tiles, x1, y1, x2, y2, width, height, thickness=1):
    x = x1
    y = y1

    while x != x2:
        step = 1 if x2 > x else -1
        x += step
        for oy in range(-thickness, thickness + 1):
            for ox in range(-thickness, thickness + 1):
                tx = x + ox
                ty = y + oy
                if in_bounds(tx, ty, width, height) and tiles[ty][tx] != 0:
                    tiles[ty][tx] = 3

    while y != y2:
        step = 1 if y2 > y else -1
        y += step
        for oy in range(-thickness, thickness + 1):
            for ox in range(-thickness, thickness + 1):
                tx = x + ox
                ty = y + oy
                if in_bounds(tx, ty, width, height) and tiles[ty][tx] != 0:
                    tiles[ty][tx] = 3


def connect_paths(tiles, zones, spawn_tile, width, height):
    sx, sy = spawn_tile

    forest = zones["forest"]
    lake = zones["lake"]
    polluted = zones["polluted"]

    for x in range(forest.right - 2, sx + 1):
        for y in range(sy + 10, sy + 13):
            if in_bounds(x, y, width, height) and tiles[y][x] != 0:
                tiles[y][x] = 3

    for y in range(lake.bottom, sy - 1):
        for x in range(sx - 1, sx + 2):
            if in_bounds(x, y, width, height) and tiles[y][x] != 0:
                tiles[y][x] = 3

    for x in range(sx, polluted.left + 4):
        for y in range(sy + 18, sy + 21):
            if in_bounds(x, y, width, height) and tiles[y][x] != 0:
                tiles[y][x] = 3

    for y in range(sy + 19, polluted.top + 8):
        for x in range(polluted.left + 2, polluted.left + 5):
            if in_bounds(x, y, width, height) and tiles[y][x] != 0:
                tiles[y][x] = 3


def connect_paths_to_all_npcs(tiles, spawn_tile, width, height):
    sx, sy = spawn_tile

    for npc in NPCS_DATA:
        tx = npc["tile_x"]
        ty = npc["tile_y"]

        # part du spawn puis relie en L
        carve_path_line(tiles, sx, sy, tx, sy, width, height, thickness=1)
        carve_path_line(tiles, tx, sy, tx, ty, width, height, thickness=1)

        # petite place autour du npc
        for y in range(ty - 1, ty + 2):
            for x in range(tx - 1, tx + 2):
                if in_bounds(x, y, width, height) and tiles[y][x] != 0:
                    tiles[y][x] = 3


def generate_world_data(width, height, spawn_tile):
    tiles = generate_base_tiles(width, height)
    carve_spawn_zone(tiles, spawn_tile, width, height)

    zones = create_zones(width, height, spawn_tile)

    apply_lake_zone(tiles, zones["lake"], width, height)
    apply_cliff_zone(tiles, zones["cliffs"], width, height)
    apply_polluted_zone(tiles, zones["polluted"], width, height)
    apply_igloo_village_zone(tiles, zones["igloo_village"], width, height, spawn_tile)

    connect_paths(tiles, zones, spawn_tile, width, height)
    connect_paths_to_all_npcs(tiles, spawn_tile, width, height)

    decorations, collision_rects = generate_zone_decorations(
        tiles=tiles,
        zones=zones,
        width=width,
        height=height,
        spawn_tile=spawn_tile
    )

    return {
        "tiles": tiles,
        "decorations": decorations,
        "collision_rects": collision_rects,
        "zones": zones,
    }