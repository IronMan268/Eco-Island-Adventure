import os
import pygame
from .config import (
    IGLOO_IMAGE_PATH,
    IGLOO_SIZES,
    IGLOO_DRAW_OFFSET_X,
    IGLOO_DRAW_OFFSET_Y,
    SNOW_PINE_IMAGE_PATH,
    POLLUTED_TREE_IMAGE_PATH,
    POLLUTED_SIGN_IMAGE_PATH,
)

_igloo_cache = {}
_image_cache = {}


def trim_transparent(surface):
    mask = pygame.mask.from_surface(surface)
    rects = mask.get_bounding_rects()

    if not rects:
        return surface.copy()

    rect = rects[0]
    return surface.subsurface(rect).copy()


def load_cached_image(path, size):
    key = (path, size)

    if key in _image_cache:
        return _image_cache[key]

    if not os.path.exists(path):
        _image_cache[key] = None
        return None

    try:
        image = pygame.image.load(path).convert_alpha()
        image = trim_transparent(image)

        if size is not None:
            image = pygame.transform.scale(image, size)

        _image_cache[key] = image
        return image
    except Exception:
        _image_cache[key] = None
        return None


def get_igloo_sprite(size):
    if size in _igloo_cache:
        return _igloo_cache[size]

    img = pygame.image.load(IGLOO_IMAGE_PATH).convert_alpha()
    img = trim_transparent(img)

    target_w, target_h = IGLOO_SIZES.get(size, IGLOO_SIZES[1])
    sprite = pygame.transform.scale(img, (target_w, target_h))
    _igloo_cache[size] = sprite
    return sprite


def draw_decoration(screen, deco, camera_x, camera_y):
    x = deco["x"] - camera_x
    y = deco["y"] - camera_y
    t = deco["type"]

    if t == "rock_snow":
        draw_rock_snow(screen, x, y, deco.get("size", 0))
    elif t == "ice_chunk":
        draw_ice_chunk(screen, x, y, deco.get("size", 0))
    elif t == "snow_pine":
        draw_snow_pine(screen, x, y, deco.get("size", 0))
    elif t == "snow_crack":
        draw_snow_crack(screen, x, y, deco.get("variant", 0))
    elif t == "ice_crack_big":
        draw_ice_crack_big(screen, x, y, deco.get("variant", 0))
    elif t == "iceberg":
        draw_iceberg(screen, x, y, deco.get("size", 0))
    elif t == "cliff_ice":
        draw_cliff_ice(screen, x, y, deco.get("size", 0))
    elif t == "toxic_barrel":
        draw_toxic_barrel(screen, x, y)
    elif t == "trash_pile":
        draw_trash_pile(screen, x, y, deco.get("size", 0))
    elif t == "oil_stain":
        draw_oil_stain(screen, x, y, deco.get("size", 0))
    elif t == "warning_sign":
        draw_warning_sign(screen, x, y)
    elif t == "igloo":
        draw_igloo(screen, x, y, deco.get("size", 0))
    elif t == "pancarte_centrale":
        draw_pancarte_centrale(screen, x, y)
    elif t == "polluted_tree":
        draw_polluted_tree(screen, x, y, deco.get("size", 0))
    elif t == "polluted_sign":
        draw_polluted_sign(screen, x, y)


def draw_rock_snow(screen, x, y, size):
    if size == 0:
        pygame.draw.ellipse(screen, (115, 123, 138), (x, y + 6, 16, 9))
        pygame.draw.ellipse(screen, (240, 246, 255), (x + 2, y + 3, 11, 5))
    else:
        pygame.draw.ellipse(screen, (103, 112, 128), (x, y + 4, 20, 12))
        pygame.draw.ellipse(screen, (238, 245, 255), (x + 3, y + 1, 14, 6))


def draw_ice_chunk(screen, x, y, size):
    if size == 0:
        pygame.draw.polygon(screen, (188, 226, 255), [
            (x + 2, y + 12), (x + 10, y + 2), (x + 18, y + 12), (x + 10, y + 18)
        ])
        pygame.draw.line(screen, (228, 245, 255), (x + 10, y + 4), (x + 10, y + 14), 1)
    else:
        pygame.draw.polygon(screen, (175, 215, 248), [
            (x + 1, y + 14), (x + 10, y + 1), (x + 21, y + 10), (x + 13, y + 20), (x + 4, y + 18)
        ])
        pygame.draw.line(screen, (226, 243, 255), (x + 9, y + 5), (x + 15, y + 12), 1)


