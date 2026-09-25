import copy

# Player Constants
WHITE = 'W' # Bottom player (moves up, r decreases)
BLACK = 'B' # Top player (moves down, r increases)

# Piece Constants
EMPTY = None
WHITE_MAN = 'w'
WHITE_KING = 'W'
BLACK_MAN = 'b'
BLACK_KING = 'B'

def get_player_pieces(player):
    """Returns set of piece characters corresponding to player."""
    if player == WHITE:
        return {WHITE_MAN, WHITE_KING}
    else:
        return {BLACK_MAN, BLACK_KING}

def get_opponent(player):
    return BLACK if player == WHITE else WHITE

def is_king(piece):
    return piece in (WHITE_KING, BLACK_KING)

def is_white(piece):
    return piece in (WHITE_MAN, WHITE_KING)

def is_black(piece):
    return piece in (BLACK_MAN, BLACK_KING)


class Move:
    def __init__(self, start, end, captures=None, is_kinging=False):
        self.start = start          # (row, col)
        self.end = end              # (row, col)
        self.captures = captures or [] # List of captured (row, col)
        self.is_kinging = is_kinging
        self.path = [start, end]    # Complete step-by-step path

    def __repr__(self):
        return f"Move({self.start}->{self.end}, captures={self.captures})"

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.start == other.start and self.end == other.end and self.captures == other.captures


