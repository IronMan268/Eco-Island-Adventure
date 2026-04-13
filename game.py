import pygame
from constants import *
from intro import Intro
from world import World
from player import Player
from pollution import PollutionSystem
from npc import MissionNPC
from npc_data import NPCS_DATA, npc_tile_to_pixel
from end_screen import EndScreen


class PlaceholderMiniGame:
    def __init__(self, screen, player, mission_key):
        self.screen = screen
        self.player = player
        self.mission_key = mission_key
        self.finished = False
        self.success = False

        self.saved_x = player.rect.x
        self.saved_y = player.rect.y

        self.title_font = pygame.font.SysFont("consolas", 32, bold=True)
        self.text_font = pygame.font.SysFont("consolas", 20, bold=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.finished = True
                self.success = True
            elif event.key == pygame.K_ESCAPE:
                self.finished = True
                self.success = False

    def update(self, dt):
        pass

    def restore_player_position(self):
        self.player.rect.x = self.saved_x
        self.player.rect.y = self.saved_y

    def draw(self):
        self.screen.fill((12, 18, 30))
        title = self.title_font.render("MINI-JEU A AJOUTER", True, WHITE)
        line1 = self.text_font.render(f"Mission : {self.mission_key}", True, WHITE)
        line2 = self.text_font.render("ENTREE = mission reussie", True, WHITE)
        line3 = self.text_font.render("ECHAP = annuler", True, WHITE)

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
        self.screen.blit(line1, (WIDTH // 2 - line1.get_width() // 2, 250))
        self.screen.blit(line2, (WIDTH // 2 - line2.get_width() // 2, 300))
        self.screen.blit(line3, (WIDTH // 2 - line3.get_width() // 2, 335))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Eco Island Adventure")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = "intro"

        self.intro = Intro(self.screen)

        self.victory_screen = EndScreen("assets/victoire.png")
        self.lose_screen = EndScreen("assets/lose.png")

        self.world = World()
        spawn_x, spawn_y = self.world.get_spawn_position()
        self.player = Player(spawn_x, spawn_y)

        self.pollution = PollutionSystem()

        self.npcs = self.create_npcs()

        self.minigame = None
        self.current_npc = None
        self.game_over_reason = ""

    def create_npcs(self):
        npcs = []

        for data in NPCS_DATA:
            px, py = npc_tile_to_pixel(data["tile_x"], data["tile_y"])

            npc_config = dict(data)
            npc_config["x"] = px
            npc_config["y"] = py

            npcs.append(MissionNPC(npc_config))

        return npcs

    def restart_game(self):
        self.__init__()

    def start_npc_mission(self, npc):
        if npc.mission_done:
            return

        self.current_npc = npc
        self.minigame = self.build_minigame_for(npc.mission_key)
        self.state = "minigame"

    def build_minigame_for(self, mission_key):
        return PlaceholderMiniGame(self.screen, self.player, mission_key)

    def check_victory(self):
        if self.pollution.value <= 0:
            self.pollution.set_pollution(0)
            self.state = "victory"
            return True
        return False

    def finish_current_minigame(self):
        if self.current_npc and self.minigame and self.minigame.success:
            self.pollution.remove_pollution(self.current_npc.pollution_reward)
            self.current_npc.set_mission_done(True)

        if self.minigame:
            self.minigame.restore_player_position()

        self.minigame = None
        self.current_npc = None

        if self.check_victory():
            return

        self.state = "world"

    def all_npcs_done(self):
        return all(npc.mission_done for npc in self.npcs)

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
                for npc in self.npcs:
                    result = npc.handle_event(event)
                    if result == "accept":
                        self.start_npc_mission(npc)
                        break

            elif self.state == "minigame":
                self.minigame.handle_event(event)

                if self.minigame.finished:
                    self.finish_current_minigame()

            elif self.state == "victory":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

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

            for npc in self.npcs:
                npc.update(self.player, dt)

            if self.check_victory():
                return

            if self.pollution.value >= self.pollution.max_value:
                self.set_game_over("La pollution a atteint 100%")

        elif self.state == "minigame":
            self.minigame.update(dt)

        elif self.state in ("victory", "game_over"):
            pass

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

            for npc in sorted(self.npcs, key=lambda n: n.rect.y):
                npc.draw(self.screen, camera_x, camera_y)

            self.player.draw(self.screen, camera_x, camera_y)
            self.pollution.draw(self.screen)

            for npc in self.npcs:
                npc.draw_dialog(self.screen)

        elif self.state == "minigame":
            self.minigame.draw()

        elif self.state == "victory":
            self.victory_screen.draw(self.screen)

        elif self.state == "game_over":
            self.lose_screen.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()