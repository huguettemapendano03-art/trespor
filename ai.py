import random
import math
from checkers_game import (
    WHITE, BLACK, EMPTY, WHITE_MAN, WHITE_KING, BLACK_MAN, BLACK_KING,
    get_opponent, is_king, is_white, is_black
)

EASY = 'easy'
MEDIUM = 'medium'
HARD = 'hard'

class CheckersAI:
    def __init__(self, difficulty=MEDIUM):
        self.difficulty = difficulty

    def get_best_move(self, game):
        """Finds best move for current player in the game state based on difficulty."""
        legal_moves = game.get_all_legal_moves()
        if not legal_moves:
            return None

        if self.difficulty == EASY:
            # Random pick among valid moves, prioritizing captures if available
            return random.choice(legal_moves)

        elif self.difficulty == MEDIUM:
            depth = 2
            return self._minimax_search(game, depth)

        elif self.difficulty == HARD:
            depth = 4 if game.size == 8 else 3
            return self._minimax_search(game, depth)

        return random.choice(legal_moves)

    def _minimax_search(self, game, max_depth):
        legal_moves = game.get_all_legal_moves()
        if not legal_moves:
            return None

        best_move = None
        current_player = game.turn
        best_eval = -math.inf

        # Shuffle moves to prevent deterministic repetitive behavior on equal scores
        shuffled_moves = list(legal_moves)
        random.shuffle(shuffled_moves)

        alpha = -math.inf
        beta = math.inf

        for move in shuffled_moves:
            cloned_game = game.clone()
            cloned_game.make_move(move)

            eval_score = self._minimax(cloned_game, max_depth - 1, alpha, beta, False, current_player)

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move

            alpha = max(alpha, best_eval)

        return best_move if best_move else random.choice(legal_moves)

    def _minimax(self, game, depth, alpha, beta, is_maximizing, ai_player):
        if depth == 0 or game.game_over:
            return self.evaluate_board(game, ai_player)

        current_turn = game.turn
        legal_moves = game.get_all_legal_moves()

        if not legal_moves:
            if current_turn == ai_player:
                return -10000 # Loss for AI
            else:
                return 10000  # Win for AI

        if is_maximizing:
            max_eval = -math.inf
            for move in legal_moves:
                cloned = game.clone()
                cloned.make_move(move)
                eval_val = self._minimax(cloned, depth - 1, alpha, beta, False, ai_player)
                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in legal_moves:
                cloned = game.clone()
                cloned.make_move(move)
                eval_val = self._minimax(cloned, depth - 1, alpha, beta, True, ai_player)
                min_eval = min(min_eval, eval_val)
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_board(self, game, ai_player):
        """
        Evaluates current board position from perspective of ai_player.
        Heuristics:
        1. Material count (Man=10, King=25)
        2. Positional control (Center control, row advancement)
        3. Protection (Edges and back row defense)
        """
        if game.game_over:
            if game.winner == ai_player:
                return 10000
            elif game.winner is not None:
                return -10000
            return 0

        score = 0
        size = game.size

        man_val = 100
        king_val = 260

        ai_is_white = (ai_player == WHITE)

        for r in range(size):
            for c in range(size):
                p = game.board[r][c]
                if p == EMPTY:
                    continue

                p_is_ai = (is_white(p) == ai_is_white)
                multiplier = 1 if p_is_ai else -1

                # Material Value
                if is_king(p):
                    p_score = king_val
                else:
                    p_score = man_val
                    # Reward advancement towards kinging
                    advancement = (size - 1 - r) if is_white(p) else r
                    p_score += advancement * 8

                # Edge bonus / protection
                if c == 0 or c == size - 1:
                    p_score += 10 # Safe against standard side captures

                # Center control bonus
                center_start = size // 4
                center_end = size - center_start
                if center_start <= r < center_end and center_start <= c < center_end:
                    p_score += 15

                score += p_score * multiplier

        return score
