# ─── MiniGameLakeCleanup ──────────────────────────────────────────────────────
#
#  Associé au PNJ "seal" (mission_key: "lake_cleanup", pollution_reward: 10)
#
#  Mécanique : le joueur vise avec HAUT/BAS (angle) et DROITE/GAUCHE (puissance),
#  puis appuie sur ESPACE pour lancer un déchet vers la bonne poubelle.
#  3 types de déchets : "papier", "verre", "plastique".
#  Objectif : atteindre SCORE_TO_WIN bonnes poubelles avant la fin du timer.
#
# ─────────────────────────────────────────────────────────────────────────────
import pygame
import math
import random
from constants import *
from minigame_reforestation import build_terrain, build_decorations, draw_terrain, draw_decorations
from world.decorations import draw_snow_pine, draw_rock_snow, draw_snow_crack, draw_ice_crack_big
import pygame
import math
import random

SCORE_TO_WIN  = 5      # nombre de bons tirs pour réussir
THROW_TIMER   = 45.0   # secondes
GRAVITY       = 280.0  # px / s²  (espace-écran, positif vers le bas)
PLAYER_SPEED  = 160    # repris de la mzap

TRASH_KINDS   = ["papier", "verre", "plastique"]

# Positions des trois poubelles (x, y du coin supérieur-gauche)
BIN_POSITIONS = {
    "plastique": (WIDTH - 340, HEIGHT - 130),
    "papier":    (WIDTH - 220, HEIGHT - 130),
    "verre":     (WIDTH - 100, HEIGHT - 130),
}
BIN_SIZE = (72, 96)


# ── Palettes pixel-art ────────────────────────────────────────────────────────

_BIN_PALETTES = {
    "papier": {
        "main":  (45,  110, 220),
        "shade": (25,   75, 170),
        "light": (95,  150, 240),
        "icon":  (255, 255, 255),
    },
    "verre": {
        "main":  (55,  170,  85),
        "shade": (28,  115,  55),
        "light": (90,  205, 120),
        "icon":  (220, 255, 220),
    },
    "plastique": {
        "main":  (240, 205,  50),
        "shade": (185, 150,  25),
        "light": (255, 230, 110),
        "icon":  (60,   70,  90),
    },
}

_TRASH_SPRITES = {
    "papier":    [(255, 255, 255, 4, 4, 12, 12),
                  (220, 220, 235, 6,  2, 10, 12),
                  (180, 180, 200, 7,  8,  6,  2)],
    "verre":     [(190, 255, 190, 8, 2, 4, 4),
                  ( 70, 200,  90, 6, 6, 8, 10),
                  ( 45, 150,  70, 7, 12, 6, 4)],
    "plastique": [( 90, 120, 255, 8, 2, 4, 3),
                  (255, 255, 170, 6, 5, 8, 9),
                  (235, 235, 120, 7, 14, 6, 3)],
}


# ── Helpers de dessin pixel-art ───────────────────────────────────────────────

def _draw_bin(surface, kind, rect):
    """Dessine une poubelle pixel-art sur `surface` à la position `rect`."""
    c = _BIN_PALETTES[kind]
    x, y = rect.x, rect.y

    # Couvercle
    pygame.draw.rect(surface, c["shade"], (x + 6,  y + 8,  60, 12))
    pygame.draw.rect(surface, c["light"], (x + 10, y + 4,  52,  6))
    # Corps
    pygame.draw.rect(surface, c["main"],  (x + 10, y + 18, 52, 62))
    pygame.draw.rect(surface, c["light"], (x + 14, y + 22,  8, 50))
    pygame.draw.rect(surface, c["shade"], (x + 54, y + 18,  8, 62))
    # Roues
    pygame.draw.rect(surface, (40, 40, 40), (x + 14, y + 80, 10, 10))
    pygame.draw.rect(surface, (40, 40, 40), (x + 48, y + 80, 10, 10))

    # Icône selon le type
    if kind == "papier":
        pygame.draw.rect(surface, c["icon"],     (x + 26, y + 34, 18, 22))
        pygame.draw.rect(surface, (220,235,255),  (x + 30, y + 30, 18, 22))
        pygame.draw.rect(surface, (180,205,250),  (x + 30, y + 38, 12,  2))
        pygame.draw.rect(surface, (180,205,250),  (x + 30, y + 44, 12,  2))
    elif kind == "verre":
        pygame.draw.rect(surface, c["icon"],     (x + 31, y + 29, 10,  8))
        pygame.draw.rect(surface, c["icon"],     (x + 28, y + 37, 16, 22))
        pygame.draw.rect(surface, (175,240,175),  (x + 32, y + 42,  8, 12))
    elif kind == "plastique":
        pygame.draw.rect(surface, c["icon"],     (x + 30, y + 28, 12,  8))
        pygame.draw.rect(surface, c["icon"],     (x + 28, y + 36, 16, 18))
        pygame.draw.rect(surface, c["icon"],     (x + 31, y + 54, 10, 10))
        pygame.draw.rect(surface, (95,105,130),   (x + 30, y + 42, 12,  3))


