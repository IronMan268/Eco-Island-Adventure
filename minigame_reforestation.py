import pygame
import math
import random
from constants import *
from world.decorations import draw_snow_pine, draw_rock_snow, draw_snow_crack, draw_ice_crack_big


# ─── Terrain ──────────────────────────────────────────────────────────────────

SNOW_COLORS = [
    (224, 236, 248),
    (218, 231, 244),
    (228, 239, 250),
    (215, 228, 242),
]
TILE_SIZE_MG = 32   # taille des tuiles dans le mini jeu


def build_terrain(width, height, seed=42):
    """Génère une grille de tuiles neige avec variation subtile de teinte."""
    tiles = []
    for ty in range(0, height + TILE_SIZE_MG, TILE_SIZE_MG):
        for tx in range(0, width + TILE_SIZE_MG, TILE_SIZE_MG):
            v = math.sin(tx * 0.08 + ty * 0.13) * 0.5 + 0.5
            idx = int(v * len(SNOW_COLORS)) % len(SNOW_COLORS)
            tiles.append((tx, ty, SNOW_COLORS[idx]))
    return tiles


def build_decorations(area, spot_positions, seed=12):
    """Place des décos (pins, rochers, fissures) en évitant les spots et le bord."""
    rng = random.Random(seed)
    decos = []
    TILE = TILE_SIZE_MG

    cols = area.width  // TILE
    rows = area.height // TILE

    for row in range(rows):
        for col in range(cols):
            tx = area.x + col * TILE
            ty = area.y + row * TILE
            cx = tx + TILE // 2
            cy = ty + TILE // 2

            # Ne pas placer sur les spots ni trop près du bord
            too_close = any(math.hypot(cx - sx, cy - sy) < 48 for sx, sy in spot_positions)
            near_edge = col == 0 or row == 0 or col == cols - 1 or row == rows - 1
            if too_close or near_edge:
                continue

            r = rng.random()
            if r < 0.10:
                decos.append(("snow_pine", tx - 4, ty - 10, rng.randint(0, 1)))
            elif r < 0.18:
                decos.append(("rock_snow", tx + rng.randint(2, 8), ty + rng.randint(6, 10), rng.randint(0, 1)))
            elif r < 0.23:
                decos.append(("snow_crack", tx, ty, rng.randint(0, 2)))
            elif r < 0.26:
                decos.append(("ice_crack_big", tx, ty, rng.randint(0, 2)))

    return decos


def draw_terrain(screen, tiles):
    for tx, ty, color in tiles:
        pygame.draw.rect(screen, color, (tx, ty, TILE_SIZE_MG + 1, TILE_SIZE_MG + 1))


def draw_decorations(screen, decos):
    for deco in decos:
        kind = deco[0]
        x, y, variant_or_size = deco[1], deco[2], deco[3]
        if kind == "snow_pine":
            draw_snow_pine(screen, x, y, variant_or_size)
        elif kind == "rock_snow":
            draw_rock_snow(screen, x, y, variant_or_size)
        elif kind == "snow_crack":
            draw_snow_crack(screen, x, y, variant_or_size)
        elif kind == "ice_crack_big":
            draw_ice_crack_big(screen, x, y, variant_or_size)


# ─── PlantSpot ────────────────────────────────────────────────────────────────

