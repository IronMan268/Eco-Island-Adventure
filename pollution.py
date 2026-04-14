import pygame
from constants import *


class PollutionSystem:
    def __init__(self):
        self.value = float(POLLUTION_START)

        self.max_value = float(POLLUTION_MAX)

        self.increase_amount = float(POLLUTION_INCREASE)

        self.interval = float(POLLUTION_INTERVAL)

        self.timer = 0.0

        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)

        self.bar_width = 220
        self.bar_height = 15

        self.margin_top = 20
        self.margin_right = 20

        self.panel_padding = 12

        self.percent_area_width = 54

        self.panel_height = 78

    def update(self, dt):
        self.timer += dt

        while self.timer >= self.interval:
            self.timer -= self.interval
            self.add_pollution(self.increase_amount)

    def add_pollution(self, amount):
        self.value = min(self.max_value, self.value + amount)

    def remove_pollution(self, amount):
        self.value = max(0.0, self.value - amount)

    def set_pollution(self, value):
        self.value = max(0.0, min(self.max_value, float(value)))

    def get_percent(self):
        if self.max_value <= 0:
            return 0.0
        return (self.value / self.max_value) * 100.0

    def draw(self, screen):
        percent = self.get_percent()
        fill_width = int((percent / 100.0) * self.bar_width)

        panel_width = (
            self.panel_padding * 2
            + self.bar_width
            + self.percent_area_width
        )

        panel_x = WIDTH - panel_width - self.margin_right
        panel_y = self.margin_top

        panel = pygame.Surface((panel_width, self.panel_height), pygame.SRCALPHA)

        pygame.draw.rect(
            panel,
            (18, 10, 12, 190),
            (0, 0, panel_width, self.panel_height),
            border_radius=10
        )

        pygame.draw.rect(
            panel,
            (255, 120, 120, 90),
            (0, 0, panel_width, self.panel_height),
            2,
            border_radius=10
        )

        screen.blit(panel, (panel_x, panel_y))

        content_x = panel_x + self.panel_padding
        title_y = panel_y + 8
        bar_y = panel_y + 34

        title = self.font.render("POLLUTION", True, WHITE)
        screen.blit(title, (content_x, title_y))

        pygame.draw.rect(
            screen,
            (45, 20, 24),
            (content_x, bar_y, self.bar_width, self.bar_height),
            border_radius=8
        )

        if fill_width > 0:
            pygame.draw.rect(
                screen,
                (210, 60, 60),
                (content_x, bar_y, fill_width, self.bar_height),
                border_radius=8
            )

        pygame.draw.rect(
            screen,
            (255, 220, 220),
            (content_x, bar_y, self.bar_width, self.bar_height),
            2,
            border_radius=8
        )

        percent_text = self.small_font.render(f"{int(percent)}%", True, WHITE)

        percent_x = content_x + self.bar_width + 10
        percent_y = bar_y + (self.bar_height - percent_text.get_height()) // 2

        screen.blit(percent_text, (percent_x, percent_y))

        remaining = max(0, int(self.interval - self.timer))

        timer_text = self.small_font.render(
            f"+{int(self.increase_amount)}% dans {remaining}s",
            True,
            (255, 210, 210)
        )

        screen.blit(timer_text, (content_x, bar_y + self.bar_height + 8))