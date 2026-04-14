import random
import pygame
from constants import TILE_SIZE
from .config import (
    IGLOO_COLLISIONS,
    IGLOO_VILLAGE_LAYOUT,
    FOREST_PINE_CHANCE,
    FOREST_ROCK_CHANCE,
    LAKE_BIG_CRACK_CHANCE,
    LAKE_ICE_CHUNK_CHANCE,
    CLIFF_ICE_CHANCE,
    CLIFF_SNOW_CRACK_CHANCE,
    POLLUTED_BARREL_CHANCE,
    POLLUTED_TRASH_CHANCE,
    POLLUTED_OIL_CHANCE,
    POLLUTED_TREE_CHANCE,
    POLLUTED_SIGN_CHANCE,
    VILLAGE_PINE_CHANCE,
    VILLAGE_ROCK_CHANCE,
    GLOBAL_ROCK_CHANCE,
    GLOBAL_PINE_CHANCE,
    GLOBAL_SNOW_CRACK_CHANCE,
    GLOBAL_ICE_CRACK_CHANCE,
    POLLUTION_WARNING_OFFSETS,
    EDGE_ICEBERG_POSITIONS,
    BEAR_POLLUTED_TREES,
)


def generate_zone_decorations(tiles, zones, width, height, spawn_tile):
    decorations = []
    collision_rects = []

    sx, sy = spawn_tile
    spawn_safe_zone = pygame.Rect(
        (sx - 4) * TILE_SIZE,
        (sy - 4) * TILE_SIZE,
        8 * TILE_SIZE,
        8 * TILE_SIZE
    )

    forest = zones["forest"]
    lake = zones["lake"]
    cliffs = zones["cliffs"]
    polluted = zones["polluted"]
    igloo_village = zones["igloo_village"]

    village_cx = igloo_village.left + igloo_village.width // 2
    village_cy = igloo_village.top + igloo_village.height // 2

    for dx, dy, size in IGLOO_VILLAGE_LAYOUT:
        tx = village_cx + dx
        ty = village_cy + dy

        if not (0 <= tx < width and 0 <= ty < height):
            continue
        if tiles[ty][tx] == 0:
            continue

        px = tx * TILE_SIZE
        py = ty * TILE_SIZE

        data = IGLOO_COLLISIONS[size]
        rect_off_x, rect_off_y = data["rect_offset"]
        rect_w, rect_h = data["rect_size"]
        deco_off_x, deco_off_y = data["deco_offset"]

        rect = pygame.Rect(px + rect_off_x, py + rect_off_y, rect_w, rect_h)
        deco_x = px + deco_off_x
        deco_y = py + deco_off_y

        if not rect.colliderect(spawn_safe_zone):
            decorations.append({
                "type": "igloo",
                "x": deco_x,
                "y": deco_y,
                "size": size
            })
            collision_rects.append(rect)

    for y in range(height):
        for x in range(width):
            tile = tiles[y][x]
            px = x * TILE_SIZE
            py = y * TILE_SIZE
            tile_rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)

            if tile == 3:
                continue

            if forest.collidepoint(x, y) and tile == 2:
                r = random.random()

                if r < FOREST_PINE_CHANCE:
                    rect = pygame.Rect(px + 8, py + 16, 16, 10)
                    if not rect.colliderect(spawn_safe_zone):
                        decorations.append({
                            "type": "snow_pine",
                            "x": px,
                            "y": py - 6,
                            "size": random.randint(0, 1)
                        })
                        collision_rects.append(rect)

                elif r < FOREST_ROCK_CHANCE:
                    rect = pygame.Rect(px + 7, py + 14, 18, 10)
                    if not rect.colliderect(spawn_safe_zone):
                        decorations.append({
                            "type": "rock_snow",
                            "x": px + random.randint(1, 5),
                            "y": py + random.randint(5, 9),
                            "size": random.randint(0, 1)
                        })
                        collision_rects.append(rect)

            elif lake.collidepoint(x, y) and tile == 1:
                r = random.random()

                if r < LAKE_BIG_CRACK_CHANCE:
                    decorations.append({
                        "type": "ice_crack_big",
                        "x": px,
                        "y": py,
                        "variant": random.randint(0, 2)
                    })

                elif r < LAKE_ICE_CHUNK_CHANCE:
                    rect = pygame.Rect(px + 10, py + 15, 12, 9)
                    decorations.append({
                        "type": "ice_chunk",
                        "x": px + random.randint(2, 6),
                        "y": py + random.randint(5, 9),
                        "size": random.randint(0, 1)
                    })
                    collision_rects.append(rect)

            elif cliffs.collidepoint(x, y) and tile in (1, 2):
                r = random.random()

                if r < CLIFF_ICE_CHANCE:
                    rect = pygame.Rect(px + 6, py + 16, 20, 10)
                    decorations.append({
                        "type": "cliff_ice",
                        "x": px,
                        "y": py + 2,
                        "size": random.randint(0, 1)
                    })
                    collision_rects.append(rect)

                elif r < CLIFF_SNOW_CRACK_CHANCE:
                    decorations.append({
                        "type": "snow_crack",
                        "x": px,
                        "y": py,
                        "variant": random.randint(0, 2)
                    })

            elif polluted.collidepoint(x, y) and tile in (2, 4):
                r = random.random()

                if r < POLLUTED_TREE_CHANCE:
                    rect = pygame.Rect(px + 8, py + 16, 16, 10)
                    decorations.append({
                        "type": "polluted_tree",
                        "x": px,
                        "y": py - 6,
                        "size": random.randint(0, 1)
                    })
                    collision_rects.append(rect)

                elif r < POLLUTED_TREE_CHANCE + POLLUTED_SIGN_CHANCE:
                    rect = pygame.Rect(px + 10, py + 16, 12, 10)
                    decorations.append({
                        "type": "polluted_sign",
                        "x": px,
                        "y": py + 1
                    })
                    collision_rects.append(rect)

                elif r < POLLUTED_TREE_CHANCE + POLLUTED_SIGN_CHANCE + POLLUTED_BARREL_CHANCE:
                    rect = pygame.Rect(px + 9, py + 14, 14, 12)
                    decorations.append({
                        "type": "toxic_barrel",
                        "x": px + 4,
                        "y": py + 6
                    })
                    collision_rects.append(rect)

                elif r < POLLUTED_TREE_CHANCE + POLLUTED_SIGN_CHANCE + POLLUTED_BARREL_CHANCE + POLLUTED_TRASH_CHANCE:
                    rect = pygame.Rect(px + 7, py + 15, 18, 10)
                    decorations.append({
                        "type": "trash_pile",
                        "x": px + 2,
                        "y": py + 7,
                        "size": random.randint(0, 1)
                    })
                    collision_rects.append(rect)

                elif r < (
                    POLLUTED_TREE_CHANCE
                    + POLLUTED_SIGN_CHANCE
                    + POLLUTED_BARREL_CHANCE
                    + POLLUTED_TRASH_CHANCE
                    + POLLUTED_OIL_CHANCE
                ):
                    decorations.append({
                        "type": "oil_stain",
                        "x": px + 2,
                        "y": py + 10,
                        "size": random.randint(0, 1)
                    })

            elif igloo_village.collidepoint(x, y) and tile == 2:
                r = random.random()

                if r < VILLAGE_PINE_CHANCE and abs(x - village_cx) > 4:
                    rect = pygame.Rect(px + 8, py + 16, 16, 10)
                    if not rect.colliderect(spawn_safe_zone):
                        decorations.append({
                            "type": "snow_pine",
                            "x": px,
                            "y": py - 6,
                            "size": random.randint(0, 1)
                        })
                        collision_rects.append(rect)

                elif r < VILLAGE_ROCK_CHANCE:
                    decorations.append({
                        "type": "rock_snow",
                        "x": px + random.randint(2, 5),
                        "y": py + random.randint(5, 9),
                        "size": random.randint(0, 1)
                    })

            elif tile == 2 and not tile_rect.colliderect(spawn_safe_zone):
                r = random.random()

                if r < GLOBAL_ROCK_CHANCE:
                    rect = pygame.Rect(px + 7, py + 14, 18, 10)
                    decorations.append({
                        "type": "rock_snow",
                        "x": px + random.randint(2, 5),
                        "y": py + random.randint(5, 9),
                        "size": random.randint(0, 1)
                    })
                    collision_rects.append(rect)

                elif r < GLOBAL_PINE_CHANCE:
                    rect = pygame.Rect(px + 8, py + 16, 16, 10)
                    decorations.append({
                        "type": "snow_pine",
                        "x": px,
                        "y": py - 6,
                        "size": random.randint(0, 1)
                    })
                    collision_rects.append(rect)

                elif r < GLOBAL_SNOW_CRACK_CHANCE:
                    decorations.append({
                        "type": "snow_crack",
                        "x": px,
                        "y": py,
                        "variant": random.randint(0, 2)
                    })

            elif tile == 1 and not tile_rect.colliderect(spawn_safe_zone):
                if random.random() < GLOBAL_ICE_CRACK_CHANCE:
                    decorations.append({
                        "type": "ice_crack_big",
                        "x": px,
                        "y": py,
                        "variant": random.randint(0, 2)
                    })

    add_fixed_pollution_details(decorations, collision_rects, zones, tiles, width, height)
    add_edge_icebergs(decorations, collision_rects, tiles, width, height)
    add_bear_polluted_trees(decorations, collision_rects, tiles, width, height)

    return decorations, collision_rects


