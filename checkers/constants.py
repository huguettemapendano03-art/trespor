# checkers/constants.py
import pygame

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Color Palette (Realistic / Premium Look)
# Dark and Light Wood / Board colors
BOARD_LIGHT = (238, 214, 175)
BOARD_DARK = (140, 84, 45)
BORDER_COLOR = (70, 40, 20)
HIGHLIGHT_COLOR = (255, 215, 0)
VALID_MOVE_COLOR = (46, 204, 113)
CAPTURE_MOVE_COLOR = (231, 76, 60)

# Piece colors (Ivory/Cream vs Dark Mahogany/Black)
RED_PIECE = (192, 57, 43)      # Dark Red / Crimson
RED_PIECE_LIGHT = (231, 76, 60)
RED_PIECE_DARK = (120, 30, 20)

WHITE_PIECE = (236, 240, 241)  # Cream / Off-white
WHITE_PIECE_LIGHT = (255, 255, 255)
WHITE_PIECE_DARK = (189, 195, 199)

# Standard Player colors (Player 1 = RED/DARK, Player 2 = WHITE/LIGHT)
RED = (192, 57, 43)
WHITE = (236, 240, 241)
BLACK = (30, 30, 30)
GOLD = (241, 196, 15)
GRAY = (127, 140, 141)
