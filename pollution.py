import pygame
from constants import *


class PollutionSystem:
    def __init__(self):
        # Valeur actuelle de pollution
        self.value = float(POLLUTION_START)

        # Valeur max (100% généralement)
        self.max_value = float(POLLUTION_MAX)

        # Combien la pollution augmente à chaque tick
        self.increase_amount = float(POLLUTION_INCREASE)

        # Temps entre chaque augmentation (en secondes)
        self.interval = float(POLLUTION_INTERVAL)

        # Timer interne pour gérer les augmentations
        self.timer = 0.0

        # Fonts utilisées pour l'affichage
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)

        # Dimensions de la barre
        self.bar_width = 220
        self.bar_height = 15

        # Position du panel (marges écran)
        self.margin_top = 20
        self.margin_right = 20

        # Padding interne du panel
        self.panel_padding = 12

        # Zone pour afficher le % à droite
        self.percent_area_width = 54

        # Hauteur totale du panel
        self.panel_height = 78

    def update(self, dt):
        # On incrémente le timer avec le delta time
        self.timer += dt

        # Tant que le timer dépasse l'intervalle → on ajoute de la pollution
        while self.timer >= self.interval:
            self.timer -= self.interval
            self.add_pollution(self.increase_amount)

    def add_pollution(self, amount):
        # Ajoute de la pollution sans dépasser le max
        self.value = min(self.max_value, self.value + amount)

    def remove_pollution(self, amount):
        # Retire de la pollution sans descendre sous 0
        self.value = max(0.0, self.value - amount)

    def set_pollution(self, value):
        # Force une valeur de pollution (clamp entre 0 et max)
        self.value = max(0.0, min(self.max_value, float(value)))

    def get_percent(self):
        # Retourne le pourcentage actuel
        if self.max_value <= 0:
            return 0.0
        return (self.value / self.max_value) * 100.0

    def draw(self, screen):
        # Calcul du pourcentage et de la largeur de la barre remplie
        percent = self.get_percent()
        fill_width = int((percent / 100.0) * self.bar_width)

        # Largeur totale du panel (barre + % + padding)
        panel_width = (
            self.panel_padding * 2
            + self.bar_width
            + self.percent_area_width
        )

        # Position du panel en haut à droite
        panel_x = WIDTH - panel_width - self.margin_right
        panel_y = self.margin_top

        # Création du fond semi-transparent
        panel = pygame.Surface((panel_width, self.panel_height), pygame.SRCALPHA)

        # Fond sombre
        pygame.draw.rect(
            panel,
            (18, 10, 12, 190),
            (0, 0, panel_width, self.panel_height),
            border_radius=10
        )

        # Bordure rouge légère
        pygame.draw.rect(
            panel,
            (255, 120, 120, 90),
            (0, 0, panel_width, self.panel_height),
            2,
            border_radius=10
        )

        # Affichage du panel
        screen.blit(panel, (panel_x, panel_y))

        # Position interne du contenu
        content_x = panel_x + self.panel_padding
        title_y = panel_y + 8
        bar_y = panel_y + 34

        # Texte titre
        title = self.font.render("POLLUTION", True, WHITE)
        screen.blit(title, (content_x, title_y))

        # Fond de la barre (vide)
        pygame.draw.rect(
            screen,
            (45, 20, 24),
            (content_x, bar_y, self.bar_width, self.bar_height),
            border_radius=8
        )

        # Barre remplie (pollution actuelle)
        if fill_width > 0:
            pygame.draw.rect(
                screen,
                (210, 60, 60),
                (content_x, bar_y, fill_width, self.bar_height),
                border_radius=8
            )

        # Contour de la barre
        pygame.draw.rect(
            screen,
            (255, 220, 220),
            (content_x, bar_y, self.bar_width, self.bar_height),
            2,
            border_radius=8
        )

        # Texte du pourcentage
        percent_text = self.small_font.render(f"{int(percent)}%", True, WHITE)

        # Position du texte % à droite de la barre
        percent_x = content_x + self.bar_width + 10
        percent_y = bar_y + (self.bar_height - percent_text.get_height()) // 2

        screen.blit(percent_text, (percent_x, percent_y))

        # Temps restant avant la prochaine augmentation
        remaining = max(0, int(self.interval - self.timer))

        # Texte d'info (augmentation future)
        timer_text = self.small_font.render(
            f"+{int(self.increase_amount)}% dans {remaining}s",
            True,
            (255, 210, 210)
        )

        # Affichage du timer sous la barre
        screen.blit(timer_text, (content_x, bar_y + self.bar_height + 8))