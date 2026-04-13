import os
import pygame
from constants import WIDTH, HEIGHT


class EndScreen:
    def __init__(self, image_path):
        self.image = None

        if os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path).convert()
                self.image = pygame.transform.scale(img, (WIDTH, HEIGHT))
            except Exception:
                self.image = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (0, 0))
        else:
            screen.fill((0, 0, 0))