def draw_snow_pine(screen, x, y, size):
    image = load_cached_image(
        SNOW_PINE_IMAGE_PATH,
        (34, 42) if size == 0 else (42, 50)
    )

    if image:
        shadow = pygame.Surface((28, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 35), (0, 0, 28, 8))
        screen.blit(shadow, (x + 4, y + 28))
        screen.blit(image, (x - 1, y - 10))
        return

    # Fallback si l'image n'existe pas encore
    trunk_h = 12 if size == 0 else 14

    shadow = pygame.Surface((24, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 35), (0, 0, 24, 8))
    screen.blit(shadow, (x + 4, y + 26))

    pygame.draw.rect(screen, (92, 66, 44), (x + 12, y + 18, 6, trunk_h))
    pygame.draw.polygon(screen, (52, 98, 78), [(x + 15, y + 2), (x + 4, y + 18), (x + 26, y + 18)])
    pygame.draw.polygon(screen, (62, 113, 90), [(x + 15, y + 8), (x + 2, y + 22), (x + 28, y + 22)])
    pygame.draw.polygon(screen, (74, 130, 102), [(x + 15, y + 14), (x, y + 28), (x + 30, y + 28)])

    pygame.draw.arc(screen, (243, 248, 255), (x + 6, y + 10, 7, 4), 0, 3.14, 2)
    pygame.draw.arc(screen, (243, 248, 255), (x + 17, y + 14, 8, 4), 0, 3.14, 2)
    pygame.draw.arc(screen, (243, 248, 255), (x + 10, y + 20, 10, 4), 0, 3.14, 2)


def draw_snow_crack(screen, x, y, variant):
    color = (196, 208, 226)
    if variant == 0:
        pygame.draw.line(screen, color, (x + 8, y + 8), (x + 16, y + 16), 1)
        pygame.draw.line(screen, color, (x + 16, y + 16), (x + 23, y + 12), 1)
    elif variant == 1:
        pygame.draw.line(screen, color, (x + 10, y + 6), (x + 14, y + 16), 1)
        pygame.draw.line(screen, color, (x + 14, y + 16), (x + 20, y + 20), 1)
    else:
        pygame.draw.line(screen, color, (x + 6, y + 18), (x + 15, y + 12), 1)
        pygame.draw.line(screen, color, (x + 15, y + 12), (x + 23, y + 19), 1)


def draw_ice_crack_big(screen, x, y, variant):
    color = (116, 155, 196)
    if variant == 0:
        pygame.draw.line(screen, color, (x + 4, y + 10), (x + 15, y + 14), 1)
        pygame.draw.line(screen, color, (x + 15, y + 14), (x + 24, y + 7), 1)
        pygame.draw.line(screen, color, (x + 15, y + 14), (x + 22, y + 22), 1)
    elif variant == 1:
        pygame.draw.line(screen, color, (x + 8, y + 6), (x + 18, y + 15), 1)
        pygame.draw.line(screen, color, (x + 18, y + 15), (x + 26, y + 12), 1)
        pygame.draw.line(screen, color, (x + 18, y + 15), (x + 14, y + 24), 1)
    else:
        pygame.draw.line(screen, color, (x + 6, y + 22), (x + 14, y + 12), 1)
        pygame.draw.line(screen, color, (x + 14, y + 12), (x + 24, y + 9), 1)
        pygame.draw.line(screen, color, (x + 14, y + 12), (x + 21, y + 20), 1)


def draw_iceberg(screen, x, y, size):
    if size == 0:
        pygame.draw.polygon(screen, (194, 229, 255), [
            (x + 3, y + 22), (x + 12, y + 6), (x + 21, y + 10),
            (x + 28, y + 20), (x + 22, y + 27), (x + 8, y + 27)
        ])
        pygame.draw.line(screen, (230, 245, 255), (x + 12, y + 8), (x + 16, y + 17), 1)
    else:
        pygame.draw.polygon(screen, (180, 217, 246), [
            (x + 2, y + 24), (x + 10, y + 8), (x + 22, y + 4),
            (x + 30, y + 14), (x + 28, y + 26), (x + 12, y + 29)
        ])
        pygame.draw.line(screen, (226, 241, 252), (x + 12, y + 8), (x + 17, y + 18), 1)
        pygame.draw.line(screen, (226, 241, 252), (x + 22, y + 6), (x + 22, y + 18), 1)


def draw_cliff_ice(screen, x, y, size):
    if size == 0:
        pygame.draw.polygon(screen, (155, 188, 218), [
            (x + 2, y + 20), (x + 8, y + 8), (x + 18, y + 6), (x + 26, y + 18), (x + 22, y + 28), (x + 6, y + 28)
        ])
        pygame.draw.polygon(screen, (210, 232, 248), [
            (x + 8, y + 8), (x + 18, y + 6), (x + 15, y + 12), (x + 10, y + 13)
        ])
    else:
        pygame.draw.polygon(screen, (138, 172, 202), [
            (x + 2, y + 23), (x + 8, y + 9), (x + 20, y + 5), (x + 29, y + 16), (x + 27, y + 29), (x + 8, y + 29)
        ])
        pygame.draw.polygon(screen, (201, 226, 244), [
            (x + 9, y + 10), (x + 20, y + 6), (x + 17, y + 13), (x + 10, y + 14)
        ])


def draw_toxic_barrel(screen, x, y):
    pygame.draw.rect(screen, (80, 120, 95), (x + 6, y + 4, 14, 18), border_radius=3)
    pygame.draw.rect(screen, (48, 74, 58), (x + 6, y + 8, 14, 2))
    pygame.draw.rect(screen, (48, 74, 58), (x + 6, y + 16, 14, 2))
    pygame.draw.circle(screen, (170, 220, 70), (x + 13, y + 13), 4)
    pygame.draw.line(screen, (50, 80, 35), (x + 13, y + 10), (x + 13, y + 16), 1)