class CheckersGame:
    """
    Checkers core game engine supporting custom board sizes (8x8 or 10x10 French Draughts rules).
    - Mandatory multi-captures (rule: maximum captures or mandatory capture if available).
    - Flying kings (in 10x10 mode or configurable) / standard king moves.
    """
    def __init__(self, size=10, flying_kings=True):
        self.size = size # 8 or 10
        self.flying_kings = flying_kings
        self.turn = WHITE
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.captured_white = 0
        self.captured_black = 0
        self.move_history = []
        self.selected_piece = None
        self.must_continue_jump = False
        self.active_jump_pos = None
        self.game_over = False
        self.winner = None

        self.reset_game()

    def reset_game(self):
        self.turn = WHITE
        self.captured_white = 0
        self.captured_black = 0
        self.move_history = []
        self.selected_piece = None
        self.must_continue_jump = False
        self.active_jump_pos = None
        self.game_over = False
        self.winner = None
        self.board = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]

        # Place pieces on dark squares (where (r + c) % 2 != 0 or == 1 depending on convention)
        # In international draughts, dark squares are (r + c) % 2 == 1
        rows_per_side = 3 if self.size == 8 else 4

        for r in range(rows_per_side):
            for c in range(self.size):
                if (r + c) % 2 == 1:
                    self.board[r][c] = BLACK_MAN

        for r in range(self.size - rows_per_side, self.size):
            for c in range(self.size):
                if (r + c) % 2 == 1:
                    self.board[r][c] = WHITE_MAN

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def get_piece(self, r, c):
        if self.in_bounds(r, c):
            return self.board[r][c]
        return None

    def get_all_legal_moves(self, player=None):
        if player is None:
            player = self.turn

        # If mid multi-jump, only active_jump_pos can continue jumping
        if self.must_continue_jump and self.active_jump_pos:
            r, c = self.active_jump_pos
            jumps = self._get_jumps_for_piece(r, c, self.board)
            if jumps:
                max_cap = max(len(m.captures) for m in jumps)
                return [m for m in jumps if len(m.captures) == max_cap]
            return []

        all_jumps = []
        all_simple_moves = []

        player_pcs = get_player_pieces(player)
        for r in range(self.size):
            for c in range(self.size):
                piece = self.board[r][c]
                if piece in player_pcs:
                    jumps = self._get_jumps_for_piece(r, c, self.board)
                    if jumps:
                        all_jumps.extend(jumps)
                    else:
                        simple = self._get_simple_moves_for_piece(r, c, self.board)
                        all_simple_moves.extend(simple)

        # Mandatory capture rule: If any capture exists, player MUST capture
        if all_jumps:
            # Maximum capture rule (International draughts rule: must choose path capturing max pieces)
            max_cap = max(len(m.captures) for m in all_jumps)
            return [m for m in all_jumps if len(m.captures) == max_cap]

        return all_simple_moves

    def _get_simple_moves_for_piece(self, r, c, board):
        piece = board[r][c]
        if not piece:
            return []

        moves = []
        directions = []

        if piece == WHITE_MAN:
            directions = [(-1, -1), (-1, 1)] # Up
        elif piece == BLACK_MAN:
            directions = [(1, -1), (1, 1)]   # Down
        elif is_king(piece):
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        if is_king(piece) and self.flying_kings:
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while self.in_bounds(nr, nc) and board[nr][nc] == EMPTY:
                    moves.append(Move((r, c), (nr, nc)))
                    nr += dr
                    nc += dc
        else:
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and board[nr][nc] == EMPTY:
                    moves.append(Move((r, c), (nr, nc)))

        return moves

    def _get_jumps_for_piece(self, r, c, board):
        piece = board[r][c]
        if not piece:
            return []

        results = []
        visited_captures = set()

        self._find_jumps_recursive(r, c, piece, board, visited_captures, [(r, c)], [], results)
        return results

    def _find_jumps_recursive(self, r, c, piece, board, visited_captures, path, captures, results):
        found_jump = False
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        is_w = is_white(piece)
        opp_func = is_black if is_w else is_white

        king_mode = is_king(piece)

        for dr, dc in directions:
            if king_mode and self.flying_kings:
                # Flying king jump logic
                nr, nc = r + dr, c + dc
                opp_pos = None
                while self.in_bounds(nr, nc):
                    p = board[nr][nc]
                    if p == EMPTY:
                        if opp_pos is not None:
                            # Jump behind opponent
                            found_jump = True
                            new_board = [row[:] for row in board]
                            new_board[r][c] = EMPTY
                            new_board[opp_pos[0]][opp_pos[1]] = EMPTY
                            new_board[nr][nc] = piece

                            self._find_jumps_recursive(
                                nr, nc, piece, new_board,
                                visited_captures | {opp_pos},
                                path + [(nr, nc)],
                                captures + [opp_pos],
                                results
                            )
                        nr += dr
                        nc += dc
                    elif opp_func(p) and (nr, nc) not in visited_captures:
                        if opp_pos is None:
                            opp_pos = (nr, nc)
                            nr += dr
                            nc += dc
                        else:
                            # Two pieces in a row - blocked
                            break
                    else:
                        # Friendly piece or already captured piece blocking
                        break
            else:
                # Standard man or non-flying king jump logic
                # Note: Men can jump backwards in French/International draughts
                opp_r, opp_c = r + dr, c + dc
                land_r, land_c = r + 2 * dr, c + 2 * dc

                if self.in_bounds(land_r, land_c):
                    mid_piece = board[opp_r][opp_c]
                    if mid_piece and opp_func(mid_piece) and (opp_r, opp_c) not in visited_captures:
                        if board[land_r][land_c] == EMPTY:
                            found_jump = True
                            new_board = [row[:] for row in board]
                            new_board[r][c] = EMPTY
                            new_board[opp_r][opp_c] = EMPTY
                            new_board[land_r][land_c] = piece

                            self._find_jumps_recursive(
                                land_r, land_c, piece, new_board,
                                visited_captures | {(opp_r, opp_c)},
                                path + [(land_r, land_c)],
                                captures + [(opp_r, opp_c)],
                                results
                            )

        if not found_jump and captures:
            move = Move(path[0], path[-1], captures=captures)
            move.path = path
            # Check promotion
            final_r, _ = path[-1]
            if (piece == WHITE_MAN and final_r == 0) or (piece == BLACK_MAN and final_r == self.size - 1):
                move.is_kinging = True
            results.append(move)

    def make_move(self, move):
        """
        Executes a Move object on the game board.
        Returns sound_type string to play: 'move', 'capture', 'king', or None.
        """
        if self.game_over:
            return None

        start_r, start_c = move.start
        end_r, end_c = move.end
        piece = self.board[start_r][start_c]

        if not piece:
            return None

        sound_event = 'move'

        # Clear start square
        self.board[start_r][start_c] = EMPTY

        # Execute captures
        if move.captures:
            sound_event = 'capture'
            for cr, cc in move.captures:
                cap_p = self.board[cr][cc]
                self.board[cr][cc] = EMPTY
                if cap_p:
                    if is_white(cap_p):
                        self.captured_white += 1
                    else:
                        self.captured_black += 1

        # Check Kinging promotion
        kinged = False
        if piece == WHITE_MAN and end_r == 0:
            piece = WHITE_KING
            kinged = True
        elif piece == BLACK_MAN and end_r == self.size - 1:
            piece = BLACK_KING
            kinged = True

        if kinged:
            sound_event = 'king'

        self.board[end_r][end_c] = piece
        self.move_history.append((move, copy.deepcopy(self.board)))

        # Switch turn
        self.turn = get_opponent(self.turn)
        self.must_continue_jump = False
        self.active_jump_pos = None

        # Check Win/Draw
        self.check_game_over()

        return sound_event

    def check_game_over(self):
        legal_moves = self.get_all_legal_moves(self.turn)
        if not legal_moves:
            self.game_over = True
            self.winner = get_opponent(self.turn)
            return True
        return False

    def clone(self):
        """Creates a deep copy of the game state for AI evaluation."""
        new_game = CheckersGame(size=self.size, flying_kings=self.flying_kings)
        new_game.turn = self.turn
        new_game.board = [row[:] for row in self.board]
        new_game.captured_white = self.captured_white
        new_game.captured_black = self.captured_black
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        return new_game
