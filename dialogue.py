import pygame
from constants import *


class DialogueBox:
    def __init__(self, text_list):
        self.text_list = text_list
        self.index = 0

        self.current_text = ""
        self.full_text = self.text_list[self.index]

        self.char_index = 0
        self.timer = 0
        self.finished = False

        self.font = pygame.font.SysFont("consolas", 30, bold=True)

        self.x = 50
        self.y = 430
        self.max_width = 700
        self.line_height = 34

    def update(self):
        if self.finished:
            return

        self.timer += 1
        if self.timer >= TEXT_SPEED:
            self.timer = 0
            if self.char_index < len(self.full_text):
                self.current_text += self.full_text[self.char_index]
                self.char_index += 1

    def next_text(self):
        if self.finished:
            return True

        if self.char_index < len(self.full_text):
            self.current_text = self.full_text
            self.char_index = len(self.full_text)
            return False

        self.index += 1

        if self.index >= len(self.text_list):
            self.finished = True
            return True

        self.full_text = self.text_list[self.index]
        self.current_text = ""
        self.char_index = 0
        return False

    def draw(self, screen):
        words = self.current_text.split(" ")
        lines = []
        line = ""

        for word in words:
            test_line = line + word + " "
            if self.font.size(test_line)[0] > self.max_width:
                lines.append(line)
                line = word + " "
            else:
                line = test_line

        lines.append(line)

        for i, l in enumerate(lines):
            shadow = self.font.render(l, True, BLACK)
            text = self.font.render(l, True, WHITE)

            screen.blit(shadow, (self.x + 2, self.y + i * self.line_height + 2))
            screen.blit(text, (self.x, self.y + i * self.line_height))