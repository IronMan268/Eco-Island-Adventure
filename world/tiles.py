import pygame
from constants import TILE_SIZE


def draw_snow_tile(screen, px, py, x, y):
    colors = [
        (240, 247, 255),
        (234, 242, 252),
        (245, 250, 255),
        (229, 238, 248),
    ]
    color = colors[(x + y) % len(colors)]
    pygame.draw.rect(screen, color, (px, py, TILE_SIZE, TILE_SIZE))
    pygame.draw.circle(screen, (220, 232, 246), (px + 8, py + 10), 2)
    pygame.draw.circle(screen, (220, 232, 246), (px + 23, py + 20), 2)


def draw_ice_tile(screen, px, py, x, y):
    colors = [
        (180, 214, 250),
        (170, 206, 244),
        (189, 222, 255),
        (163, 198, 236),
    ]
    color = colors[(x + y) % len(colors)]
    pygame.draw.rect(screen, color, (px, py, TILE_SIZE, TILE_SIZE))

    pygame.draw.line(screen, (210, 236, 255), (px + 5, py + 8), (px + 15, py + 6), 1)
    pygame.draw.line(screen, (145, 180, 220), (px + 15, py + 18), (px + 25, py + 23), 1)

    if (x * 11 + y * 7) % 9 == 0:
        pygame.draw.line(screen, (118, 156, 196), (px + 7, py + 9), (px + 22, py + 21), 1)


def draw_water_tile(screen, px, py, x, y):
    colors = [
        (16, 48, 95),
        (12, 42, 84),
        (18, 56, 106),
        (15, 46, 92),
    ]
    color = colors[(x + y) % len(colors)]
    pygame.draw.rect(screen, color, (px, py, TILE_SIZE, TILE_SIZE))
    pygame.draw.arc(screen, (72, 126, 190), (px + 5, py + 10, 12, 6), 0, 3.14, 1)
    pygame.draw.arc(screen, (72, 126, 190), (px + 16, py + 18, 10, 5), 0, 3.14, 1)


def draw_path_tile(screen, px, py, x, y):
    colors = [
        (222, 235, 248),
        (214, 228, 242),
        (229, 240, 251),
    ]
    color = colors[(x + y) % len(colors)]
    pygame.draw.rect(screen, color, (px, py, TILE_SIZE, TILE_SIZE))
    pygame.draw.line(screen, (198, 214, 232), (px, py + 31), (px + 31, py + 31), 1)
    pygame.draw.circle(screen, (237, 245, 255), (px + 11, py + 12), 2)


def draw_dirty_snow_tile(screen, px, py, x, y):
    colors = [
        (205, 214, 210),
        (196, 205, 202),
        (214, 220, 216),
        (188, 198, 194),
    ]
    color = colors[(x + y) % len(colors)]
    pygame.draw.rect(screen, color, (px, py, TILE_SIZE, TILE_SIZE))
    pygame.draw.circle(screen, (160, 170, 166), (px + 9, py + 11), 2)
    pygame.draw.circle(screen, (150, 158, 154), (px + 21, py + 20), 2)