# checkers/game.py
from checkers.constants import RED, WHITE
from checkers.board import Board

# Game Modes
MODE_TWO_PLAYER = "2P"
MODE_AI = "AI"

class Game:
    def __init__(self, mode=MODE_TWO_PLAYER, ai_difficulty="MEDIUM"):
        self.mode = mode
        self.ai_difficulty = ai_difficulty
        self._init()

    def _init(self):
        self.selected_piece = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.winner = None
        self.must_capture_pieces = set()
        self.update_valid_moves_for_turn()

    def reset(self):
        self._init()

    def update_valid_moves_for_turn(self):
        all_moves = self.board.get_all_valid_moves(self.turn)
        self.must_capture_pieces = set()

        # Check if any moves involve captures
        has_jumps = False
        for piece, moves in all_moves.items():
            for move, captured in moves.items():
                if captured:
                    has_jumps = True
                    self.must_capture_pieces.add(piece)

        if self.selected_piece:
            if self.selected_piece in all_moves:
                self.valid_moves = all_moves[self.selected_piece]
            else:
                self.valid_moves = {}

    def select(self, row, col):
        if self.winner is not None:
            return False

        if self.selected_piece:
            result = self._move(row, col)
            if not result:
                self.selected_piece = None
                self.select(row, col)
            return result

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece is not None and piece.color == self.turn:
            all_moves = self.board.get_all_valid_moves(self.turn)
            if piece in all_moves:
                self.selected_piece = piece
                self.valid_moves = all_moves[piece]
                return True

        return False

    def _move(self, row, col):
        piece = self.selected_piece
        if piece and (row, col) in self.valid_moves:
            captured = self.valid_moves[(row, col)]
            self.board.move(piece, row, col)
            if captured:
                self.board.remove(captured)

            self.change_turn()
            return True
        return False

    def change_turn(self):
        self.valid_moves = {}
        self.selected_piece = None
        self.winner = self.board.winner()

        if self.winner is None:
            if self.turn == RED:
                self.turn = WHITE
            else:
                self.turn = RED
            self.update_valid_moves_for_turn()

    def get_board(self):
        return self.board

    def ai_move(self, new_board):
        self.board = new_board
        self.change_turn()
