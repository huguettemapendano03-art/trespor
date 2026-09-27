# checkers/piece.py
from checkers.constants import RED, WHITE, SQUARE_SIZE

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def get_directions(self):
        if self.king:
            return [-1, 1]
        elif self.color == RED:
            return [1]   # Red moves down
        else:
            return [-1]  # White moves up

    def __repr__(self):
        return f"{'K' if self.king else 'P'}({'R' if self.color == RED else 'W'})"
