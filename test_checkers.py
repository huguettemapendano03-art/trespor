# test_checkers.py
import unittest
from checkers.constants import RED, WHITE, ROWS, COLS
from checkers.piece import Piece
from checkers.board import Board
from checkers.game import Game, MODE_TWO_PLAYER, MODE_AI
from checkers.ai import minimax

class TestCheckers(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.game = Game()

    def test_board_initialization(self):
        self.assertEqual(self.board.red_left, 12)
        self.assertEqual(self.board.white_left, 12)
        self.assertEqual(self.board.red_kings, 0)
        self.assertEqual(self.board.white_kings, 0)

        # Check piece placement count
        red_count = len(self.board.get_all_pieces(RED))
        white_count = len(self.board.get_all_pieces(WHITE))
        self.assertEqual(red_count, 12)
        self.assertEqual(white_count, 12)

    def test_piece_movement_and_promotion(self):
        # Create a piece near king promotion line
        p = Piece(6, 1, RED)
        self.board.board[6][1] = p
        self.assertFalse(p.king)

        # Move piece to row 7 (promotion for RED)
        self.board.move(p, 7, 2)
        self.assertTrue(p.king)
        self.assertEqual(self.board.red_kings, 1)

    def test_single_capture(self):
        # Custom setup for capture test
        self.board.board = [[0]*COLS for _ in range(ROWS)]
        red_p = Piece(2, 2, RED)
        white_p = Piece(3, 3, WHITE)
        self.board.board[2][2] = red_p
        self.board.board[3][3] = white_p
        self.board.red_left = 1
        self.board.white_left = 1

        valid_moves = self.board.get_valid_moves(red_p)
        self.assertIn((4, 4), valid_moves)
        self.assertEqual(valid_moves[(4, 4)], [white_p])

        # Perform capture
        self.board.move(red_p, 4, 4)
        self.board.remove(valid_moves[(4, 4)])
        self.assertEqual(self.board.white_left, 0)
        self.assertEqual(self.board.get_piece(3, 3), 0)

    def test_multi_jump_capture(self):
        # Setup board for multi jump
        self.board.board = [[0]*COLS for _ in range(ROWS)]
        red_p = Piece(0, 0, RED)
        white_p1 = Piece(1, 1, WHITE)
        white_p2 = Piece(3, 3, WHITE)
        self.board.board[0][0] = red_p
        self.board.board[1][1] = white_p1
        self.board.board[3][3] = white_p2
        self.board.red_left = 1
        self.board.white_left = 2

        valid_moves = self.board.get_valid_moves(red_p)
        self.assertIn((4, 4), valid_moves)
        captured = valid_moves[(4, 4)]
        self.assertIn(white_p1, captured)
        self.assertIn(white_p2, captured)

    def test_game_turn_and_winner(self):
        self.assertEqual(self.game.turn, RED)
        # Select red piece at (2, 1)
        piece = self.game.board.get_piece(2, 1)
        self.assertIsNotNone(piece)
        self.assertTrue(self.game.select(2, 1))
        # Move to (3, 0)
        self.assertTrue(self.game.select(3, 0))
        self.assertEqual(self.game.turn, WHITE)

    def test_ai_minimax(self):
        # Minimax returns evaluation value and board state
        val, new_board = minimax(self.game.get_board(), 2, float('-inf'), float('inf'), True, self.game)
        self.assertIsNotNone(new_board)
        self.assertIsInstance(val, (int, float))

if __name__ == '__main__':
    unittest.main()
