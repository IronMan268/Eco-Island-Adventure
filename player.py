import math
import pygame
from constants import *


def trim_transparent(surface):
    # Crée un mask pour détecter les pixels visibles
    mask = pygame.mask.from_surface(surface)

    # Récupère les zones non transparentes
    rects = mask.get_bounding_rects()

    # Si rien trouvé → image vide, on retourne une copie
    if not rects:
        return surface.copy()

    # On prend la première zone utile
    rect = rects[0]

    # On découpe l'image pour enlever les pixels transparents autour
    return surface.subsurface(rect).copy()


class Player:
    def __init__(self, x, y):
        # Direction actuelle du joueur
        self.direction = "down"

        # Chargement des sprites selon la direction
        raw_sprites = {
            "down": pygame.image.load("assets/player/penguin_down.png").convert_alpha(),
            "up": pygame.image.load("assets/player/penguin_up.png").convert_alpha(),
            "left": pygame.image.load("assets/player/penguin_left.png").convert_alpha(),
            "right": pygame.image.load("assets/player/penguin_right.png").convert_alpha(),
        }

        self.base_sprites = {}

        # Hauteur cible pour uniformiser tous les sprites
        target_height = 42

        for key, image in raw_sprites.items():
            # On enlève les bords transparents
            trimmed = trim_transparent(image)

            # Dimensions originales
            img_w, img_h = trimmed.get_size()

            # Calcul du facteur de scale pour garder les proportions
            scale = target_height / img_h

            # Nouvelles dimensions
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)

            # On redimensionne le sprite
            self.base_sprites[key] = pygame.transform.scale(trimmed, (new_w, new_h))

        # Hitbox (plus petite que le sprite pour un meilleur feeling)
        hitbox_width = 22
        hitbox_height = 18

        # Position réelle en float (plus fluide)
        self.x = float(x)
        self.y = float(y)

        # Rect utilisé pour les collisions
        self.rect = pygame.Rect(int(self.x), int(self.y), hitbox_width, hitbox_height)

        # Etat du mouvement
        self.is_moving = False

        # Temps d'animation
        self.anim_time = 0.0

        # Décalage pour coller le sprite au sol
        self.sprite_ground_offset = 2

    def update(self, keys, world, dt):
        move_x = 0.0
        move_y = 0.0

        # Gestion des déplacements horizontaux
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            move_x = -PLAYER_SPEED
            self.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = PLAYER_SPEED
            self.direction = "right"

        # Gestion des déplacements verticaux
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            move_y = -PLAYER_SPEED
            self.direction = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = PLAYER_SPEED
            self.direction = "down"

        # Normalisation diagonale (évite d'aller plus vite en diagonale)
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        # Détection si le joueur bouge
        self.is_moving = (move_x != 0 or move_y != 0)

        # Mise à jour du temps d'animation
        if self.is_moving:
            self.anim_time += dt * 11
        else:
            self.anim_time = 0.0

        # Déplacement horizontal avec collision
        if move_x != 0:
            new_rect = self.rect.copy()
            new_x = self.x + move_x * dt
            new_rect.x = int(new_x)

            if not world.rect_collides(new_rect):
                self.x = new_x
                self.rect.x = int(self.x)

        # Déplacement vertical avec collision
        if move_y != 0:
            new_rect = self.rect.copy()
            new_y = self.y + move_y * dt
            new_rect.y = int(new_y)

            if not world.rect_collides(new_rect):
                self.y = new_y
                self.rect.y = int(self.y)

    def get_animated_sprite(self):
        # Sprite de base selon la direction
        sprite = self.base_sprites[self.direction]

        # Si le joueur ne bouge pas → pas d'animation
        if not self.is_moving:
            return sprite, 0, 0, 1.0

        # Ondes pour créer une animation fluide
        wave = math.sin(self.anim_time)
        wave2 = math.sin(self.anim_time * 2)

        # Petit rebond vertical
        bounce_y = int(abs(wave) * 1)

        # Effet d'écrasement / étirement (illusion de pas)
        width_factor = 1.0 + (abs(wave) * 0.05)
        height_factor = 1.0 - (abs(wave) * 0.05)

        # Léger mouvement horizontal (balancement)
        sway_x = int(wave2 * 1.5)

        # Nouvelle taille du sprite animé
        new_w = max(1, int(sprite.get_width() * width_factor))
        new_h = max(1, int(sprite.get_height() * height_factor))

        animated = pygame.transform.scale(sprite, (new_w, new_h))

        # Ombre qui varie légèrement (donne un effet de profondeur)
        shadow_factor = 1.0 - (abs(wave) * 0.10)

        return animated, bounce_y, sway_x, shadow_factor

    def draw(self, screen, camera_x, camera_y):
        # Récupération du sprite animé
        sprite, bounce_y, sway_x, shadow_factor = self.get_animated_sprite()

        # Position du sprite à l'écran (centré sur la hitbox)
        draw_x = self.rect.centerx - sprite.get_width() // 2 - camera_x + sway_x
        draw_y = (
            self.rect.bottom
            - sprite.get_height()
            - camera_y
            + self.sprite_ground_offset
            - bounce_y
        )

        # Calcul de l'ombre sous le joueur
        shadow_w = max(12, int(self.rect.width * shadow_factor))
        shadow_h = 4
        shadow_x = self.rect.centerx - shadow_w // 2 - camera_x
        shadow_y = self.rect.bottom - camera_y + 1

        # Création de l'ombre (ellipse semi-transparente)
        shadow_surface = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 45), (0, 0, shadow_w, shadow_h))

        screen.blit(shadow_surface, (shadow_x, shadow_y))

        # Affichage du joueur
        screen.blit(sprite, (draw_x, draw_y))