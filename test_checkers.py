import unittest
from checkers_game import (
    CheckersGame, Move, WHITE, BLACK, EMPTY,
    WHITE_MAN, WHITE_KING, BLACK_MAN, BLACK_KING
)
from ai import CheckersAI, EASY, MEDIUM, HARD

class TestCheckersRules(unittest.TestCase):
    def test_initial_setup_10x10(self):
        game = CheckersGame(size=10)
        self.assertEqual(game.size, 10)
        self.assertEqual(game.turn, WHITE)
        black_count = sum(row.count(BLACK_MAN) for row in game.board)
        white_count = sum(row.count(WHITE_MAN) for row in game.board)
        self.assertEqual(black_count, 20)
        self.assertEqual(white_count, 20)

    def test_initial_setup_8x8(self):
        game = CheckersGame(size=8)
        self.assertEqual(game.size, 8)
        black_count = sum(row.count(BLACK_MAN) for row in game.board)
        white_count = sum(row.count(WHITE_MAN) for row in game.board)
        self.assertEqual(black_count, 12)
        self.assertEqual(white_count, 12)

    def test_simple_move(self):
        game = CheckersGame(size=10)
        legal_moves = game.get_all_legal_moves(WHITE)
        self.assertGreater(len(legal_moves), 0)
        move = legal_moves[0]
        sound = game.make_move(move)
        self.assertEqual(sound, 'move')
        self.assertEqual(game.turn, BLACK)

    def test_mandatory_capture(self):
        game = CheckersGame(size=10)
        game.board = [[EMPTY for _ in range(10)] for _ in range(10)]
        game.board[5][5] = WHITE_MAN
        game.board[4][4] = BLACK_MAN

        moves = game.get_all_legal_moves(WHITE)
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].start, (5, 5))
        self.assertEqual(moves[0].end, (3, 3))
        self.assertEqual(moves[0].captures, [(4, 4)])

        sound = game.make_move(moves[0])
        self.assertEqual(sound, 'capture')
        self.assertEqual(game.get_piece(4, 4), EMPTY)
        self.assertEqual(game.get_piece(3, 3), WHITE_MAN)

    def test_king_promotion(self):
        game = CheckersGame(size=10)
        game.board = [[EMPTY for _ in range(10)] for _ in range(10)]
        game.board[1][1] = WHITE_MAN

        moves = game.get_all_legal_moves(WHITE)
        move = [m for m in moves if m.start == (1, 1) and m.end == (0, 0)][0]
        sound = game.make_move(move)

        self.assertEqual(sound, 'king')
        self.assertEqual(game.get_piece(0, 0), WHITE_KING)

    def test_flying_king_movement(self):
        game = CheckersGame(size=10, flying_kings=True)
        game.board = [[EMPTY for _ in range(10)] for _ in range(10)]
        game.board[5][5] = WHITE_KING

        moves = game.get_all_legal_moves(WHITE)
        self.assertEqual(len(moves), 17)

    def test_game_over_no_moves(self):
        game = CheckersGame(size=8)
        game.board = [[EMPTY for _ in range(8)] for _ in range(8)]
        game.board[4][4] = WHITE_MAN
        game.turn = BLACK
        game.check_game_over()
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, WHITE)

class TestCheckersAI(unittest.TestCase):
    def test_ai_move_selection_easy(self):
        game = CheckersGame(size=10)
        ai = CheckersAI(EASY)
        move = ai.get_best_move(game)
        self.assertIsNotNone(move)
        self.assertIn(move, game.get_all_legal_moves())

    def test_ai_move_selection_medium(self):
        game = CheckersGame(size=10)
        game.turn = BLACK
        ai = CheckersAI(MEDIUM)
        move = ai.get_best_move(game)
        self.assertIsNotNone(move)
        self.assertIn(move, game.get_all_legal_moves())

    def test_ai_prioritizes_capture(self):
        game = CheckersGame(size=8)
        game.board = [[EMPTY for _ in range(8)] for _ in range(8)]
        game.board[4][4] = BLACK_MAN
        game.board[5][5] = WHITE_MAN
        game.turn = BLACK

        ai = CheckersAI(HARD)
        move = ai.get_best_move(game)
        self.assertIsNotNone(move)
        # Capture move must be selected
        self.assertEqual(len(move.captures), 1)
        self.assertEqual(move.end, (6, 6))

if __name__ == '__main__':
    unittest.main()
