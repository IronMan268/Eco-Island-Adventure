import pygame


def remove_background(surface):
    # Copie de l'image avec gestion de la transparence
    surface = surface.copy().convert_alpha()

    width, height = surface.get_size()

    # On prend la couleur du pixel en haut à gauche (fond supposé)
    bg_color = surface.get_at((0, 0))

    # Tolérance pour éviter les petits écarts de couleur
    tolerance = 15  # peut être ajusté si besoin

    # Parcours de tous les pixels de l'image
    for y in range(height):
        for x in range(width):
            r, g, b, a = surface.get_at((x, y))

            # Si la couleur est proche du fond → on rend transparent
            if (
                abs(r - bg_color.r) < tolerance and
                abs(g - bg_color.g) < tolerance and
                abs(b - bg_color.b) < tolerance
            ):
                surface.set_at((x, y), (0, 0, 0, 0))

    return surface


def load_player_sprites(path):
    # Chargement de l'image complète (spritesheet)
    image = pygame.image.load(path).convert_alpha()

    # Nettoyage du fond pour enlever la couleur unie
    image = remove_background(image)

    width, height = image.get_size()

    # On découpe l'image en 4 parties (2x2)
    frame_w = width // 2
    frame_h = height // 2

    sprites = {}

    # Attribution des directions selon la position dans la spritesheet
    sprites["down"] = image.subsurface((0, 0, frame_w, frame_h)).copy()
    sprites["up"] = image.subsurface((frame_w, 0, frame_w, frame_h)).copy()
    sprites["left"] = image.subsurface((0, frame_h, frame_w, frame_h)).copy()
    sprites["right"] = image.subsurface((frame_w, frame_h, frame_w, frame_h)).copy()
    
    return sprites