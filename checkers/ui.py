# checkers/ui.py
import pygame
import math
from checkers.constants import (
    WIDTH, HEIGHT, ROWS, COLS, SQUARE_SIZE,
    BOARD_LIGHT, BOARD_DARK, BORDER_COLOR,
    RED_PIECE, RED_PIECE_LIGHT, RED_PIECE_DARK,
    WHITE_PIECE, WHITE_PIECE_LIGHT, WHITE_PIECE_DARK,
    HIGHLIGHT_COLOR, VALID_MOVE_COLOR, CAPTURE_MOVE_COLOR,
    RED, WHITE, GOLD, BLACK, GRAY
)

HEADER_HEIGHT = 100
BOARD_OFFSET_Y = HEADER_HEIGHT
WINDOW_WIDTH = WIDTH
WINDOW_HEIGHT = HEIGHT + HEADER_HEIGHT

class UI:
    def __init__(self, win):
        self.win = win
        self.font_large = pygame.font.SysFont("helvetica", 36, bold=True)
        self.font_medium = pygame.font.SysFont("helvetica", 24, bold=True)
        self.font_small = pygame.font.SysFont("helvetica", 18, bold=True)
        self.board_surface = self._create_wood_board_texture()

    def _create_wood_board_texture(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        for row in range(ROWS):
            for col in range(COLS):
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)

                if (row + col) % 2 == 0:
                    base_color = BOARD_LIGHT
                else:
                    base_color = BOARD_DARK

                pygame.draw.rect(surface, base_color, rect)

                # Subtle inner bevel gradient for realism
                inner_rect = (x + 2, y + 2, SQUARE_SIZE - 4, SQUARE_SIZE - 4)
                if (row + col) % 2 != 0:
                    pygame.draw.rect(surface, (base_color[0] + 15, base_color[1] + 10, base_color[2] + 5), inner_rect, 1)
                    pygame.draw.line(surface, (100, 55, 25), (x, y + SQUARE_SIZE - 1), (x + SQUARE_SIZE - 1, y + SQUARE_SIZE - 1), 2)
                    pygame.draw.line(surface, (100, 55, 25), (x + SQUARE_SIZE - 1, y), (x + SQUARE_SIZE - 1, y + SQUARE_SIZE - 1), 2)
                else:
                    pygame.draw.line(surface, (255, 235, 205), (x, y), (x + SQUARE_SIZE - 1, y), 2)
                    pygame.draw.line(surface, (255, 235, 205), (x, y), (x, y + SQUARE_SIZE - 1), 2)

        return surface

    def draw_board(self):
        self.win.blit(self.board_surface, (0, BOARD_OFFSET_Y))

    def draw_pieces(self, board):
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.board[row][col]
                if piece != 0 and piece is not None:
                    self.draw_piece(piece)

    def draw_piece(self, piece):
        radius = SQUARE_SIZE // 2 - 12
        cx = piece.x
        cy = piece.y + BOARD_OFFSET_Y

        # Piece colors
        if piece.color == RED:
            main_color = RED_PIECE
            light_color = RED_PIECE_LIGHT
            dark_color = RED_PIECE_DARK
        else:
            main_color = WHITE_PIECE
            light_color = WHITE_PIECE_LIGHT
            dark_color = WHITE_PIECE_DARK

        # Shadow
        pygame.draw.circle(self.win, (20, 20, 20, 150), (cx + 4, cy + 6), radius)

        # Base 3D bevel circles
        pygame.draw.circle(self.win, dark_color, (cx, cy), radius)
        pygame.draw.circle(self.win, main_color, (cx - 1, cy - 2), radius - 3)
        pygame.draw.circle(self.win, light_color, (cx - 3, cy - 4), radius - 6)
        pygame.draw.circle(self.win, main_color, (cx - 2, cy - 2), radius - 8)

        # Concentric inner grooves for realistic wooden checker piece look
        pygame.draw.circle(self.win, dark_color, (cx, cy), radius - 14, 2)
        pygame.draw.circle(self.win, light_color, (cx - 1, cy - 1), radius - 18, 1)

        # Specular highlight
        highlight_pos = (cx - radius // 3, cy - radius // 3)
        pygame.draw.circle(self.win, (255, 255, 255, 180), highlight_pos, radius // 5)

        # Crown icon if King
        if piece.king:
            self.draw_crown(cx, cy)

    def draw_crown(self, cx, cy):
        # Golden metallic 3D Crown
        points = [
            (cx - 14, cy + 8),
            (cx - 14, cy - 6),
            (cx - 7, cy + 1),
            (cx, cy - 10),
            (cx + 7, cy + 1),
            (cx + 14, cy - 6),
            (cx + 14, cy + 8),
        ]
        pygame.draw.polygon(self.win, (180, 140, 0), [(x + 1, y + 2) for x, y in points]) # Shadow
        pygame.draw.polygon(self.win, GOLD, points)
        pygame.draw.polygon(self.win, (255, 250, 200), points, 2) # Highlight

        # Jewels on crown tips
        for jewel_x, jewel_y in [(cx - 14, cy - 6), (cx, cy - 10), (cx + 14, cy - 6)]:
            pygame.draw.circle(self.win, (220, 20, 20), (jewel_x, jewel_y), 3)

    def draw_highlights(self, game):
        # Selected piece highlight
        if game.selected_piece:
            piece = game.selected_piece
            cx = piece.x
            cy = piece.y + BOARD_OFFSET_Y
            radius = SQUARE_SIZE // 2 - 6
            pygame.draw.circle(self.win, HIGHLIGHT_COLOR, (cx, cy), radius, 4)

        # Mandatory capture piece indicators
        if game.must_capture_pieces:
            for p in game.must_capture_pieces:
                cx = p.x
                cy = p.y + BOARD_OFFSET_Y
                radius = SQUARE_SIZE // 2 - 4
                pygame.draw.circle(self.win, CAPTURE_MOVE_COLOR, (cx, cy), radius, 3)

        # Valid moves indicators
        for move, captured in game.valid_moves.items():
            row, col = move
            cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y

            if captured:
                # Capture move indicator
                pygame.draw.circle(self.win, CAPTURE_MOVE_COLOR, (cx, cy), 18)
                pygame.draw.circle(self.win, (255, 255, 255), (cx, cy), 8)
            else:
                # Normal valid move indicator
                pygame.draw.circle(self.win, VALID_MOVE_COLOR, (cx, cy), 14)
                pygame.draw.circle(self.win, (255, 255, 255), (cx, cy), 6)

    def draw_header(self, game):
        # Top banner frame
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(self.win, BORDER_COLOR, header_rect)
        pygame.draw.line(self.win, GOLD, (0, HEADER_HEIGHT - 2), (WINDOW_WIDTH, HEADER_HEIGHT - 2), 3)

        # Game Title
        title_surf = self.font_large.render("JEU DE DAMES", True, GOLD)
        self.win.blit(title_surf, (WINDOW_WIDTH // 2 - title_surf.get_width() // 2, 8))

        # Mode Indicator
        mode_text = f"Mode: {'2 Joueurs' if game.mode == '2P' else 'VS IA (' + game.ai_difficulty + ')'}"
        mode_surf = self.font_small.render(mode_text, True, (220, 220, 220))
        self.win.blit(mode_surf, (WINDOW_WIDTH // 2 - mode_surf.get_width() // 2, 48))

        # Turn indicator
        turn_str = "Tour: " + ("Rouge (Joueur 1)" if game.turn == RED else ("Blanc (Joueur 2)" if game.mode == "2P" else "Blanc (IA)"))
        turn_color = RED_PIECE_LIGHT if game.turn == RED else WHITE_PIECE
        turn_surf = self.font_medium.render(turn_str, True, turn_color)
        self.win.blit(turn_surf, (WINDOW_WIDTH // 2 - turn_surf.get_width() // 2, 70))

        # Score / Remaining pieces counters
        # Left (Red)
        pygame.draw.circle(self.win, RED_PIECE, (30, 50), 16)
        red_cnt_surf = self.font_medium.render(f"x {game.board.red_left}", True, (255, 255, 255))
        self.win.blit(red_cnt_surf, (55, 38))

        # Right (White)
        pygame.draw.circle(self.win, WHITE_PIECE, (WINDOW_WIDTH - 85, 50), 16)
        white_cnt_surf = self.font_medium.render(f"x {game.board.white_left}", True, (255, 255, 255))
        self.win.blit(white_cnt_surf, (WINDOW_WIDTH - 60, 38))

    def draw_menu(self, selected_mode, selected_diff):
        self.win.fill(BORDER_COLOR)

        # Menu Panel Box
        panel = pygame.Rect(100, 100, WINDOW_WIDTH - 200, WINDOW_HEIGHT - 200)
        pygame.draw.rect(self.win, BOARD_DARK, panel, border_radius=15)
        pygame.draw.rect(self.win, GOLD, panel, width=4, border_radius=15)

        # Title
        title = self.font_large.render("JEU DE DAMES PREMUM", True, GOLD)
        self.win.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 140))

        subtitle = self.font_medium.render("Choisissez votre mode de jeu", True, (240, 240, 240))
        self.win.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 200))

        # Buttons
        # Mode 2 Players Button
        p2_btn = pygame.Rect(200, 270, 400, 50)
        p2_color = GOLD if selected_mode == "2P" else BOARD_LIGHT
        pygame.draw.rect(self.win, p2_color, p2_btn, border_radius=10)
        p2_txt = self.font_medium.render("1. Deux Joueurs (Local)", True, BLACK if selected_mode == "2P" else BORDER_COLOR)
        self.win.blit(p2_txt, (p2_btn.centerx - p2_txt.get_width() // 2, p2_btn.centery - p2_txt.get_height() // 2))

        # Mode AI Button
        ai_btn = pygame.Rect(200, 340, 400, 50)
        ai_color = GOLD if selected_mode == "AI" else BOARD_LIGHT
        pygame.draw.rect(self.win, ai_color, ai_btn, border_radius=10)
        ai_txt = self.font_medium.render("2. Joueur vs Ordinateur (IA)", True, BLACK if selected_mode == "AI" else BORDER_COLOR)
        self.win.blit(ai_txt, (ai_btn.centerx - ai_txt.get_width() // 2, ai_btn.centery - ai_txt.get_height() // 2))

        # Difficulty Buttons (If AI mode selected)
        diff_easy_btn = pygame.Rect(200, 450, 120, 45)
        diff_med_btn = pygame.Rect(340, 450, 120, 45)
        diff_hard_btn = pygame.Rect(480, 450, 120, 45)

        if selected_mode == "AI":
            diff_title = self.font_medium.render("Difficulté de l'IA:", True, GOLD)
            self.win.blit(diff_title, (200, 415))

            for btn, label, diff_val in [
                (diff_easy_btn, "Facile", "EASY"),
                (diff_med_btn, "Moyen", "MEDIUM"),
                (diff_hard_btn, "Difficile", "HARD")
            ]:
                b_color = HIGHLIGHT_COLOR if selected_diff == diff_val else BOARD_LIGHT
                pygame.draw.rect(self.win, b_color, btn, border_radius=8)
                txt = self.font_small.render(label, True, BLACK)
                self.win.blit(txt, (btn.centerx - txt.get_width() // 2, btn.centery - txt.get_height() // 2))

        # Start Game Button
        start_btn = pygame.Rect(250, 560, 300, 60)
        pygame.draw.rect(self.win, (46, 204, 113), start_btn, border_radius=12)
        pygame.draw.rect(self.win, (255, 255, 255), start_btn, width=2, border_radius=12)
        start_txt = self.font_large.render("LANCER LA PARTIE", True, (255, 255, 255))
        self.win.blit(start_txt, (start_btn.centerx - start_txt.get_width() // 2, start_btn.centery - start_txt.get_height() // 2))

        return {
            "2P": p2_btn,
            "AI": ai_btn,
            "EASY": diff_easy_btn,
            "MEDIUM": diff_med_btn,
            "HARD": diff_hard_btn,
            "START": start_btn
        }

    def draw_game_over(self, winner, mode):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.win.blit(overlay, (0, 0))

        box = pygame.Rect(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 150, 500, 300)
        pygame.draw.rect(self.win, BOARD_DARK, box, border_radius=15)
        pygame.draw.rect(self.win, GOLD, box, width=4, border_radius=15)

        title = self.font_large.render("FIN DE LA PARTIE", True, GOLD)
        self.win.blit(title, (box.centerx - title.get_width() // 2, box.y + 30))

        if winner == "DRAW":
            win_txt_str = "Match Nul !"
        elif winner == RED:
            win_txt_str = "Victoire du Joueur Rouge !"
        else:
            win_txt_str = "Victoire du Joueur Blanc !" if mode == "2P" else "L'IA a gagné !"

        win_surf = self.font_medium.render(win_txt_str, True, (255, 255, 255))
        self.win.blit(win_surf, (box.centerx - win_surf.get_width() // 2, box.y + 100))

        restart_btn = pygame.Rect(box.centerx - 120, box.y + 180, 240, 50)
        pygame.draw.rect(self.win, GOLD, restart_btn, border_radius=10)
        rst_txt = self.font_medium.render("Recommencer [R]", True, BLACK)
        self.win.blit(rst_txt, (restart_btn.centerx - rst_txt.get_width() // 2, restart_btn.centery - rst_txt.get_height() // 2))

        return restart_btn
