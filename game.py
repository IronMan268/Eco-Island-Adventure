import pygame
from constants import *
from intro import Intro
from world import World
from player import Player
from pollution import PollutionSystem
from npc import PollutionNPC
from minigame_reforestation import MiniGameReforestation


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

        # Ours place dans une zone plus vide de l'ile
        bear_tile_x = 42
        bear_tile_y = 92

        npc_x = bear_tile_x * TILE_SIZE + 4
        npc_y = bear_tile_y * TILE_SIZE - 8

        self.pollution_npc = PollutionNPC(npc_x, npc_y)

        self.minigame = None
        self.game_over_reason = ""

    def restart_game(self):
        self.__init__()

    def start_reforestation_minigame(self):
        if self.pollution_npc.mission_done:
            return

        self.minigame = MiniGameReforestation(self.screen, self.player)
        self.state = "minigame"

    def finish_reforestation_minigame(self):
        if self.minigame.success:
            self.pollution.remove_pollution(20)
            self.pollution_npc.set_mission_done(True)

        self.minigame.restore_player_position()
        self.minigame = None
        self.state = "world"

    def set_game_over(self, reason="La pollution a atteint 100%"):
        self.game_over_reason = reason
        self.state = "game_over"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "intro":
                self.intro.handle_event(event)
                if self.intro.finished:
                    self.state = "world"

            elif self.state == "world":
                result = self.pollution_npc.handle_event(event)
                if result == "accept":
                    self.start_reforestation_minigame()

            elif self.state == "minigame":
                self.minigame.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.minigame.finished:
                        self.finish_reforestation_minigame()

            elif self.state == "game_over":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def update(self, dt):
        if self.state == "intro":
            self.intro.update()

        elif self.state == "world":
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.world, dt)
            self.pollution.update(dt)
            self.pollution_npc.update(self.player, dt)

            if self.pollution.value >= self.pollution.max_value:
                self.set_game_over("La pollution a atteint 100%.")

        elif self.state == "minigame":
            self.minigame.update(dt)

        elif self.state == "game_over":
            pass

    def draw_game_over(self):
        self.screen.fill((15, 10, 16))

        title_font = pygame.font.SysFont("consolas", 46, bold=True)
        text_font = pygame.font.SysFont("consolas", 22, bold=True)
        small_font = pygame.font.SysFont("consolas", 18, bold=True)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((120, 0, 0, 35))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(140, 160, WIDTH - 280, 250)
        pygame.draw.rect(self.screen, (35, 12, 18), box, border_radius=18)
        pygame.draw.rect(self.screen, (255, 140, 140), box, 3, border_radius=18)

        title = title_font.render("GAME OVER", True, WHITE)
        subtitle = text_font.render(self.game_over_reason, True, (255, 220, 220))
        info = small_font.render("Appuie sur R pour recommencer ou ESC pour quitter", True, WHITE)

        self.screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 45))
        self.screen.blit(subtitle, (box.centerx - subtitle.get_width() // 2, box.y + 120))
        self.screen.blit(info, (box.centerx - info.get_width() // 2, box.y + 185))

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
            self.pollution_npc.draw(self.screen, camera_x, camera_y)
            self.player.draw(self.screen, camera_x, camera_y)
            self.pollution.draw(self.screen)
            self.pollution_npc.draw_dialog(self.screen)

        elif self.state == "minigame":
            self.minigame.draw()

        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()