def add_fixed_pollution_details(decorations, collision_rects, zones, tiles, width, height):
    polluted = zones["polluted"]

    for dx, dy in POLLUTION_WARNING_OFFSETS:
        tx = polluted.left + dx
        ty = polluted.top + dy

        if 0 <= tx < width and 0 <= ty < height and tiles[ty][tx] != 0:
            px = tx * TILE_SIZE
            py = ty * TILE_SIZE
            decorations.append({"type": "polluted_sign", "x": px, "y": py})
            collision_rects.append(pygame.Rect(px + 10, py + 16, 12, 10))


def add_bear_polluted_trees(decorations, collision_rects, tiles, width, height):
    for tx, ty in BEAR_POLLUTED_TREES:
        if not (0 <= tx < width and 0 <= ty < height):
            continue

        if tiles[ty][tx] == 0 or tiles[ty][tx] == 3:
            continue

        px = tx * TILE_SIZE
        py = ty * TILE_SIZE

        decorations.append({
            "type": "polluted_tree",
            "x": px,
            "y": py - 6,
            "size": random.randint(0, 1)
        })
        collision_rects.append(pygame.Rect(px + 8, py + 16, 16, 10))


def add_edge_icebergs(decorations, collision_rects, tiles, width, height):
    for tx, ty in EDGE_ICEBERG_POSITIONS:
        if not (0 <= tx < width and 0 <= ty < height):
            continue

        if tiles[ty][tx] != 0:
            decorations.append({
                "type": "iceberg",
                "x": tx * TILE_SIZE - 8,
                "y": ty * TILE_SIZE - 6,
                "size": random.randint(0, 1)
            })
            collision_rects.append(
                pygame.Rect(tx * TILE_SIZE + 6, ty * TILE_SIZE + 12, 20, 12)
            )