class PlantSpot:
    RADIUS = 26

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.planted = False
        self.grow_anim = 0.0   # 0..1 animation d'apparition du pin
        self.pulse = 0.0       # anneau vert quand le joueur est proche

    def is_near(self, px, py, margin=22):
        return math.hypot(px - self.x, py - self.y) < self.RADIUS + margin

    def update(self, dt, player_near):
        if self.planted:
            self.grow_anim = min(1.0, self.grow_anim + dt * 2.0)
        if player_near and not self.planted:
            self.pulse = (self.pulse + dt * 3.5) % (math.pi * 2)
        else:
            self.pulse = 0.0

    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        if self.planted:
            self._draw_planted(screen, x, y)
        else:
            self._draw_empty(screen, x, y)

    def _draw_empty(self, screen, x, y):
        r = self.RADIUS
        # Sol creusé (ellipse brune)
        pygame.draw.ellipse(screen, (148, 110, 72),
                            (x - r, y - int(r * 0.55), r * 2, int(r * 1.1)))
        pygame.draw.ellipse(screen, (172, 134, 92),
                            (x - r + 5, y - int(r * 0.45) + 2, r * 2 - 10, int(r * 0.9) - 4))
        # Croix de plantation
        pygame.draw.line(screen, (200, 240, 160), (x - 8, y), (x + 8, y), 2)
        pygame.draw.line(screen, (200, 240, 160), (x, y - 8), (x, y + 8), 2)
        # Anneau de pulsation proximité
        if self.pulse > 0:
            alpha = int((math.sin(self.pulse) * 0.5 + 0.5) * 130)
            surf = pygame.Surface((r * 2 + 24, r * 2 + 24), pygame.SRCALPHA)
            pygame.draw.circle(surf, (160, 230, 100, alpha), (r + 12, r + 12), r + 10, 2)
            screen.blit(surf, (x - r - 12, y - r - 12))

    def _draw_planted(self, screen, x, y):
        """Utilise draw_snow_pine du jeu avec animation d'échelle."""
        s = _ease_out(self.grow_anim)
        size = 1   # pin taille 1 (identique aux décos du monde)

        # On dessine dans une Surface temporaire puis on scale
        tmp = pygame.Surface((40, 48), pygame.SRCALPHA)
        draw_snow_pine(tmp, 2, 4, size)

        tw = max(1, int(tmp.get_width()  * s))
        th = max(1, int(tmp.get_height() * s))
        scaled = pygame.transform.scale(tmp, (tw, th))

        screen.blit(scaled, (x - tw // 2, y - th + 8))


def _ease_out(t):
    return 1 - (1 - t) ** 3


# ─── MiniGameReforestation ────────────────────────────────────────────────────

SPOT_POSITIONS = [
    (190, 190),
    (360, 150),
    (530, 200),
    (270, 330),
    (470, 340),
]


class MiniGameReforestation:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        self.font       = pygame.font.SysFont("consolas", 22, bold=True)
        self.big_font   = pygame.font.SysFont("consolas", 38, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)

        self.area = pygame.Rect(60, 60, WIDTH - 120, HEIGHT - 100)

        self.spots = [PlantSpot(x, y) for x, y in SPOT_POSITIONS]

        self.terrain_tiles = build_terrain(WIDTH, HEIGHT)
        self.decorations   = build_decorations(self.area, SPOT_POSITIONS)

        self.timer    = 30.0
        self.finished = False
        self.success  = False

        self._save_player_position()
        self.player.x = float(self.area.x + 40)
        self.player.y = float(self.area.y + 40)
        self.player.rect.x = int(self.player.x)
        self.player.rect.y = int(self.player.y)

    # ── Position ──────────────────────────────────────────────────────────────

    def _save_player_position(self):
        self._saved = (
            self.player.x, self.player.y,
            self.player.rect.x, self.player.rect.y,
        )

    def restore_player_position(self):
        self.player.x, self.player.y, self.player.rect.x, self.player.rect.y = self._saved

    # ── Événements ────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and not self.finished:
                self._try_plant()
            if event.key == pygame.K_RETURN and self.finished:
                self.restore_player_position()

    def _try_plant(self):
        for spot in self.spots:
            if not spot.planted and spot.is_near(self.player.x, self.player.y):
                spot.planted = True
                break
        if self._count_planted() == len(self.spots):
            self.finished = True
            self.success = True

    def _count_planted(self):
        return sum(1 for s in self.spots if s.planted)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        if self.finished:
            return

        keys = pygame.key.get_pressed()
        self._update_player(keys, dt)

        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0.0
            self.finished = True
            self.success = (self._count_planted() == len(self.spots))

        for spot in self.spots:
            spot.update(dt, spot.is_near(self.player.x, self.player.y))

    def _update_player(self, keys, dt):
        move_x = 0.0
        move_y = 0.0

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            move_x = -PLAYER_SPEED
            self.player.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = PLAYER_SPEED
            self.player.direction = "right"

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            move_y = -PLAYER_SPEED
            self.player.direction = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = PLAYER_SPEED
            self.player.direction = "down"

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        self.player.is_moving = (move_x != 0 or move_y != 0)
        if self.player.is_moving:
            self.player.anim_time      += dt * 10
            self.player.walk_frame_time += dt * 8
        else:
            self.player.anim_time      = 0.0
            self.player.walk_frame_time = 0.0

        if move_x != 0:
            new_x = self.player.x + move_x * dt
            new_rect = self.player.rect.copy()
            new_rect.x = int(new_x)
            if self.area.contains(new_rect):
                self.player.x = new_x
                self.player.rect.x = int(self.player.x)

        if move_y != 0:
            new_y = self.player.y + move_y * dt
            new_rect = self.player.rect.copy()
            new_rect.y = int(new_y)
            if self.area.contains(new_rect):
                self.player.y = new_y
                self.player.rect.y = int(self.player.y)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        # Fond neige
        draw_terrain(self.screen, self.terrain_tiles)

        # Bordure de zone
        self._draw_area_border()

        # Décorations du monde (pins, rochers, fissures) — derrière tout
        draw_decorations(self.screen, self.decorations)

        # Tri par Y : spots plantés + joueur pour la profondeur
        drawables = []
        for spot in self.spots:
            drawables.append((spot.y, "spot", spot))
        drawables.append((self.player.rect.bottom, "player", None))
        drawables.sort(key=lambda item: item[0])

        for _, kind, obj in drawables:
            if kind == "spot":
                obj.draw(self.screen)
            else:
                # Vrai pingouin du jeu — camera à (0,0) car on est en coordonnées écran
                self.player.draw(self.screen, 0, 0)

        # Emplacements vides toujours visibles (dessinés après pour le anneau de pulse)
        for spot in self.spots:
            if not spot.planted:
                spot.draw(self.screen)

        self._draw_hud()
        self._draw_hint()

        if self.finished:
            self._draw_end_overlay()

    def _draw_area_border(self):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(surf, (160, 220, 255, 55),
                         self.area, width=2, border_radius=14)
        self.screen.blit(surf, (0, 0))

    def _draw_hud(self):
        panel = pygame.Rect(20, 14, WIDTH - 40, 44)
        panel_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        panel_surf.fill((20, 30, 50, 190))
        self.screen.blit(panel_surf, (panel.x, panel.y))
        pygame.draw.rect(self.screen, (160, 210, 255), panel, width=1, border_radius=10)

        count_text = self.font.render(
            f"Arbres : {self._count_planted()} / {len(self.spots)}", True, (220, 240, 255)
        )
        timer_color = (255, 130, 80) if self.timer < 10 else (220, 240, 255)
        time_text = self.font.render(f"Temps : {int(self.timer)}s", True, timer_color)

        self.screen.blit(count_text, (panel.x + 18, panel.y + 11))
        self.screen.blit(time_text, (panel.right - time_text.get_width() - 18, panel.y + 11))

    def _draw_hint(self):
        hint = self.small_font.render(
            "Approche un emplacement  ->  appuie sur E pour planter",
            True, (200, 225, 255)
        )
        hint_x = WIDTH // 2 - hint.get_width() // 2
        hint_y = HEIGHT - 30
        bg = pygame.Surface((hint.get_width() + 24, hint.get_height() + 8), pygame.SRCALPHA)
        bg.fill((20, 30, 50, 160))
        self.screen.blit(bg, (hint_x - 12, hint_y - 4))
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
            title_str = "Mission reussie !"
            sub_str   = "L'ile respire mieux grace a toi."
            title_col = (180, 240, 255)
        else:
            n = self._count_planted()
            title_str = "Temps ecoule..."
            sub_str   = f"Tu as plante {n} arbre(s) sur {len(self.spots)}."
            title_col = (255, 180, 100)

        title = self.big_font.render(title_str, True, title_col)
        sub   = self.font.render(sub_str, True, (190, 220, 245))
        info  = self.small_font.render("Appuie sur ENTREE pour revenir", True, (130, 170, 210))

        self.screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 24))
        self.screen.blit(sub,   (box.centerx - sub.get_width()   // 2, box.y + 90))
        self.screen.blit(info,  (box.centerx - info.get_width()  // 2, box.y + 150))