def draw_trash_pile(screen, x, y, size):
    if size == 0:
        pygame.draw.ellipse(screen, (110, 110, 118), (x + 2, y + 9, 22, 10))
        pygame.draw.rect(screen, (140, 105, 72), (x + 8, y + 4, 7, 8))
        pygame.draw.rect(screen, (90, 136, 152), (x + 13, y + 6, 5, 7))
    else:
        pygame.draw.ellipse(screen, (104, 104, 112), (x + 1, y + 8, 26, 12))
        pygame.draw.rect(screen, (148, 112, 78), (x + 6, y + 3, 8, 9))
        pygame.draw.rect(screen, (84, 128, 146), (x + 15, y + 5, 6, 8))
        pygame.draw.rect(screen, (70, 70, 78), (x + 18, y + 7, 5, 5))


def draw_oil_stain(screen, x, y, size):
    if size == 0:
        pygame.draw.ellipse(screen, (28, 28, 32), (x + 1, y + 4, 22, 8))
        pygame.draw.ellipse(screen, (55, 80, 100), (x + 5, y + 6, 6, 2))
    else:
        pygame.draw.ellipse(screen, (24, 24, 28), (x, y + 3, 27, 10))
        pygame.draw.ellipse(screen, (60, 84, 106), (x + 7, y + 6, 8, 2))


def draw_warning_sign(screen, x, y):
    pygame.draw.rect(screen, (116, 88, 56), (x + 13, y + 14, 6, 16))
    pygame.draw.rect(screen, (236, 214, 82), (x + 4, y + 2, 24, 14), border_radius=2)
    pygame.draw.rect(screen, (80, 70, 35), (x + 4, y + 2, 24, 14), 2, border_radius=2)
    pygame.draw.polygon(screen, (40, 40, 40), [(x + 16, y + 5), (x + 10, y + 12), (x + 22, y + 12)])
    pygame.draw.line(screen, (40, 40, 40), (x + 16, y + 8), (x + 16, y + 10), 1)


def draw_igloo(screen, x, y, size):
    sprite = get_igloo_sprite(size)
    screen.blit(sprite, (x + IGLOO_DRAW_OFFSET_X, y + IGLOO_DRAW_OFFSET_Y))


def draw_pancarte_centrale(screen, x, y):
    shadow = pygame.Surface((32, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 40), (0, 0, 32, 10))
    screen.blit(shadow, (x, y + 34))

    pygame.draw.rect(screen, (109, 82, 55), (x + 14, y + 18, 6, 22))
    pygame.draw.rect(screen, (197, 166, 110), (x + 1, y + 2, 32, 18), border_radius=3)
    pygame.draw.rect(screen, (108, 82, 52), (x + 1, y + 2, 32, 18), 2, border_radius=3)

    pygame.draw.line(screen, (135, 102, 66), (x + 5, y + 8), (x + 29, y + 8), 1)
    pygame.draw.line(screen, (135, 102, 66), (x + 5, y + 12), (x + 25, y + 12), 1)


def draw_polluted_tree(screen, x, y, size):
    image = load_cached_image(POLLUTED_TREE_IMAGE_PATH, (36, 44) if size == 0 else (44, 52))

    if image:
        screen.blit(image, (x - 2, y - 10))
        return

    shadow = pygame.Surface((28, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 35), (0, 0, 28, 8))
    screen.blit(shadow, (x + 3, y + 28))

    pygame.draw.rect(screen, (82, 58, 36), (x + 13, y + 18, 6, 14))
    pygame.draw.polygon(screen, (70, 92, 62), [(x + 16, y + 3), (x + 5, y + 18), (x + 27, y + 18)])
    pygame.draw.polygon(screen, (88, 106, 66), [(x + 16, y + 10), (x + 3, y + 23), (x + 29, y + 23)])
    pygame.draw.polygon(screen, (96, 120, 70), [(x + 16, y + 15), (x + 1, y + 30), (x + 31, y + 30)])

    pygame.draw.circle(screen, (78, 135, 82), (x + 10, y + 17), 3)
    pygame.draw.circle(screen, (86, 150, 88), (x + 21, y + 21), 3)


def draw_polluted_sign(screen, x, y):
    image = load_cached_image(POLLUTED_SIGN_IMAGE_PATH, (28, 32))

    if image:
        screen.blit(image, (x + 2, y))
        return

    pygame.draw.rect(screen, (110, 85, 55), (x + 13, y + 12, 5, 18))
    pygame.draw.rect(screen, (214, 198, 90), (x + 4, y + 2, 24, 14), border_radius=2)
    pygame.draw.rect(screen, (80, 66, 35), (x + 4, y + 2, 24, 14), 2, border_radius=2)
    pygame.draw.line(screen, (45, 45, 45), (x + 9, y + 6), (x + 23, y + 12), 2)
    pygame.draw.line(screen, (45, 45, 45), (x + 23, y + 6), (x + 9, y + 12), 2)