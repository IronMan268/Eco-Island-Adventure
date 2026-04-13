"""
ÉTATS - Gère les différents écrans du jeu
"""

from enum import Enum

class GameState(Enum):
    """
    Énumération des états possibles du jeu
    """
    DIALOGUE = 1      # Écran d'intro avec dialogue
    ISLAND = 2        # Écran de l'île
    PUZZLE = 3        # Écrans de puzzle/épreuves
    VICTORY = 4       # Écran de victoire
    LOSE = 5