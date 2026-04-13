import math
import pygame
from constants import *


def trim_transparent(surface):
    mask = pygame.mask.from_surface(surface)
    rects = mask.get_bounding_rects()

    if not rects:
        return surface.copy()

    rect = rects[0]
    return surface.subsurface(rect).copy()


class Player:
    def __init__(self, x, y):
        self.direction = "down"
        self.target_height = 42

        slide_left = self.load_scaled_sprite("assets/player/slide_left.png")
        slide_right = self.load_scaled_sprite("assets/player/slide_right.png")

        slide_scale = 0.6
        slide_left = pygame.transform.scale(
            slide_left,
            (int(slide_left.get_width() * slide_scale),
             int(slide_left.get_height() * slide_scale))
        )
        slide_right = pygame.transform.scale(
            slide_right,
            (int(slide_right.get_width() * slide_scale),
             int(slide_right.get_height() * slide_scale))
        )

        self.base_sprites = {
            "down": self.load_scaled_sprite("assets/player/penguin_down.png"),
            "up": self.load_scaled_sprite("assets/player/penguin_up.png"),
            "left": slide_left,
            "right": slide_right,
        }

        self.down_walk_frames = [
            self.load_scaled_sprite("assets/player/penguin_down_left.png"),
            self.base_sprites["down"],
            self.load_scaled_sprite("assets/player/penguin_down_right.png"),
            self.base_sprites["down"],
        ]
        self.down_walk_frames = [
            frame if frame is not None else self.base_sprites["down"]
            for frame in self.down_walk_frames
        ]

        self.up_walk_frames = [
            self.load_scaled_sprite("assets/player/penguin_up_left.png"),
            self.base_sprites["up"],
            self.load_scaled_sprite("assets/player/penguin_up_right.png"),
            self.base_sprites["up"],
        ]
        self.up_walk_frames = [
            frame if frame is not None else self.base_sprites["up"]
            for frame in self.up_walk_frames
        ]

        hitbox_width = 22
        hitbox_height = 18

        self.x = float(x)
        self.y = float(y)

        self.rect = pygame.Rect(int(self.x), int(self.y), hitbox_width, hitbox_height)

        self.is_moving = False
        self.anim_time = 0.0
        self.walk_frame_time = 0.0

        self.sprite_ground_offset = 2

        self.walk_anim_speed = 8.0
        self.slide_anim_speed = 11.0

    def load_scaled_sprite(self, path):
        image = pygame.image.load(path).convert_alpha()
        trimmed = trim_transparent(image)

        img_w, img_h = trimmed.get_size()
        scale = self.target_height / img_h

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        return pygame.transform.scale(trimmed, (new_w, new_h))

    def update(self, keys, world, dt):
        move_x = 0.0
        move_y = 0.0

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            move_x = -PLAYER_SPEED
            self.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = PLAYER_SPEED
            self.direction = "right"

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            move_y = -PLAYER_SPEED
            self.direction = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = PLAYER_SPEED
            self.direction = "down"

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        self.is_moving = (move_x != 0 or move_y != 0)

        if self.is_moving:
            self.anim_time += dt

            if self.direction in ("left", "right"):
                self.walk_frame_time += dt * self.slide_anim_speed
            else:
                self.walk_frame_time += dt * self.walk_anim_speed
        else:
            self.anim_time = 0.0
            self.walk_frame_time = 0.0

        if move_x != 0:
            new_rect = self.rect.copy()
            new_x = self.x + move_x * dt
            new_rect.x = int(new_x)

            if not world.rect_collides(new_rect):
                self.x = new_x
                self.rect.x = int(self.x)

        if move_y != 0:
            new_rect = self.rect.copy()
            new_y = self.y + move_y * dt
            new_rect.y = int(new_y)

            if not world.rect_collides(new_rect):
                self.y = new_y
                self.rect.y = int(self.y)

    def get_current_sprite(self):
        if not self.is_moving:
            return self.base_sprites[self.direction]

        if self.direction == "down":
            index = int(self.walk_frame_time) % len(self.down_walk_frames)
            return self.down_walk_frames[index]

        if self.direction == "up":
            index = int(self.walk_frame_time) % len(self.up_walk_frames)
            return self.up_walk_frames[index]

        return self.base_sprites[self.direction]

    def get_slide_transform(self, sprite):
        if not self.is_moving or self.direction not in ("left", "right"):
            return sprite, 0, 0, 1.0

        t = self.anim_time * self.slide_anim_speed

        wave = math.sin(t * 2.2)

        bounce_y = int(abs(math.sin(t * 2.2)) * 2)

        side = -1 if self.direction == "left" else 1
        sway_x = int(wave * 2 * side)

        width = sprite.get_width()
        height = sprite.get_height()

        stretch_x = 1.0 + abs(math.sin(t * 2.2)) * 0.06
        stretch_y = 1.0 - abs(math.sin(t * 2.2)) * 0.04

        new_w = max(1, int(width * stretch_x))
        new_h = max(1, int(height * stretch_y))

        transformed = pygame.transform.smoothscale(sprite, (new_w, new_h))

        shadow_factor = 1.0 - abs(wave) * 0.10

        return transformed, bounce_y, sway_x, shadow_factor

    def get_animated_sprite(self):
        sprite = self.get_current_sprite()

        if not self.is_moving:
            return sprite, 0, 0, 1.0

        if self.direction in ("down", "up"):
            return sprite, 0, 0, 0.94

        return self.get_slide_transform(sprite)

    def draw(self, screen, camera_x, camera_y):
        sprite, bounce_y, sway_x, shadow_factor = self.get_animated_sprite()

        draw_x = self.rect.centerx - sprite.get_width() // 2 - camera_x + sway_x
        draw_y = (
            self.rect.bottom
            - sprite.get_height()
            - camera_y
            + self.sprite_ground_offset
            - bounce_y
        )

        shadow_w = max(12, int(self.rect.width * shadow_factor))
        shadow_h = 4
        shadow_x = self.rect.centerx - shadow_w // 2 - camera_x
        shadow_y = self.rect.bottom - camera_y + 1

        shadow_surface = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 45), (0, 0, shadow_w, shadow_h))

        screen.blit(shadow_surface, (shadow_x, shadow_y))
        screen.blit(sprite, (draw_x, draw_y))