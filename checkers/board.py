# checkers/board.py
import copy
from checkers.constants import ROWS, COLS, RED, WHITE
from checkers.piece import Piece

class Board:
    def __init__(self):
        self.board = []
        self.red_left = 12
        self.white_left = 12
        self.red_kings = 0
        self.white_kings = 0
        self.create_board()

    def create_board(self):
        self.board = []
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, RED))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def get_piece(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return None

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = 0, self.board[row][col]
        piece.move(row, col)
        self.board[row][col] = piece

        # Promotion to King
        if not piece.king:
            if piece.color == RED and row == ROWS - 1:
                piece.make_king()
                self.red_kings += 1
            elif piece.color == WHITE and row == 0:
                piece.make_king()
                self.white_kings += 1

    def remove(self, pieces):
        for piece in pieces:
            if piece != 0:
                self.board[piece.row][piece.col] = 0
                if piece.color == RED:
                    self.red_left -= 1
                    if piece.king:
                        self.red_kings -= 1
                else:
                    self.white_left -= 1
                    if piece.king:
                        self.white_kings -= 1

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED

        red_has_moves = len(self.get_all_valid_moves(RED)) > 0
        white_has_moves = len(self.get_all_valid_moves(WHITE)) > 0

        if not red_has_moves and not white_has_moves:
            return "DRAW"
        elif not red_has_moves:
            return WHITE
        elif not white_has_moves:
            return RED

        return None

    def get_valid_moves(self, piece):
        moves = {}
        if piece == 0 or piece is None:
            return moves

        directions = piece.get_directions()

        # Check jumps (captures)
        jumps = self._get_jumps(piece, piece.row, piece.col, directions, set())
        if jumps:
            return jumps

        # Check simple moves if no jumps available
        simple_moves = self._get_simple_moves(piece, piece.row, piece.col, directions)
        return simple_moves

    def _get_simple_moves(self, piece, row, col, directions):
        moves = {}
        for dr in directions:
            for dc in [-1, 1]:
                r = row + dr
                c = col + dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    target = self.board[r][c]
                    if target == 0:
                        moves[(r, c)] = []
        return moves

    def _get_jumps(self, piece, row, col, directions, visited_captured):
        jumps = {}
        for dr in directions:
            for dc in [-1, 1]:
                r_jump = row + dr
                c_jump = col + dc
                r_land = row + 2 * dr
                c_land = col + 2 * dc

                if 0 <= r_land < ROWS and 0 <= c_land < COLS:
                    mid_piece = self.board[r_jump][c_jump]
                    land_space = self.board[r_land][c_land]

                    # Must jump over an enemy piece that hasn't been captured yet in this turn
                    if (mid_piece != 0 and mid_piece is not None and
                        mid_piece.color != piece.color and
                        (mid_piece.row, mid_piece.col) not in visited_captured):

                        if land_space == 0 or (r_land == piece.row and c_land == piece.col):
                            new_visited = set(visited_captured)
                            new_visited.add((mid_piece.row, mid_piece.col))

                            # Continuation jumps
                            # Note: If piece becomes king during jump, it continues as king, but usually promotion happens at end of turn.
                            # Standard rules: piece promotes if it reaches back row, but if it jumps, promotion stops multi-jump in standard or continues as king in standard checkers.
                            # Here, kings can jump in all 4 directions.
                            next_directions = [-1, 1] if (piece.king or (piece.color == RED and r_land == ROWS - 1) or (piece.color == WHITE and r_land == 0)) else directions

                            sub_jumps = self._get_jumps_recursive(piece, r_land, c_land, next_directions, new_visited, [mid_piece])
                            for end_pos, captured_list in sub_jumps.items():
                                jumps[end_pos] = captured_list

        return jumps

    def _get_jumps_recursive(self, piece, row, col, directions, visited_captured, captured_so_far):
        results = {(row, col): captured_so_far}
        found_further_jump = False

        for dr in directions:
            for dc in [-1, 1]:
                r_jump = row + dr
                c_jump = col + dc
                r_land = row + 2 * dr
                c_land = col + 2 * dc

                if 0 <= r_land < ROWS and 0 <= c_land < COLS:
                    mid_piece = self.board[r_jump][c_jump]
                    land_space = self.board[r_land][c_land]

                    if (mid_piece != 0 and mid_piece is not None and
                        mid_piece.color != piece.color and
                        (mid_piece.row, mid_piece.col) not in visited_captured):

                        if land_space == 0 or (r_land == piece.row and c_land == piece.col):
                            found_further_jump = True
                            new_visited = set(visited_captured)
                            new_visited.add((mid_piece.row, mid_piece.col))

                            next_directions = [-1, 1] if (piece.king or (piece.color == RED and r_land == ROWS - 1) or (piece.color == WHITE and r_land == 0)) else directions
                            sub = self._get_jumps_recursive(piece, r_land, c_land, next_directions, new_visited, captured_so_far + [mid_piece])
                            for end_pos, captured_list in sub.items():
                                if end_pos != (row, col):
                                    results[end_pos] = captured_list

        if found_further_jump:
            del results[(row, col)]

        return results

    def get_all_valid_moves(self, color):
        moves = {}
        has_jumps = False

        # First scan for any jumps (forced capture rule)
        for piece in self.get_all_pieces(color):
            valid_m = self.get_valid_moves(piece)
            for move, captured in valid_m.items():
                if captured:
                    has_jumps = True
                    break

        for piece in self.get_all_pieces(color):
            valid_m = self.get_valid_moves(piece)
            filtered_m = {}
            for move, captured in valid_m.items():
                if has_jumps:
                    if captured:
                        filtered_m[move] = captured
                else:
                    filtered_m[move] = captured
            if filtered_m:
                moves[piece] = filtered_m

        return moves

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece is not None and piece.color == color:
                    pieces.append(piece)
        return pieces

    def evaluate(self):
        # Evaluation function for AI
        # Kings are worth 1.5x regular pieces, position weight gives incentive to control center
        score = 0
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece != 0 and piece is not None:
                    value = 10 + (2 if 2 <= r <= 5 and 2 <= c <= 5 else 0)
                    if piece.king:
                        value += 5
                    if piece.color == WHITE:
                        score += value
                    else:
                        score -= value
        return score