def _make_trash_surf(kind):
    """Retourne une Surface 20×20 représentant un déchet pixel-art."""
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    for r, g, b, rx, ry, rw, rh in _TRASH_SPRITES[kind]:
        pygame.draw.rect(surf, (r, g, b), (rx, ry, rw, rh))
    return surf


def _make_label_surf(kind, font):
    """Retourne une Surface avec le nom du déchet en couleur."""
    colors = {"papier": (130, 170, 255), "verre": (100, 220, 130), "plastique": (240, 210, 60)}
    return font.render(kind.upper(), True, colors[kind])


# ─── Classe principale ────────────────────────────────────────────────────────

class MiniGameLakeCleanup:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        self.font       = pygame.font.SysFont("consolas", 22, bold=True)
        self.big_font   = pygame.font.SysFont("consolas", 38, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)

        self.area = pygame.Rect(60, 60, WIDTH - 120, HEIGHT - 100)

        # Poubelles
        self.bins = {
            kind: pygame.Rect(bx, by, BIN_SIZE[0], BIN_SIZE[1])
            for kind, (bx, by) in BIN_POSITIONS.items()
        }

        # Sprites des déchets
        self._trash_surfs = {k: _make_trash_surf(k) for k in TRASH_KINDS}

        # Décor (terrain + décorations héritées de la mzap)
        self.terrain_tiles = build_terrain(WIDTH, HEIGHT)
        self.decorations   = build_decorations(self.area, [])

        # État du mini-jeu
        self.timer    = THROW_TIMER
        self.score    = 0
        self.finished = False
        self.success  = False

        # État du lancer
        self.angle    = 45.0   # degrés
        self.power    = 10.0   # pixels/s (sera multiplié par 30 dans le lancer)
        self._launched = False
        self._trash_x  = 0.0
        self._trash_y  = 0.0
        self._vx       = 0.0
        self._vy       = 0.0
        self._current_trash = random.choice(TRASH_KINDS)

        # Position de départ du joueur (coin gauche de la zone)
        self._save_player_position()
        self.player.x = float(self.area.x + 40)
        self.player.y = float(self.area.y + self.area.height // 2)
        self.player.rect.x = int(self.player.x)
        self.player.rect.y = int(self.player.y)

        self._reset_throw()

    # ── Sauvegarde / restauration ─────────────────────────────────────────────

    def _save_player_position(self):
        self._saved = (
            self.player.x, self.player.y,
            self.player.rect.x, self.player.rect.y,
        )

    def restore_player_position(self):
        self.player.x, self.player.y, self.player.rect.x, self.player.rect.y = self._saved

    # ── Gestion du lancer ─────────────────────────────────────────────────────

    def _reset_throw(self):
        """Replace le déchet dans les mains du joueur."""
        self._launched   = False
        self._trash_x    = float(self.player.rect.right + 4)
        self._trash_y    = float(self.player.rect.centery)
        self._vx         = 0.0
        self._vy         = 0.0
        self._current_trash = random.choice(TRASH_KINDS)

    def _launch(self):
        if self._launched:
            return
        rad = math.radians(self.angle)
        spd = self.power * 30.0           # mise à l'échelle px/s
        self._vx = spd * math.cos(rad)
        self._vy = -spd * math.sin(rad)
        self._launched = True

    # ── Événements ────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.finished:
                if event.key == pygame.K_SPACE:
                    self._launch()
                if event.key == pygame.K_r and self._launched:
                    self._reset_throw()
            if event.key == pygame.K_RETURN and self.finished:
                self.restore_player_position()

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        if self.finished:
            return

        # Visée clavier (angle & puissance) quand pas encore lancé
        if not self._launched:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.angle = min(80.0, self.angle + 60.0 * dt)
            if keys[pygame.K_DOWN]:
                self.angle = max(10.0, self.angle - 60.0 * dt)
            if keys[pygame.K_RIGHT]:
                self.power = min(20.0, self.power + 8.0 * dt)
            if keys[pygame.K_LEFT]:
                self.power = max(5.0, self.power - 8.0 * dt)

        # Physique du projectile
        if self._launched:
            self._vy    += GRAVITY * dt
            self._trash_x += self._vx * dt
            self._trash_y += self._vy * dt
            self._check_collision()

            # Hors écran → reset
            if (self._trash_x > WIDTH + 40 or self._trash_y > HEIGHT + 40
                    or self._trash_x < -40):
                self._reset_throw()

        # Synchronise la position du déchet sur le joueur quand il n'est pas lancé
        if not self._launched:
            self._trash_x = float(self.player.rect.right + 4)
            self._trash_y = float(self.player.rect.centery)

        # Timer
        self.timer -= dt
        if self.timer <= 0.0:
            self.timer    = 0.0
            self.finished = True
            self.success  = self.score >= SCORE_TO_WIN

        # Mise à jour animation du joueur (immobile pendant le jeu)
        self.player.is_moving = False
        self.player.anim_time      = 0.0
        self.player.walk_frame_time = 0.0

    def _check_collision(self):
        trash_rect = self._trash_surfs[self._current_trash].get_rect(
            center=(int(self._trash_x), int(self._trash_y))
        )
        for kind, bin_rect in self.bins.items():
            if trash_rect.colliderect(bin_rect):
                if kind == self._current_trash:
                    self.score += 1
                    if self.score >= SCORE_TO_WIN:
                        self.finished = True
                        self.success  = True
                self._reset_throw()
                return

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        draw_terrain(self.screen, self.terrain_tiles)
        self._draw_area_border()
        draw_decorations(self.screen, self.decorations)

        # Joueur
        self.player.draw(self.screen, 0, 0)

        # Poubelles (triées par Y pour la profondeur)
        bins_sorted = sorted(self.bins.items(), key=lambda kv: kv[1].bottom)
        for kind, rect in bins_sorted:
            _draw_bin(self.screen, kind, rect)

        # Trajectoire de visée (pointillés)
        if not self._launched:
            self._draw_aim_trajectory()

        # Déchet en vol (ou dans les mains)
        surf = self._trash_surfs[self._current_trash]
        pos  = surf.get_rect(center=(int(self._trash_x), int(self._trash_y)))
        self.screen.blit(surf, pos.topleft)

        # HUD & hint
        self._draw_hud()
        self._draw_hint()

        if self.finished:
            self._draw_end_overlay()

    def _draw_area_border(self):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(surf, (160, 220, 255, 55),
                         self.area, width=2, border_radius=14)
        self.screen.blit(surf, (0, 0))

    def _draw_aim_trajectory(self):
        rad = math.radians(self.angle)
        spd = self.power * 30.0
        vx0 = spd * math.cos(rad)
        vy0 = -spd * math.sin(rad)
        dt_step = 0.04
        for i in range(1, 9):
            t  = i * dt_step
            px = self._trash_x + vx0 * t
            py = self._trash_y + vy0 * t + 0.5 * GRAVITY * t * t
            pygame.draw.rect(self.screen, (80, 80, 80), (int(px), int(py), 4, 4))

    def _draw_hud(self):
        panel = pygame.Rect(20, 14, WIDTH - 40, 44)
        panel_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        panel_surf.fill((20, 30, 50, 190))
        self.screen.blit(panel_surf, (panel.x, panel.y))
        pygame.draw.rect(self.screen, (160, 210, 255), panel, width=1, border_radius=10)

        score_text = self.font.render(
            f"Score : {self.score} / {SCORE_TO_WIN}", True, (220, 240, 255)
        )
        timer_color = (255, 130, 80) if self.timer < 10 else (220, 240, 255)
        time_text = self.font.render(f"Temps : {int(self.timer)}s", True, timer_color)

        self.screen.blit(score_text, (panel.x + 18, panel.y + 11))
        self.screen.blit(time_text,  (panel.right - time_text.get_width() - 18, panel.y + 11))

        # Infos de visée (angle & puissance) en haut au centre
        aim_text = self.small_font.render(
            f"Angle : {int(self.angle)}°   Puiss. : {self.power:.1f}",
            True, (200, 225, 255)
        )
        self.screen.blit(aim_text,
                         (WIDTH // 2 - aim_text.get_width() // 2, panel.y + 14))

        # Déchet courant
        trash_label = _make_label_surf(self._current_trash, self.small_font)
        self.screen.blit(trash_label, (panel.x + 18, panel.bottom + 8))

    def _draw_hint(self):
        hint = self.small_font.render(
            "HAUT/BAS = angle   DROITE/GAUCHE = puissance   ESPACE = lancer   R = reset",
            True, (200, 225, 255)
        )
        hint_x = WIDTH // 2 - hint.get_width() // 2
        hint_y = HEIGHT - 30
        bg = pygame.Surface((hint.get_width() + 24, hint.get_height() + 8), pygame.SRCALPHA)
        bg.fill((20, 30, 50, 160))
        self.screen.blit(bg,   (hint_x - 12, hint_y - 4))
        self.screen.blit(hint, (hint_x, hint_y))

    def _draw_end_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 95, 440, 190)
        box_surf = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        box_surf.fill((18, 28, 48, 245))
        self.screen.blit(box_surf, (box.x, box.y))
        pygame.draw.rect(self.screen, (140, 200, 255), box, width=2, border_radius=16)

        if self.success:
            title_str = "Lac nettoye !"
            sub_str   = "Le phoque peut nager en paix."
            title_col = (180, 240, 255)
        else:
            title_str = "Temps ecoule..."
            sub_str   = f"Tu as trie {self.score} dechet(s) sur {SCORE_TO_WIN}."
            title_col = (255, 180, 100)

        title = self.big_font.render(title_str, True, title_col)
        sub   = self.font.render(sub_str, True, (190, 220, 245))
        info  = self.small_font.render("Appuie sur ENTREE pour revenir", True, (130, 170, 210))

        self.screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 24))
        self.screen.blit(sub,   (box.centerx - sub.get_width()   // 2, box.y + 90))
        self.screen.blit(info,  (box.centerx - info.get_width()  // 2, box.y + 150))
