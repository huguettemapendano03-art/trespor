"""
Unit Test Suite for Checkers Game Logic and AI Engine.
"""

import unittest
from checkers_engine import CheckersEngine, Piece, RED, WHITE
from checkers_game import MinimaxAI


class TestCheckersEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CheckersEngine()

    def test_initial_board_setup(self):
        self.assertEqual(self.engine.red_left, 12)
        self.assertEqual(self.engine.white_left, 12)
        self.assertEqual(self.engine.turn, RED)
        self.assertEqual(self.engine.winner, None)

    def test_select_and_move_regular_piece(self):
        # Select RED piece at row 5, col 2
        self.assertTrue(self.engine.select_piece(5, 2))
        # Move to (4, 1)
        moved = self.engine.move_selected(4, 1)
        self.assertTrue(moved)
        self.assertIsNone(self.engine.get_piece(5, 2))
        self.assertIsNotNone(self.engine.get_piece(4, 1))
        # Turn changes to WHITE
        self.assertEqual(self.engine.turn, WHITE)

    def test_mandatory_capture(self):
        # Set up a board where RED must jump
        self.engine.board = [[None for _ in range(8)] for _ in range(8)]
        red_p = Piece(4, 3, RED)
        white_p = Piece(3, 2, WHITE)
        self.engine.board[4][3] = red_p
        self.engine.board[3][2] = white_p
        self.engine.red_left = 1
        self.engine.white_left = 1
        self.engine.turn = RED
        self.engine.update_valid_moves()

        # Valid moves should ONLY contain the jump capture to (2, 1)
        self.assertIn((2, 1), self.engine.valid_moves)

        self.engine.select_piece(4, 3)
        self.engine.move_selected(2, 1)

        # Captured piece removed
        self.assertIsNone(self.engine.get_piece(3, 2))
        self.assertEqual(self.engine.white_left, 0)

    def test_king_promotion(self):
        self.engine.board = [[None for _ in range(8)] for _ in range(8)]
        red_p = Piece(1, 2, RED)
        self.engine.board[1][2] = red_p
        self.engine.turn = RED
        self.engine.update_valid_moves()

        self.engine.select_piece(1, 2)
        self.engine.move_selected(0, 1)

        piece = self.engine.get_piece(0, 1)
        self.assertTrue(piece.is_king)
        self.assertEqual(self.engine.red_kings, 1)


class TestMinimaxAI(unittest.TestCase):
    def setUp(self):
        self.engine = CheckersEngine()
        self.ai = MinimaxAI(depth=2)

    def test_ai_finds_move(self):
        self.engine.turn = WHITE
        self.engine.update_valid_moves()
        eval_score, best_move = self.ai.minimax(self.engine, depth=2, alpha=-1000, beta=1000, maximizing=True)
        self.assertIsNotNone(best_move)


if __name__ == "__main__":
    unittest.main()
