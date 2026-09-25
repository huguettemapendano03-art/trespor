"""
Main entry point for the Pygame Checkers (Jeu de Dames) Game.
"""

from checkers_game import CheckersGameUI


def main():
    game = CheckersGameUI(vs_ai=True)
    game.run()


if __name__ == "__main__":
    main()
