import os
import pygame
from constants import WIDTH, HEIGHT, WHITE

from world.decorations import draw_snow_pine



def trim_transparent(surface):
    mask = pygame.mask.from_surface(surface)
    rects = mask.get_bounding_rects()

    if not rects:
        return surface.copy()

    rect = rects[0]
    return surface.subsurface(rect).copy()


class PollutionNPC:
    def __init__(self, x, y, image_path="assets/npc_pollution.png"):
        self.x = int(x)
        self.y = int(y)

        self.rect = pygame.Rect(self.x, self.y, 34, 44)

        self.font = pygame.font.SysFont("consolas", 18, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)

        self.interaction_distance = 80
        self.show_prompt = False
        self.dialog_open = False

        self.name = "Ours protecteur"

        self.default_lines = [
            "Cette partie de l'ile est encore fragile...",
            "Veux-tu m'aider a replanter des pousses ?",
            "Si tu reussis, la pollution baissera de 20%."
        ]

        self.done_lines = [
            "Merci pour ton aide.",
            "Regarde, la nature revient deja.",
            "De nouveaux sapins ont pousse ici."
        ]

        self.current_lines = list(self.default_lines)

        self.image = None
        self.image_offset_y = 4

        if os.path.exists(image_path):
            try:
                loaded = pygame.image.load(image_path).convert_alpha()
                trimmed = trim_transparent(loaded)

                target_height = 56
                img_w, img_h = trimmed.get_size()

                scale = target_height / img_h
                new_w = max(1, int(img_w * scale))
                new_h = max(1, int(img_h * scale))

                self.image = pygame.transform.scale(trimmed, (new_w, new_h))
            except Exception:
                self.image = None

        self.typewriter_speed = 42.0
        self.visible_chars = 0.0

        self.mission_done = False

        # arbres de recompense
        # coordonnees plus eloignees de l'ours pour eviter la superposition
        # dx/dy en pixels dans le monde
        self.reward_trees = [
            {"dx": -90, "dy": 6, "size": 0},
            {"dx": -58, "dy": 34, "size": 1},
            {"dx": 62, "dy": 10, "size": 0},
            {"dx": 96, "dy": 36, "size": 1},
        ]

    def set_mission_done(self, value=True):
        self.mission_done = value
        if self.mission_done:
            self.current_lines = list(self.done_lines)
        else:
            self.current_lines = list(self.default_lines)

    def reset_typewriter(self):
        self.visible_chars = 0.0

    def get_full_text(self):
        return "\n".join([self.name] + self.current_lines)

    def update(self, player, dt):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist_sq = dx * dx + dy * dy

        self.show_prompt = dist_sq <= self.interaction_distance * self.interaction_distance

        if not self.show_prompt:
            self.dialog_open = False
            self.reset_typewriter()

        if self.dialog_open:
            full_text = self.get_full_text()
            self.visible_chars = min(
                len(full_text),
                self.visible_chars + self.typewriter_speed * dt
            )

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if not self.show_prompt:
            return None

        if not self.dialog_open:
            if event.key == pygame.K_e:
                self.dialog_open = True
                self.reset_typewriter()
            return None

        if self.mission_done:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_e):
                self.dialog_open = False
                self.reset_typewriter()
            return None

        if event.key == pygame.K_a:
            self.dialog_open = False
            self.reset_typewriter()
            return "accept"

        if event.key == pygame.K_r:
            self.dialog_open = False
            self.reset_typewriter()
            return "refuse"

        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.dialog_open = False
            self.reset_typewriter()

        return None

    def draw_reward_trees(self, screen, camera_x, camera_y):
        if not self.mission_done:
            return

        base_x = self.rect.centerx
        base_y = self.rect.bottom - 8

        # on utilise exactement le meme dessin que les arbres de la map
        for tree in self.reward_trees:
            tx = base_x + tree["dx"] - camera_x
            ty = base_y + tree["dy"] - camera_y
            draw_snow_pine(screen, tx, ty, tree["size"])

    def draw(self, screen, camera_x, camera_y):
        # arbres derriere l'ours
        self.draw_reward_trees(screen, camera_x, camera_y)

        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y - camera_y

        shadow = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), (0, 0, 28, 10))
        screen.blit(shadow, (draw_x + 4, draw_y + 34))

        if self.image:
            img_x = draw_x - (self.image.get_width() - self.rect.width) // 2
            img_y = draw_y - self.image.get_height() + self.rect.height + self.image_offset_y
            screen.blit(self.image, (img_x, img_y))
        else:
            pygame.draw.ellipse(screen, (205, 220, 230), (draw_x + 6, draw_y + 14, 24, 20))
            pygame.draw.circle(screen, (225, 235, 242), (draw_x + 18, draw_y + 11), 11)
            pygame.draw.circle(screen, (210, 220, 230), (draw_x + 11, draw_y + 3), 4)
            pygame.draw.circle(screen, (210, 220, 230), (draw_x + 25, draw_y + 3), 4)
            pygame.draw.circle(screen, (30, 30, 30), (draw_x + 15, draw_y + 10), 1)
            pygame.draw.circle(screen, (30, 30, 30), (draw_x + 21, draw_y + 10), 1)
            pygame.draw.circle(screen, (50, 50, 50), (draw_x + 18, draw_y + 14), 2)

        if self.show_prompt and not self.dialog_open:
            bubble_bg = pygame.Surface((26, 26), pygame.SRCALPHA)
            pygame.draw.circle(bubble_bg, (20, 30, 50, 215), (13, 13), 13)
            pygame.draw.circle(bubble_bg, (220, 235, 255), (13, 13), 13, 2)
            screen.blit(bubble_bg, (draw_x + 4, draw_y - 30))

            txt = self.small_font.render("E", True, WHITE)
            screen.blit(txt, (draw_x + 12, draw_y - 26))

    def draw_dialog(self, screen):
        if not self.dialog_open:
            return

        box_w = 560
        box_h = 190
        x = 24
        y = HEIGHT - box_h - 24

        panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (8, 16, 30, 225), (0, 0, box_w, box_h), border_radius=14)
        pygame.draw.rect(panel, (210, 225, 245), (0, 0, box_w, box_h), 2, border_radius=14)
        screen.blit(panel, (x, y))

        full_text = self.get_full_text()
        shown_text = full_text[:int(self.visible_chars)]
        split_lines = shown_text.split("\n")

        title = split_lines[0] if split_lines else self.name
        title_surface = self.font.render(title, True, WHITE)
        screen.blit(title_surface, (x + 16, y + 14))

        for i, line in enumerate(split_lines[1:]):
            txt = self.small_font.render(line, True, (225, 235, 245))
            screen.blit(txt, (x + 16, y + 50 + i * 24))

        if self.mission_done:
            help_text = self.small_font.render(
                "ENTREE / ECHAP pour fermer",
                True,
                (180, 220, 255)
            )
        else:
            help_text = self.small_font.render(
                "A = accepter   |   R = refuser",
                True,
                (180, 255, 190)
            )

        screen.blit(help_text, (x + 16, y + box_h - 34))