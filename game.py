import pygame
from constants import *
from intro import Intro
from world import World
from player import Player
from pollution import PollutionSystem
from npc import SpawnNPC


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Eco Island Adventure")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = "intro"

        self.intro = Intro(self.screen)

        self.world = World()
        spawn_x, spawn_y = self.world.get_spawn_position()
        self.player = Player(spawn_x, spawn_y)

        self.pollution = PollutionSystem()

        npc_x = spawn_x + 70
        npc_y = spawn_y - 8
        self.spawn_npc = SpawnNPC(npc_x, npc_y)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "intro":
                self.intro.handle_event(event)
                if self.intro.finished:
                    self.state = "world"

            elif self.state == "world":
                pass

    def update(self, dt):
        if self.state == "intro":
            self.intro.update()

        elif self.state == "world":
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.world, dt)
            self.pollution.update(dt)
            self.spawn_npc.update(self.player)

    def draw(self):
        if self.state == "intro":
            self.intro.draw()

        elif self.state == "world":
            camera_x = self.player.rect.centerx - WIDTH // 2
            camera_y = self.player.rect.centery - HEIGHT // 2

            max_camera_x = max(0, self.world.pixel_width - WIDTH)
            max_camera_y = max(0, self.world.pixel_height - HEIGHT)

            camera_x = max(0, min(camera_x, max_camera_x))
            camera_y = max(0, min(camera_y, max_camera_y))

            self.world.draw(self.screen, camera_x, camera_y)
            self.spawn_npc.draw(self.screen, camera_x, camera_y)
            self.player.draw(self.screen, camera_x, camera_y)
            self.pollution.draw(self.screen)
            self.spawn_npc.draw_dialog(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()