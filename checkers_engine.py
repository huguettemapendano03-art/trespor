"""
Checkers (Jeu de Dames) Core Engine Module
Manages board representation, move validation, mandatory multi-jumps,
king promotions, and game state checks.
"""

from typing import List, Tuple, Optional, Dict


RED = "RED"      # Player 1 (moves UP by default, starting at rows 5,6,7)
WHITE = "WHITE"  # Player 2 / AI (moves DOWN, starting at rows 0,1,2)


class Piece:
    def __init__(self, row: int, col: int, color: str):
        self.row = row
        self.col = col
        self.color = color
        self.is_king = False

    def make_king(self):
        self.is_king = True

    def copy(self) -> 'Piece':
        p = Piece(self.row, self.col, self.color)
        p.is_king = self.is_king
        return p


class CheckersEngine:
    ROWS = 8
    COLS = 8

    def __init__(self):
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.turn = RED
        self.selected_piece: Optional[Piece] = None
        # valid_moves structure: Dict[dest_pos (r, c), Tuple[source_piece, List[captured_pieces]]]
        self.valid_moves: Dict[Tuple[int, int], Tuple[Piece, List[Piece]]] = {}
        self.red_left = 12
        self.white_left = 12
        self.red_kings = 0
        self.white_kings = 0
        self.winner: Optional[str] = None
        self.must_chain_jump = False
        self.chain_piece: Optional[Piece] = None
        self.reset_board()

    def reset_board(self):
        self.board = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.red_left = 12
        self.white_left = 12
        self.red_kings = 0
        self.white_kings = 0
        self.turn = RED
        self.winner = None
        self.selected_piece = None
        self.must_chain_jump = False
        self.chain_piece = None

        # Standard 8x8 checkers setup
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = Piece(row, col, WHITE)
                    elif row > 4:
                        self.board[row][col] = Piece(row, col, RED)

        self.update_valid_moves()

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            return self.board[row][col]
        return None

    def update_valid_moves(self):
        self.valid_moves = {}

        if self.must_chain_jump and self.chain_piece:
            jumps = self._get_piece_jumps(self.chain_piece)
            if jumps:
                self.valid_moves = jumps
            else:
                self.must_chain_jump = False
                self.chain_piece = None
                self.change_turn()
            return

        # Check for mandatory captures for current player
        all_jumps = {}
        all_regular = {}

        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = self.board[row][col]
                if piece and piece.color == self.turn:
                    jumps = self._get_piece_jumps(piece)
                    if jumps:
                        all_jumps.update(jumps)
                    elif not all_jumps:
                        regular = self._get_piece_regular_moves(piece)
                        all_regular.update(regular)

        # Mandatory jump rule: if any capture is available, player MUST capture
        if all_jumps:
            self.valid_moves = all_jumps
        else:
            self.valid_moves = all_regular

        # Check win/loss condition
        if not self.valid_moves and not self.must_chain_jump:
            self.winner = WHITE if self.turn == RED else RED

    def select_piece(self, row: int, col: int) -> bool:
        piece = self.get_piece(row, col)
        if piece and piece.color == self.turn:
            if self.must_chain_jump and piece != self.chain_piece:
                return False
            self.selected_piece = piece
            return True
        return False

    def move_selected(self, target_row: int, target_col: int) -> bool:
        if not self.selected_piece:
            return False

        start_pos = (self.selected_piece.row, self.selected_piece.col)
        target_pos = (target_row, target_col)

        if target_pos not in self.valid_moves:
            return False

        src_piece, captured_pieces = self.valid_moves[target_pos]
        if (src_piece.row, src_piece.col) != start_pos:
            return False

        self._execute_move(self.selected_piece, target_row, target_col, captured_pieces)
        return True

    def _execute_move(self, piece: Piece, target_row: int, target_col: int, captured: List[Piece]):
        # Move piece on board
        self.board[piece.row][piece.col] = None
        piece.row = target_row
        piece.col = target_col
        self.board[target_row][target_col] = piece

        # Remove captured pieces
        for cap in captured:
            self.board[cap.row][cap.col] = None
            if cap.color == RED:
                self.red_left -= 1
                if cap.is_king:
                    self.red_kings -= 1
            else:
                self.white_left -= 1
                if cap.is_king:
                    self.white_kings -= 1

        # Check King promotion
        promoted = False
        if not piece.is_king:
            if piece.color == RED and target_row == 0:
                piece.make_king()
                self.red_kings += 1
                promoted = True
            elif piece.color == WHITE and target_row == self.ROWS - 1:
                piece.make_king()
                self.white_kings += 1
                promoted = True

        # Check multi-jump chaining if captured and not newly promoted
        if captured and not promoted:
            further_jumps = self._get_piece_jumps(piece)
            if further_jumps:
                self.must_chain_jump = True
                self.chain_piece = piece
                self.selected_piece = piece
                self.update_valid_moves()
                return

        self.must_chain_jump = False
        self.chain_piece = None
        self.selected_piece = None
        self.change_turn()

    def change_turn(self):
        self.turn = WHITE if self.turn == RED else RED
        self.update_valid_moves()

    def _get_piece_regular_moves(self, piece: Piece) -> Dict[Tuple[int, int], Tuple[Piece, List[Piece]]]:
        moves = {}
        directions = []

        if piece.is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == RED:
            directions = [(-1, -1), (-1, 1)]  # UP
        else:
            directions = [(1, -1), (1, 1)]    # DOWN

        for dr, dc in directions:
            r = piece.row + dr
            c = piece.col + dc
            if 0 <= r < self.ROWS and 0 <= c < self.COLS and self.board[r][c] is None:
                moves[(r, c)] = (piece, [])

        return moves

    def _get_piece_jumps(self, piece: Piece) -> Dict[Tuple[int, int], Tuple[Piece, List[Piece]]]:
        jumps = {}
        directions = []

        if piece.is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == RED:
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]

        for dr, dc in directions:
            jump_r = piece.row + dr * 2
            jump_c = piece.col + dc * 2
            mid_r = piece.row + dr
            mid_c = piece.col + dc

            if 0 <= jump_r < self.ROWS and 0 <= jump_c < self.COLS:
                mid_piece = self.board[mid_r][mid_c]
                dest_space = self.board[jump_r][jump_c]
                if mid_piece and mid_piece.color != piece.color and dest_space is None:
                    jumps[(jump_r, jump_c)] = (piece, [mid_piece])

        return jumps

    def copy(self) -> 'CheckersEngine':
        new_engine = CheckersEngine.__new__(CheckersEngine)
        new_engine.board = [[p.copy() if p else None for p in row] for row in self.board]
        new_engine.turn = self.turn
        new_engine.red_left = self.red_left
        new_engine.white_left = self.white_left
        new_engine.red_kings = self.red_kings
        new_engine.white_kings = self.white_kings
        new_engine.winner = self.winner
        new_engine.must_chain_jump = self.must_chain_jump
        new_engine.chain_piece = new_engine.get_piece(self.chain_piece.row, self.chain_piece.col) if self.chain_piece else None
        new_engine.selected_piece = None
        new_engine.valid_moves = {}
        return new_engine
