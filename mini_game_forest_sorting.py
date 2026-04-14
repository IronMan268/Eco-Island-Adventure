import math
import random
import pygame


class MiniGameForestSorting:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        self.finished = False
        self.success = False

        self.saved_x = player.rect.x
        self.saved_y = player.rect.y

        self.LARGEUR = 1080
        self.HAUTEUR = 720

        # Couleurs
        self.BLANC = (255, 255, 255)
        self.NOIR = (20, 20, 30)
        self.VERT = (70, 190, 90)
        self.ROUGE = (225, 70, 70)
        self.BLEU = (85, 160, 255)
        self.JAUNE = (240, 210, 70)
        self.GRIS = (95, 95, 105)
        self.BORDURE = (70, 120, 170)

        # Polices
        self.font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 50)
        self.mid_font = pygame.font.SysFont("arial", 34)

        # Fond
        self.background = pygame.image.load("asets/la.png").convert()
        self.background = pygame.transform.scale(self.background, (self.LARGEUR, self.HAUTEUR))

        # Images
        self.img_bouteille = self.load_img("asets/456.png", 74)
        self.img_canette = self.load_img("asets/789.png", 74)
        self.img_sac = self.load_img("asets/1.png", 74)
        self.img_baril = self.load_img("asets/123.png", 80)

        # Déchets
        self.dechets_data = [
            {"type": "recyclage", "image": self.img_bouteille, "nom": "bouteille"},
            {"type": "recyclage", "image": self.img_canette, "nom": "canette"},
            {"type": "normal", "image": self.img_sac, "nom": "sac"},
            {"type": "toxique", "image": self.img_baril, "nom": "baril"},
        ]

        # Poubelles
        self.bin_width = 150
        self.bin_height = 125
        self.bin_y = self.HAUTEUR - 165

        self.bins = {
            "recyclage": pygame.Rect(150, self.bin_y, self.bin_width, self.bin_height),
            "normal": pygame.Rect(self.LARGEUR // 2 - self.bin_width // 2, self.bin_y, self.bin_width, self.bin_height),
            "toxique": pygame.Rect(self.LARGEUR - 150 - self.bin_width, self.bin_y, self.bin_width, self.bin_height),
        }

        self.BIN_COLORS = {
            "recyclage": self.BLEU,
            "normal": self.GRIS,
            "toxique": self.ROUGE,
        }

        self.bin_anim = {
            k: {"open": 0.0, "shake": 0.0, "shake_dir": 1}
            for k in self.bins
        }

        self.particles = []

        # Déchet actuel
        self.dechet_actuel = None
        self.dechet_x = float(self.LARGEUR // 2)
        self.dechet_y = 40.0
        self.dechet_vy = 3.8
        self.float_phase = 0.0

        self.arc_start_x = 0.0
        self.arc_start_y = 0.0
        self.arc_t = 0.0
        self.arc_duration = 60

        # Shake écran
        self.screen_shake_frames = 0
        self.screen_shake_intensity = 7

        # Score / temps
        self.score = 0
        self.bonnes_reponses = 0
        self.erreurs = 0
        self.objectif = 12
        self.temps_max = 35
        self.temps_restant = float(self.temps_max)
        self.game_over = False
        self.victoire = False

        self.feedback_timer = 0
        self.feedback_text = ""
        self.feedback_color = self.BLANC
        self.flash_timer = 0

        self.nouveau_dechet()

    def load_img(self, path, size=74):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (size, size))

    def restore_player_position(self):
        self.player.rect.x = self.saved_x
        self.player.rect.y = self.saved_y

    class Particle:
        def __init__(self, x, y, color):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 9)
            self.x = x
            self.y = y
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed - random.uniform(2, 5)
            self.color = color
            self.radius = random.randint(4, 9)
            self.life = random.randint(35, 60)
            self.max_life = self.life
            self.gravity = 0.3
            self.shape = random.randint(0, 2)
            self.angle = random.uniform(0, math.pi * 2)
            self.rot_speed = random.uniform(-0.2, 0.2)

        def update(self):
            self.vx *= 0.97
            self.vy += self.gravity
            self.x += self.vx
            self.y += self.vy
            self.life -= 1
            self.angle += self.rot_speed

        def draw(self, surface):
            alpha = int(255 * (self.life / self.max_life))
            r = max(1, int(self.radius * (self.life / self.max_life)))
            c = (*self.color, alpha)
            tmp = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)

            if self.shape == 0:
                pygame.draw.circle(tmp, c, (r * 2, r * 2), r)
            elif self.shape == 1:
                pygame.draw.rect(tmp, c, (r, r, r * 2, r * 2), border_radius=2)
            else:
                pts = []
                for i in range(5):
                    a_out = self.angle + i * (2 * math.pi / 5) - math.pi / 2
                    a_in = a_out + math.pi / 5
                    pts.append((r * 2 + math.cos(a_out) * r * 2, r * 2 + math.sin(a_out) * r * 2))
                    pts.append((r * 2 + math.cos(a_in) * r, r * 2 + math.sin(a_in) * r))
                pygame.draw.polygon(tmp, c, pts)

            surface.blit(tmp, (int(self.x) - r * 2, int(self.y) - r * 2))

    def spawn_particles(self, x, y, color, count=40):
        colors = [
            color,
            (
                min(color[0] + 60, 255),
                min(color[1] + 60, 255),
                min(color[2] + 60, 255)
            ),
            self.BLANC,
            self.JAUNE
        ]
        for _ in range(count):
            self.particles.append(self.Particle(x, y, random.choice(colors)))

    def nouveau_dechet(self):
        self.dechet_actuel = random.choice(self.dechets_data)
        self.float_phase = random.uniform(0, math.pi * 2)

        self.arc_start_x = -40.0 if random.random() < 0.5 else float(self.LARGEUR + 40)
        self.arc_start_y = random.uniform(60, 160)
        self.arc_t = 0.0

        self.dechet_x = self.arc_start_x
        self.dechet_y = self.arc_start_y
        self.dechet_vy = 0.0

    def reset_game(self):
        self.score = 0
        self.bonnes_reponses = 0
        self.erreurs = 0
        self.temps_restant = float(self.temps_max)
        self.game_over = False
        self.victoire = False
        self.feedback_timer = 0
        self.feedback_text = ""
        self.feedback_color = self.BLANC
        self.flash_timer = 0
        self.screen_shake_frames = 0
        self.particles = []

        for k in self.bin_anim:
            self.bin_anim[k] = {"open": 0.0, "shake": 0.0, "shake_dir": 1}

        self.nouveau_dechet()

    def get_item_color(self, item_type):
        return self.BIN_COLORS[item_type]

    def get_bin_hit(self, item_rect):
        test_point = (item_rect.centerx, item_rect.bottom - 4)
        for nom_bin, rect_bin in self.bins.items():
            if rect_bin.collidepoint(test_point):
                return nom_bin
        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if (self.game_over or self.victoire) and event.key == pygame.K_r:
                self.reset_game()

            elif (self.game_over or self.victoire) and event.key == pygame.K_RETURN:
                self.finished = True
                self.success = self.victoire

            elif event.key == pygame.K_ESCAPE:
                self.finished = True
                self.success = False

    def update(self, dt):
        if self.finished:
            return

        if not self.game_over and not self.victoire:
            self.temps_restant -= dt
            if self.temps_restant <= 0:
                self.temps_restant = 0
                self.game_over = True

            keys = pygame.key.get_pressed()

            if self.arc_t < 1.0:
                self.arc_t += 1.0 / self.arc_duration
                self.arc_t = min(self.arc_t, 1.0)

                t = self.arc_t
                p0x, p0y = self.arc_start_x, self.arc_start_y
                p1x, p1y = self.LARGEUR / 2, -60.0
                p2x, p2y = self.LARGEUR / 2 - 37, 60.0

                self.dechet_x = (1 - t) ** 2 * p0x + 2 * (1 - t) * t * p1x + t ** 2 * p2x
                self.dechet_y = (1 - t) ** 2 * p0y + 2 * (1 - t) * t * p1y + t ** 2 * p2y
                self.dechet_vy = 0.0

            else:
                if keys[pygame.K_LEFT]:
                    self.dechet_x -= 7
                if keys[pygame.K_RIGHT]:
                    self.dechet_x += 7

                self.dechet_x = max(0, min(self.dechet_x, self.LARGEUR - 74))

                self.dechet_vy += 0.18
                self.dechet_y += self.dechet_vy

                rect_dechet = pygame.Rect(int(self.dechet_x), int(self.dechet_y), 74, 74)

                if rect_dechet.bottom >= self.bin_y + 10:
                    poubelle_trouvee = self.get_bin_hit(rect_dechet)

                    if poubelle_trouvee == self.dechet_actuel["type"]:
                        self.score += 1
                        self.bonnes_reponses += 1
                        self.feedback_text = "Bien trie !"
                        self.feedback_color = self.VERT
                        self.flash_timer = 8

                        cx = self.bins[poubelle_trouvee].centerx
                        cy = self.bins[poubelle_trouvee].y
                        self.spawn_particles(cx, cy, self.BIN_COLORS[poubelle_trouvee], count=55)
                        self.bin_anim[poubelle_trouvee]["open"] = 1.0

                        self.feedback_timer = 45
                        self.nouveau_dechet()

                    elif poubelle_trouvee is not None:
                        self.erreurs += 1
                        self.feedback_text = "Mauvais tri !"
                        self.feedback_color = self.ROUGE
                        self.flash_timer = 8

                        self.bin_anim[poubelle_trouvee]["shake"] = 12.0
                        self.bin_anim[poubelle_trouvee]["shake_dir"] = 1

                        self.screen_shake_frames = 18
                        self.feedback_timer = 45
                        self.nouveau_dechet()

                    elif rect_dechet.bottom >= self.HAUTEUR - 20:
                        self.erreurs += 1
                        self.feedback_text = "Rate !"
                        self.feedback_color = self.ROUGE
                        self.flash_timer = 8
                        self.feedback_timer = 35
                        self.nouveau_dechet()

            if self.score >= self.objectif:
                self.victoire = True

        for k in self.bin_anim:
            a = self.bin_anim[k]
            if a["open"] > 0:
                a["open"] = max(0.0, a["open"] - 0.05)
            if a["shake"] > 0:
                a["shake"] = max(0.0, a["shake"] - 0.8)
                a["shake_dir"] = -a["shake_dir"]

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        if self.feedback_timer > 0:
            self.feedback_timer -= 1

        if self.screen_shake_frames > 0:
            self.screen_shake_frames -= 1

    def draw_bin(self, key, rect, color, label, emoji, surface):
        anim = self.bin_anim[key]
        shake = anim["shake"]
        ox = int(shake * anim["shake_dir"])

        x = rect.x + ox
        y = rect.y
        w = rect.w
        h = rect.h

        dark = (
            max(color[0] - 45, 0),
            max(color[1] - 45, 0),
            max(color[2] - 45, 0)
        )

        shadow = pygame.Surface((w + 30, h + 35), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 55), (10, h + 8, w, 18))
        surface.blit(shadow, (x - 10, y - 5))

        body_top_w = int(w * 0.82)
        body_x_top = x + (w - body_top_w) // 2
        body_y_top = y + 24
        body_y_bottom = y + h - 18

        body_points = [
            (body_x_top, body_y_top),
            (body_x_top + body_top_w, body_y_top),
            (x + w, body_y_bottom),
            (x, body_y_bottom)
        ]

        pygame.draw.polygon(surface, color, body_points)
        pygame.draw.polygon(surface, dark, body_points, 3)

        open_offset = int(anim["open"] * 18)
        lid_w = int(w * 0.92)
        lid_h = 18
        lid_x = x + (w - lid_w) // 2
        lid_y = y + 6 - open_offset

        pygame.draw.rect(surface, dark, (lid_x, lid_y, lid_w, lid_h), border_radius=8)
        pygame.draw.rect(surface, (35, 40, 50), (lid_x, lid_y, lid_w, lid_h), 2, border_radius=8)
        pygame.draw.rect(surface, (220, 220, 225), (x + w // 2 - 12, lid_y + 4, 24, 5), border_radius=3)

        wheel_y = y + h - 10
        pygame.draw.circle(surface, (40, 40, 45), (x + 28, wheel_y), 10)
        pygame.draw.circle(surface, (40, 40, 45), (x + w - 28, wheel_y), 10)

        txt_emoji = self.mid_font.render(emoji, True, self.BLANC)
        txt_label = self.small_font.render(label, True, self.BLANC)
        surface.blit(txt_emoji, (x + w // 2 - txt_emoji.get_width() // 2, y + 52))
        surface.blit(txt_label, (x + w // 2 - txt_label.get_width() // 2, y + 82))

    def draw_ui_panel(self, surface):
        pygame.draw.rect(surface, (120, 130, 150), (24, 24, 270, 180), border_radius=16)
        ui_panel = pygame.Surface((270, 180), pygame.SRCALPHA)
        ui_panel.fill((255, 255, 255, 225))
        surface.blit(ui_panel, (20, 20))
        pygame.draw.rect(surface, self.BORDURE, (20, 20, 270, 180), 3, border_radius=16)
        pygame.draw.line(surface, self.BLANC, (35, 35), (275, 35), 2)

        surface.blit(self.font.render(f"Score : {self.score}/{self.objectif}", True, self.NOIR), (38, 35))
        surface.blit(self.font.render(f"Bons tris : {self.bonnes_reponses}", True, self.NOIR), (38, 72))
        surface.blit(self.font.render(f"Erreurs : {self.erreurs}", True, self.NOIR), (38, 109))
        surface.blit(self.font.render(f"Temps : {int(self.temps_restant)}", True, self.NOIR), (38, 146))

    def draw_sorting_zone(self, surface):
        pygame.draw.rect(surface, (150, 160, 180), (116, 536, 860, 150), border_radius=26)
        pygame.draw.rect(surface, (235, 240, 248), (110, 530, 860, 150), border_radius=26)
        pygame.draw.rect(surface, (180, 190, 210), (110, 530, 860, 150), 3, border_radius=26)
        pygame.draw.rect(surface, (248, 250, 255), (130, 545, 820, 12), border_radius=12)

    def draw_current_item(self, surface):
        float_offset = math.sin(self.float_phase) * 4
        self.float_phase += 0.08

        item_color = self.get_item_color(self.dechet_actuel["type"])

        ombre = pygame.Surface((64, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(ombre, (0, 0, 0, 95), (0, 0, 64, 20))
        surface.blit(ombre, (int(self.dechet_x) + 6, int(self.dechet_y) + 66))

        bg_circle = pygame.Surface((92, 92), pygame.SRCALPHA)
        pygame.draw.circle(bg_circle, (*item_color, 200), (46, 46), 40)
        pygame.draw.circle(bg_circle, (255, 255, 255, 170), (46, 46), 40, 2)
        surface.blit(bg_circle, (int(self.dechet_x) - 9, int(self.dechet_y) - 8 + int(float_offset)))

        halo = pygame.Surface((104, 104), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 255, 255, 28), (52, 52), 44)
        surface.blit(halo, (int(self.dechet_x) - 15, int(self.dechet_y) - 14 + int(float_offset)))

        img = self.dechet_actuel["image"]
        img_rect = img.get_rect(center=(int(self.dechet_x) + 37, int(self.dechet_y) + 37 + int(float_offset)))
        surface.blit(img, img_rect)

    def draw_feedback(self, surface):
        if self.feedback_timer > 0:
            txt = self.big_font.render(self.feedback_text, True, self.feedback_color)
            x = self.LARGEUR // 2 - txt.get_width() // 2
            y = 120

            outline = self.big_font.render(self.feedback_text, True, self.BLANC)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                surface.blit(outline, (x + dx, y + dy))
            surface.blit(txt, (x, y))

    def draw_end_panel(self, surface):
        overlay = pygame.Surface((self.LARGEUR, self.HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(260, 185, 560, 250)
        pygame.draw.rect(surface, (245, 248, 250), panel, border_radius=20)
        pygame.draw.rect(surface, self.BORDURE, panel, 4, border_radius=20)

        titre = "MISSION REUSSIE !" if self.victoire else "MISSION ECHOUEE !"
        couleur_titre = self.VERT if self.victoire else self.ROUGE

        surface.blit(
            self.big_font.render(titre, True, couleur_titre),
            (panel.centerx - self.big_font.size(titre)[0] // 2, panel.y + 32)
        )

        for i, line in enumerate([
            f"Score final : {self.score}",
            f"Bons tris : {self.bonnes_reponses}",
            f"Erreurs : {self.erreurs}",
        ]):
            t = self.font.render(line, True, self.NOIR)
            surface.blit(t, (panel.centerx - t.get_width() // 2, panel.y + 102 + i * 36))

        hint = self.small_font.render("R = recommencer | ENTREE = quitter", True, self.NOIR)
        surface.blit(hint, (panel.centerx - hint.get_width() // 2, panel.y + 214))

    def draw(self):
        shake_ox, shake_oy = 0, 0
        if self.screen_shake_frames > 0:
            shake_ox = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_oy = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)

        # Canvas logique du mini-jeu
        canvas = pygame.Surface((self.LARGEUR, self.HAUTEUR))
        canvas.blit(self.background, (0, 0))

        self.draw_sorting_zone(canvas)
        self.draw_ui_panel(canvas)
        self.draw_bin("recyclage", self.bins["recyclage"], self.BLEU, "RECYCLAGE", "♻", canvas)
        self.draw_bin("normal", self.bins["normal"], self.GRIS, "NORMAL", "🗑", canvas)
        self.draw_bin("toxique", self.bins["toxique"], self.ROUGE, "TOXIQUE", "☣", canvas)

        if self.dechet_actuel is not None and not self.game_over and not self.victoire:
            self.draw_current_item(canvas)

        for p in self.particles:
            p.draw(canvas)

        self.draw_feedback(canvas)

        if self.victoire or self.game_over:
            self.draw_end_panel(canvas)

        if self.flash_timer > 0:
            flash = pygame.Surface((self.LARGEUR, self.HAUTEUR), pygame.SRCALPHA)
            if self.feedback_color == self.VERT:
                flash.fill((120, 255, 120, 55))
            else:
                flash.fill((255, 120, 120, 55))
            canvas.blit(flash, (0, 0))
            self.flash_timer -= 1

        # Affichage final sans déformation
        self.screen.fill(self.NOIR)

        screen_w, screen_h = self.screen.get_size()
        scale = min(screen_w / self.LARGEUR, screen_h / self.HAUTEUR)

        scaled_w = int(self.LARGEUR * scale)
        scaled_h = int(self.HAUTEUR * scale)

        scaled_canvas = pygame.transform.smoothscale(canvas, (scaled_w, scaled_h))

        x = (screen_w - scaled_w) // 2
        y = (screen_h - scaled_h) // 2

        self.screen.blit(scaled_canvas, (x + shake_ox, y + shake_oy))