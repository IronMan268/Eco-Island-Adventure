import pygame
from constants import *
from dialogue import DialogueBox


class Intro:
    def __init__(self, screen):
        # Référence à l'écran principal
        self.screen = screen

        # Permet de savoir si l'intro est terminée
        self.finished = False

        # Chargement de l'image de fond
        image = pygame.image.load("assets/intro.png").convert()

        # Dimensions originales de l'image
        img_w, img_h = image.get_size()

        # Calcul du scale pour garder les proportions
        scale = min(WIDTH / img_w, HEIGHT / img_h)

        # Nouvelles dimensions adaptées à l'écran
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        # Redimensionnement de l'image
        self.background = pygame.transform.scale(image, (new_w, new_h))

        # Centrage de l'image sur l'écran
        self.bg_x = (WIDTH - new_w) // 2
        self.bg_y = (HEIGHT - new_h) // 2

        # Création de la boîte de dialogue avec le texte d'intro
        self.dialogue = DialogueBox([
            "Bienvenue sur Eco Island Adventure !",
            "Je suis le Maire Pingouin.",
            "Autrefois, notre île était un paradis de glace...",
            "Mais aujourd'hui, elle est envahie par la pollution.",
            "La banquise s'abîme, les zones naturelles disparaissent, et le danger approche.",
            "Nous avons besoin de toi pour inverser la situation.",
            "Ta mission sera claire : faire tomber le taux de pollution à 0% dans le temps donné.",
            "Pour cela, tu devras accomplir des quêtes dans les zones polluées de l'île.",
            "Ramasse les déchets, nettoie les secteurs contaminés et restaure la banquise.",
            "Chaque quête réussie rapprochera l'île de sa survie.",
            "Bonne chance..."
        ])

    def handle_event(self, event):
        # Si le joueur appuie sur Entrée → on passe au texte suivant
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            done = self.dialogue.next_text()

            # Si tous les textes sont lus → fin de l'intro
            if done:
                self.finished = True

    def update(self):
        # Mise à jour de la boîte de dialogue (animation texte, etc.)
        self.dialogue.update()

    def draw(self):
        # Fond écran
        self.screen.fill(DARK_BLUE)

        # Affichage de l'image de fond
        self.screen.blit(self.background, (self.bg_x, self.bg_y))

        # Affichage du dialogue par-dessus
        self.dialogue.draw(self.screen)