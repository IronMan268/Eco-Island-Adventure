import pygame
from constants import *
from intro import Intro
from world import World
from player import Player
from pollution import PollutionSystem
from npc import MissionNPC
from npc_data import NPCS_DATA, npc_tile_to_pixel
from end_screen import EndScreen
from mini_game_lake_cleanup import MiniGameLakeCleanup
from minigame_reforestation import MiniGameReforestation


class MiniJeuTemporaire:
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

        self.font_title = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 17, bold=True)
        self.font_sign_title = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_sign_text = pygame.font.SysFont("consolas", 19, bold=False)
        self.font_sign_hint = pygame.font.SysFont("consolas", 15, bold=True)

        self.panneau_ouvert = False

    def create_npcs(self):
        npcs = []

        for data in NPCS_DATA:
            px, py = npc_tile_to_pixel(data["tile_x"], data["tile_y"])

            config = dict(data)
            config["x"] = px
            config["y"] = py

            npcs.append(MissionNPC(config))

        return npcs

    def restart_game(self):
        self.__init__()

    def lancer_mission_npc(self, npc):
        if npc.mission_done:
            return

        self.current_npc = npc
        self.minigame = self.create_minigame(npc.mission_key)
        self.state = "minigame"

    def create_minigame(self, mission_key):
        if mission_key == "reforestation":
            return MiniGameReforestation(self.screen, self.player)

        if mission_key == "lake_cleanup":
            return MiniGameLakeCleanup(self.screen, self.player)

        return MiniJeuTemporaire(self.screen, self.player, mission_key)

    def verifier_victoire(self):
        if self.pollution.value <= 0:
            self.pollution.set_pollution(0)
            self.state = "victory"
            return True

        return False

    def finir_minijeu(self):
        if self.current_npc and self.minigame and self.minigame.success:
            self.pollution.remove_pollution(self.current_npc.pollution_reward)
            self.current_npc.set_mission_done(True)

        if self.minigame:
            self.minigame.restore_player_position()

        self.minigame = None
        self.current_npc = None

        if self.verifier_victoire():
            return

        self.state = "world"

    def joueur_proche_panneau(self):
        zone = self.world.get_sign_rect()
        return self.player.rect.colliderect(zone.inflate(30, 30))

    def position_devant_joueur(self):
        x = self.player.rect.centerx
        y = self.player.rect.centery
        distance = 22

        direction = getattr(self.player, "direction", "down")

        if direction == "up":
            y -= distance
        elif direction == "down":
            y += distance
        elif direction == "left":
            x -= distance
        elif direction == "right":
            x += distance

        return x, y

    def joueur_devant_eau(self):
        x, y = self.position_devant_joueur()
        return self.world.is_water_at_pixel(x, y)

    def draw_box_bottom(self, text):
        texte = self.font_small.render(text, True, WHITE)
        fond = pygame.Surface((texte.get_width() + 30, 36), pygame.SRCALPHA)
        fond.fill((0, 0, 0, 145))

        x = WIDTH // 2 - fond.get_width() // 2
        y = HEIGHT - 18 - fond.get_height()

        self.screen.blit(fond, (x, y))
        self.screen.blit(texte, (x + 15, y + 8))

    def draw_sign_help(self):
        if self.panneau_ouvert:
            return

        if self.joueur_proche_panneau():
            texte = self.font_small.render("Appuie sur E pour lire la pancarte", True, WHITE)

            fond = pygame.Surface((texte.get_width() + 34, 40), pygame.SRCALPHA)
            fond.fill((8, 14, 22, 165))

            x = WIDTH // 2 - fond.get_width() // 2
            y = HEIGHT - 62

            pygame.draw.rect(self.screen, (170, 210, 255), (x, y, fond.get_width(), fond.get_height()), 2, border_radius=10)
            self.screen.blit(fond, (x, y))
            self.screen.blit(texte, (x + 17, y + 10))

    def draw_sign_text(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        self.screen.blit(overlay, (0, 0))

        box_w = 760
        box_h = 250
        box_x = WIDTH // 2 - box_w // 2
        box_y = HEIGHT // 2 - box_h // 2 + 40

        ombre = pygame.Surface((box_w + 10, box_h + 10), pygame.SRCALPHA)
        ombre.fill((0, 0, 0, 70))
        self.screen.blit(ombre, (box_x + 6, box_y + 8))

        fond = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        fond.fill((12, 18, 28, 235))
        self.screen.blit(fond, (box_x, box_y))

        pygame.draw.rect(self.screen, (155, 205, 255), (box_x, box_y, box_w, box_h), 2, border_radius=16)
        pygame.draw.rect(self.screen, (55, 90, 125), (box_x + 8, box_y + 8, box_w - 16, box_h - 16), 1, border_radius=12)

        titre = self.font_sign_title.render("Mission de l'ile", True, (230, 245, 255))
        self.screen.blit(titre, (WIDTH // 2 - titre.get_width() // 2, box_y + 24))

        pygame.draw.line(
            self.screen,
            (110, 170, 220),
            (box_x + 80, box_y + 66),
            (box_x + box_w - 80, box_y + 66),
            2
        )

        lignes = [
            "Parle avec les habitants pour sauver l'ile.",
            "Chaque mission reussie fait baisser la pollution.",
            "Suis les chemins pour trouver tous les habitants.",
        ]

        y = box_y + 92
        for texte in lignes:
            rendu = self.font_sign_text.render(texte, True, (215, 228, 240))
            self.screen.blit(rendu, (WIDTH // 2 - rendu.get_width() // 2, y))
            y += 34

        hint = self.font_sign_hint.render("ESPACE ou ECHAP pour fermer", True, (160, 200, 235))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, box_y + box_h - 34))

    def draw_water_text(self):
        if self.joueur_devant_eau():
            self.draw_box_bottom("Impossible de nager pour l'instant")

    def gerer_intro_event(self, event):
        self.intro.handle_event(event)
        if self.intro.finished:
            self.state = "world"

    def gerer_world_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if self.joueur_proche_panneau():
                self.panneau_ouvert = not self.panneau_ouvert
                return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
            if self.panneau_ouvert:
                self.panneau_ouvert = False
                return

        if self.panneau_ouvert:
            return

        for npc in self.npcs:
            result = npc.handle_event(event)
            if result == "accept":
                self.lancer_mission_npc(npc)
                break

    def gerer_minigame_event(self, event):
        self.minigame.handle_event(event)

        if self.minigame.finished:
            self.finir_minijeu()

    def gerer_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart_game()
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif self.state == "intro":
                self.gerer_intro_event(event)

            elif self.state == "world":
                self.gerer_world_event(event)

            elif self.state == "minigame":
                self.gerer_minigame_event(event)

            elif self.state in ("victory", "game_over"):
                self.gerer_end_event(event)

    def update_intro(self):
        self.intro.update()

    def update_world(self, dt):
        keys = pygame.key.get_pressed()

        if not self.panneau_ouvert:
            self.player.update(keys, self.world, dt)

        self.pollution.update(dt)

        for npc in self.npcs:
            npc.update(self.player, dt)

        bear_npc = None
        for npc in self.npcs:
            if npc.id == "bear":
                bear_npc = npc
                break

        if bear_npc:
            self.world.update_bear_trees(bear_npc.mission_done)

        if self.verifier_victoire():
            return

        if self.pollution.value >= self.pollution.max_value:
            self.game_over_reason = "La pollution a atteint 100%"
            self.state = "game_over"

    def update_minigame(self, dt):
        self.minigame.update(dt)

    def update(self, dt):
        if self.state == "intro":
            self.update_intro()
        elif self.state == "world":
            self.update_world(dt)
        elif self.state == "minigame":
            self.update_minigame(dt)

    def get_camera(self):
        camera_x = self.player.rect.centerx - WIDTH // 2
        camera_y = self.player.rect.centery - HEIGHT // 2

        max_camera_x = max(0, self.world.pixel_width - WIDTH)
        max_camera_y = max(0, self.world.pixel_height - HEIGHT)

        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        return camera_x, camera_y

    def draw_world_scene(self):
        camera_x, camera_y = self.get_camera()

        self.world.draw(self.screen, camera_x, camera_y)

        for npc in sorted(self.npcs, key=lambda n: n.rect.y):
            npc.draw(self.screen, camera_x, camera_y)

        self.player.draw(self.screen, camera_x, camera_y)
        self.pollution.draw(self.screen)

        for npc in self.npcs:
            npc.draw_dialog(self.screen)

        self.draw_sign_help()
        self.draw_water_text()

        if self.panneau_ouvert:
            self.draw_sign_text()

    def draw(self):
        if self.state == "intro":
            self.intro.draw()

        elif self.state == "world":
            self.draw_world_scene()

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