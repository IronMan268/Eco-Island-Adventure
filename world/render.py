import pygame
from constants import WIDTH, HEIGHT, TILE_SIZE
from .tiles import (
    draw_water_tile,
    draw_ice_tile,
    draw_snow_tile,
    draw_path_tile,
    draw_dirty_snow_tile,
)
from .decorations import draw_decoration


def draw_world(screen, camera_x, camera_y, tiles, decorations, width, height):
    screen.fill((12, 26, 58))

    start_x = max(0, camera_x // TILE_SIZE)
    start_y = max(0, camera_y // TILE_SIZE)
    end_x = min(width, (camera_x + WIDTH) // TILE_SIZE + 2)
    end_y = min(height, (camera_y + HEIGHT) // TILE_SIZE + 2)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = tiles[y][x]
            px = x * TILE_SIZE - camera_x
            py = y * TILE_SIZE - camera_y

            if tile == 0:
                draw_water_tile(screen, px, py, x, y)
            elif tile == 1:
                draw_ice_tile(screen, px, py, x, y)
            elif tile == 2:
                draw_snow_tile(screen, px, py, x, y)
            elif tile == 3:
                draw_path_tile(screen, px, py, x, y)
            elif tile == 4:
                draw_dirty_snow_tile(screen, px, py, x, y)

    visible_decor = []
    cam_rect = pygame.Rect(camera_x - 96, camera_y - 96, WIDTH + 192, HEIGHT + 192)

    for deco in decorations:
        deco_rect = pygame.Rect(deco["x"], deco["y"], 96, 96)
        if deco_rect.colliderect(cam_rect):
            visible_decor.append(deco)

    visible_decor.sort(key=lambda d: d["y"])

    for deco in visible_decor:
        draw_decoration(screen, deco, camera_x, camera_y)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((180, 210, 255, 18))
    screen.blit(overlay, (0, 0))