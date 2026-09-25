"""
Checkers Pygame Application & Minimax AI Module
Features:
- Smooth Pygame board rendering with wooden themes & piece anti-aliasing
- Legal move indicators & selection highlights
- Minimax AI with alpha-beta pruning for single-player mode
- Capture count display & game over banners
- Reset and mode toggle (PvP / vs AI)
"""

import math
import sys
import time
import pygame
from typing import Tuple, Optional, List, Dict

from checkers_engine import CheckersEngine, Piece, RED, WHITE

# Color Palette
BOARD_LIGHT = (238, 216, 192)
BOARD_DARK = (118, 75, 43)
HIGHLIGHT_BLUE = (100, 149, 237)
VALID_MOVE_GREEN = (46, 204, 113)
CROWN_GOLD = (241, 196, 15)

PIECE_RED = (217, 30, 24)
PIECE_RED_BORDER = (150, 10, 10)
PIECE_WHITE = (245, 245, 245)
PIECE_WHITE_BORDER = (180, 180, 180)

SIDEBAR_BG = (40, 44, 52)
TEXT_WHITE = (255, 255, 255)
TEXT_GOLD = (241, 196, 15)


class MinimaxAI:
    def __init__(self, depth: int = 3):
        self.depth = depth

    def evaluate_board(self, engine: CheckersEngine) -> float:
        # Score from WHITE perspective (AI is WHITE)
        score = (engine.white_left - engine.red_left) * 10
        score += (engine.white_kings - engine.red_kings) * 5

        # Encourage advancing regular pieces towards king row
        for row in range(engine.ROWS):
            for col in range(engine.COLS):
                piece = engine.board[row][col]
                if piece and not piece.is_king:
                    if piece.color == WHITE:
                        score += row * 0.2  # Moving down
                    else:
                        score -= (7 - row) * 0.2  # Moving up

        return score

    def get_all_possible_states(self, engine: CheckersEngine, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int], CheckersEngine]]:
        states = []
        original_turn = engine.turn
        engine.turn = color
        engine.update_valid_moves()

        valid_moves_map = dict(engine.valid_moves)

        for dest, (src_piece, captured) in valid_moves_map.items():
            start_pos = (src_piece.row, src_piece.col)
            test_eng = self._clone_engine(engine)
            if test_eng.select_piece(start_pos[0], start_pos[1]):
                if test_eng.move_selected(dest[0], dest[1]):
                    states.append((start_pos, dest, test_eng))

        engine.turn = original_turn
        engine.update_valid_moves()
        return states

    def _clone_engine(self, engine: CheckersEngine) -> CheckersEngine:
        clone = CheckersEngine.__new__(CheckersEngine)
        clone.board = [[p.copy() if p else None for p in row] for row in engine.board]
        clone.turn = engine.turn
        clone.red_left = engine.red_left
        clone.white_left = engine.white_left
        clone.red_kings = engine.red_kings
        clone.white_kings = engine.white_kings
        clone.winner = engine.winner
        clone.must_chain_jump = engine.must_chain_jump
        clone.chain_piece = clone.get_piece(engine.chain_piece.row, engine.chain_piece.col) if engine.chain_piece else None
        clone.selected_piece = None
        clone.valid_moves = {}
        clone.update_valid_moves()
        return clone

    def minimax(self, engine: CheckersEngine, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[float, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        if depth == 0 or engine.winner:
            return self.evaluate_board(engine), None

        best_move = None

        if maximizing:
            max_eval = -math.inf
            states = self.get_all_possible_states(engine, WHITE)
            if not states:
                return self.evaluate_board(engine), None

            for start, dest, new_engine in states:
                eval_score, _ = self.minimax(new_engine, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (start, dest)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            states = self.get_all_possible_states(engine, RED)
            if not states:
                return self.evaluate_board(engine), None

            for start, dest, new_engine in states:
                eval_score, _ = self.minimax(new_engine, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (start, dest)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move


class CheckersGameUI:
    BOARD_SIZE = 600
    SIDEBAR_WIDTH = 220
    SQUARE_SIZE = BOARD_SIZE // 8

    def __init__(self, vs_ai: bool = True):
        pygame.init()
        pygame.font.init()

        self.width = self.BOARD_SIZE + self.SIDEBAR_WIDTH
        self.height = self.BOARD_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Jeu de Dames Moderne - Pygame Checkers")

        self.clock = pygame.time.Clock()
        self.engine = CheckersEngine()
        self.ai = MinimaxAI(depth=3)
        self.vs_ai = vs_ai

        self.font_title = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            # AI Move Turn Check
            if self.vs_ai and self.engine.turn == WHITE and not self.engine.winner:
                pygame.time.delay(300)
                _, best_move = self.ai.minimax(self.engine, depth=3, alpha=-math.inf, beta=math.inf, maximizing=True)
                if best_move:
                    start, dest = best_move
                    self.engine.select_piece(start[0], start[1])
                    self.engine.move_selected(dest[0], dest[1])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.engine.reset_board()
                    elif event.key == pygame.K_m:
                        self.vs_ai = not self.vs_ai
                        self.engine.reset_board()

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def handle_mouse_click(self, pos: Tuple[int, int]):
        x, y = pos

        # Click inside Sidebar (Buttons)
        if x > self.BOARD_SIZE:
            # Reset Button Click
            if 60 <= y <= 95:
                self.engine.reset_board()
            # Toggle Mode Click
            elif 105 <= y <= 140:
                self.vs_ai = not self.vs_ai
                self.engine.reset_board()
            return

        # Click inside Board
        row = y // self.SQUARE_SIZE
        col = x // self.SQUARE_SIZE

        if self.engine.selected_piece:
            # Attempt to move to clicked square
            moved = self.engine.move_selected(row, col)
            if not moved:
                # Select another piece if valid
                self.engine.select_piece(row, col)
        else:
            self.engine.select_piece(row, col)

    def draw(self):
        self.screen.fill(SIDEBAR_BG)
        self.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        self.draw_sidebar()

        if self.engine.winner:
            self.draw_winner_banner()

    def draw_board(self):
        for row in range(CheckersEngine.ROWS):
            for col in range(CheckersEngine.COLS):
                color = BOARD_LIGHT if (row + col) % 2 == 0 else BOARD_DARK
                rect = pygame.Rect(col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def draw_highlights(self):
        # Selected piece highlight
        if self.engine.selected_piece:
            sp = self.engine.selected_piece
            rect = pygame.Rect(sp.col * self.SQUARE_SIZE, sp.row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE)
            pygame.draw.rect(self.screen, HIGHLIGHT_BLUE, rect, 4)

            # Valid moves circles
            start_pos = (sp.row, sp.col)
            for dest, (src_piece, _) in self.engine.valid_moves.items():
                if (src_piece.row, src_piece.col) == start_pos:
                    center_x = dest[1] * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    center_y = dest[0] * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    pygame.draw.circle(self.screen, VALID_MOVE_GREEN, (center_x, center_y), 12)

    def draw_pieces(self):
        for row in range(CheckersEngine.ROWS):
            for col in range(CheckersEngine.COLS):
                piece = self.engine.get_piece(row, col)
                if piece:
                    center_x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    center_y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    radius = self.SQUARE_SIZE // 2 - 10

                    fill_color = PIECE_RED if piece.color == RED else PIECE_WHITE
                    border_color = PIECE_RED_BORDER if piece.color == RED else PIECE_WHITE_BORDER

                    # Draw outer circle border & inner filled circle
                    pygame.draw.circle(self.screen, border_color, (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, fill_color, (center_x, center_y), radius - 4)

                    # Draw King Crown symbol if piece is a king
                    if piece.is_king:
                        crown_radius = radius // 2
                        pygame.draw.circle(self.screen, CROWN_GOLD, (center_x, center_y), crown_radius)

    def draw_sidebar(self):
        sidebar_x = self.BOARD_SIZE + 15

        # Title
        title_surf = self.font_title.render("JEU DE DAMES", True, TEXT_GOLD)
        self.screen.blit(title_surf, (sidebar_x, 15))

        # Reset Button Box
        btn_reset = pygame.Rect(self.BOARD_SIZE + 15, 60, 190, 35)
        pygame.draw.rect(self.screen, (60, 64, 72), btn_reset, border_radius=6)
        txt_reset = self.font_small.render("🔄 Recommencer (R)", True, TEXT_WHITE)
        self.screen.blit(txt_reset, (sidebar_x + 15, 68))

        # Mode Button Box
        btn_mode = pygame.Rect(self.BOARD_SIZE + 15, 105, 190, 35)
        pygame.draw.rect(self.screen, (60, 64, 72), btn_mode, border_radius=6)
        mode_text = "Mode: vs IA 🤖" if self.vs_ai else "Mode: 2 Joueurs 👥"
        txt_mode = self.font_small.render(mode_text, True, TEXT_WHITE)
        self.screen.blit(txt_mode, (sidebar_x + 10, 113))

        # Current Turn Indicator
        turn_str = "Tour: ROUGE" if self.engine.turn == RED else "Tour: BLANC"
        turn_color = PIECE_RED if self.engine.turn == RED else TEXT_WHITE
        txt_turn = self.font_medium.render(turn_str, True, turn_color)
        self.screen.blit(txt_turn, (sidebar_x, 170))

        # Score & Captures
        pygame.draw.line(self.screen, (80, 80, 80), (self.BOARD_SIZE + 10, 210), (self.width - 10, 210), 2)

        txt_scores = self.font_medium.render("Pions Restants :", True, TEXT_GOLD)
        self.screen.blit(txt_scores, (sidebar_x, 225))

        # Red remaining
        txt_red = self.font_small.render(f"🔴 Rouges : {self.engine.red_left} (Rois: {self.engine.red_kings})", True, TEXT_WHITE)
        self.screen.blit(txt_red, (sidebar_x, 260))

        # White remaining
        txt_white = self.font_small.render(f"⚪ Blancs : {self.engine.white_left} (Rois: {self.engine.white_kings})", True, TEXT_WHITE)
        self.screen.blit(txt_white, (sidebar_x, 290))

        # Info instructions
        pygame.draw.line(self.screen, (80, 80, 80), (self.BOARD_SIZE + 10, 340), (self.width - 10, 340), 2)

        info1 = self.font_small.render("Règles :", True, TEXT_GOLD)
        info2 = self.font_small.render("- Prises obligatoires", True, TEXT_WHITE)
        info3 = self.font_small.render("- Rois déplacent 4-diag", True, TEXT_WHITE)
        info4 = self.font_small.render("- Touche M : Changer Mode", True, TEXT_WHITE)

        self.screen.blit(info1, (sidebar_x, 355))
        self.screen.blit(info2, (sidebar_x, 380))
        self.screen.blit(info3, (sidebar_x, 400))
        self.screen.blit(info4, (sidebar_x, 420))

    def draw_winner_banner(self):
        overlay = pygame.Surface((self.BOARD_SIZE, 120))
        overlay.set_alpha(220)
        overlay.fill((20, 20, 20))
        self.screen.blit(overlay, (0, self.BOARD_SIZE // 2 - 60))

        winner_str = "Victoire des ROUGES !" if self.engine.winner == RED else "Victoire des BLANCS !"
        win_surf = self.font_title.render(winner_str, True, CROWN_GOLD)
        rect = win_surf.get_rect(center=(self.BOARD_SIZE // 2, self.BOARD_SIZE // 2 - 15))
        self.screen.blit(win_surf, rect)

        sub_surf = self.font_small.render("Appuyez sur R pour rejouer", True, TEXT_WHITE)
        sub_rect = sub_surf.get_rect(center=(self.BOARD_SIZE // 2, self.BOARD_SIZE // 2 + 20))
        self.screen.blit(sub_surf, sub_rect)
