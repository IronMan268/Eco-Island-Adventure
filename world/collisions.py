from constants import TILE_SIZE


def in_bounds(x, y, width, height):
    return 0 <= x < width and 0 <= y < height


def rect_collides_world(rect, tiles, collision_rects, width, height, pixel_width, pixel_height):
    if rect.left < 0 or rect.top < 0 or rect.right > pixel_width or rect.bottom > pixel_height:
        return True

    points = [
        (rect.left + 2, rect.top + 2),
        (rect.right - 2, rect.top + 2),
        (rect.left + 2, rect.bottom - 2),
        (rect.right - 2, rect.bottom - 2),
        (rect.centerx, rect.centery),
    ]

    for px, py in points:
        tx = px // TILE_SIZE
        ty = py // TILE_SIZE

        if not in_bounds(tx, ty, width, height):
            return True

        if tiles[ty][tx] == 0:
            return True

    for collision_rect in collision_rects:
        if rect.colliderect(collision_rect):
            return True

    return False