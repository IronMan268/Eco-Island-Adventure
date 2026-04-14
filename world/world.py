from constants import TILE_SIZE
from .generation import generate_world_data
from .collisions import rect_collides_world
from .render import draw_world
import pygame


class World:
    def __init__(self):
        self.width = 220
        self.height = 150

        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE

        self.spawn_tile = (self.width // 2, self.height // 2)

        self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.decorations = []
        self.collision_rects = []
        self.zones = {}
        self.sign_rect = pygame.Rect(0, 0, 1, 1)

        self.generate_world()

    def generate_world(self):
        data = generate_world_data(self.width, self.height, self.spawn_tile)
        self.tiles = data["tiles"]
        self.decorations = data["decorations"]
        self.collision_rects = data["collision_rects"]
        self.zones = data["zones"]
        self.sign_rect = data["sign_rect"]

    def get_spawn_position(self):
        x = self.spawn_tile[0] * TILE_SIZE + 5
        y = self.spawn_tile[1] * TILE_SIZE + 12
        return x, y

    def get_sign_rect(self):
        return self.sign_rect

    def get_tile(self, tile_x, tile_y):
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x]
        return 0

    def get_tile_at_pixel(self, px, py):
        tile_x = int(px // TILE_SIZE)
        tile_y = int(py // TILE_SIZE)
        return self.get_tile(tile_x, tile_y)

    def is_water_at_pixel(self, px, py):
        return self.get_tile_at_pixel(px, py) == 0

    def rect_collides(self, rect):
        return rect_collides_world(
            rect=rect,
            tiles=self.tiles,
            collision_rects=self.collision_rects,
            width=self.width,
            height=self.height,
            pixel_width=self.pixel_width,
            pixel_height=self.pixel_height,
        )

    def update_bear_trees(self, mission_done):
        for deco in self.decorations:
            if deco.get("zone_tag") == "bear_forest":
                if mission_done:
                    if deco.get("type") == "polluted_tree":
                        deco["type"] = "snow_pine"
                else:
                    if deco.get("type") == "snow_pine":
                        deco["type"] = "polluted_tree"

    def draw(self, screen, camera_x, camera_y):
        draw_world(
            screen=screen,
            camera_x=camera_x,
            camera_y=camera_y,
            tiles=self.tiles,
            decorations=self.decorations,
            width=self.width,
            height=self.height,
        )