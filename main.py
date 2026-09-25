import os
import sys
import math
import time
import argparse

# Force dummy video driver if running headless test
if "--test-run" in sys.argv:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from checkers_game import (
    CheckersGame, Move, WHITE, BLACK, EMPTY,
    WHITE_MAN, WHITE_KING, BLACK_MAN, BLACK_KING,
    is_king, is_white, is_black, get_opponent
)
from ai import CheckersAI, EASY, MEDIUM, HARD
from sound import get_sound_manager

# Window Dimensions
WIN_WIDTH = 1024
WIN_HEIGHT = 768
FPS = 60

# Colors
COLOR_BG = (28, 25, 23)
COLOR_TEXT = (240, 238, 233)
COLOR_TEXT_DIM = (160, 155, 145)
COLOR_GOLD = (234, 179, 8)
COLOR_ACCENT = (14, 165, 233)
COLOR_SUCCESS = (34, 197, 94)
COLOR_DANGER = (239, 68, 68)

# Board Theme Colors
THEMES = {
    'bois_classic': {
        'name': 'Bois Classique',
        'light_sq': (238, 214, 175),
        'dark_sq': (139, 87, 42),
        'border': (80, 45, 20),
        'highlight': (250, 204, 21, 150),
        'valid_move': (34, 197, 94, 180)
    },
    'acajou': {
        'name': 'Acajou de Luxe',
        'light_sq': (245, 230, 210),
        'dark_sq': (110, 38, 14),
        'border': (60, 18, 5),
        'highlight': (234, 179, 8, 150),
        'valid_move': (16, 185, 129, 180)
    },
    'moderne': {
        'name': 'Sombre Moderne',
        'light_sq': (210, 215, 225),
        'dark_sq': (45, 55, 72),
        'border': (26, 32, 44),
        'highlight': (56, 189, 248, 150),
        'valid_move': (129, 140, 248, 180)
    }
}

class CheckersGUI:
    def __init__(self, test_mode=False):
        pygame.init()
        pygame.font.init()

        self.test_mode = test_mode
        if not test_mode:
            self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
            pygame.display.set_caption("Jeu de Dames Élite - Jeu avec IA & Multijoueur")
        else:
            self.screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.sound_mgr = get_sound_manager()

        # Fonts
        self.font_title = pygame.font.SysFont("Helvetica", 42, bold=True)
        self.font_subtitle = pygame.font.SysFont("Helvetica", 24, bold=True)
        self.font_main = pygame.font.SysFont("Helvetica", 18)
        self.font_small = pygame.font.SysFont("Helvetica", 14)

        # Settings
        self.game_mode = 'vs_ai' # 'vs_ai' or 'pvp'
        self.ai_difficulty = MEDIUM # EASY, MEDIUM, HARD
        self.ai_player_color = BLACK # Human is WHITE
        self.board_size = 10 # 10 or 8
        self.current_theme_key = 'bois_classic'

        # Game Engine & State
        self.game = CheckersGame(size=self.board_size)
        self.ai = CheckersAI(difficulty=self.ai_difficulty)

        # UI State
        self.state = 'menu' # 'menu', 'settings', 'game', 'game_over'
        self.selected_sq = None
        self.valid_moves = []
        self.animating_move = None
        self.anim_progress = 0.0

        # Offscreen Board Surfaces
        self.board_rect = pygame.Rect(40, 60, 640, 640)
        self.sq_size = self.board_rect.width // self.board_size

    def change_board_size(self, new_size):
        self.board_size = new_size
        self.sq_size = self.board_rect.width // self.board_size
        self.game = CheckersGame(size=self.board_size)
        self.selected_sq = None
        self.valid_moves = []

    def start_new_game(self):
        self.game = CheckersGame(size=self.board_size)
        self.ai = CheckersAI(difficulty=self.ai_difficulty)
        self.selected_sq = None
        self.valid_moves = []
        self.state = 'game'

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.state == 'menu':
                    self.handle_menu_click(pos)
                elif self.state == 'settings':
                    self.handle_settings_click(pos)
                elif self.state == 'game':
                    self.handle_game_click(pos)
                elif self.state == 'game_over':
                    self.handle_game_over_click(pos)

        return True

    # --- Click Handlers ---
    def handle_menu_click(self, pos):
        # Menu Buttons
        btn_vs_ai = pygame.Rect(362, 280, 300, 50)
        btn_pvp = pygame.Rect(362, 350, 300, 50)
        btn_settings = pygame.Rect(362, 420, 300, 50)
        btn_quit = pygame.Rect(362, 490, 300, 50)

        if btn_vs_ai.collidepoint(pos):
            self.sound_mgr.play('button')
            self.game_mode = 'vs_ai'
            self.start_new_game()
        elif btn_pvp.collidepoint(pos):
            self.sound_mgr.play('button')
            self.game_mode = 'pvp'
            self.start_new_game()
        elif btn_settings.collidepoint(pos):
            self.sound_mgr.play('button')
            self.state = 'settings'
        elif btn_quit.collidepoint(pos):
            self.sound_mgr.play('button')
            pygame.quit()
            sys.exit()

    def handle_settings_click(self, pos):
        # Back button
        btn_back = pygame.Rect(40, 40, 120, 40)
        if btn_back.collidepoint(pos):
            self.sound_mgr.play('button')
            self.state = 'menu'
            return

        # Board Size Buttons (8x8 vs 10x10)
        btn_8x8 = pygame.Rect(350, 200, 120, 40)
        btn_10x10 = pygame.Rect(490, 200, 120, 40)
        if btn_8x8.collidepoint(pos) and self.board_size != 8:
            self.sound_mgr.play('button')
            self.change_board_size(8)
        elif btn_10x10.collidepoint(pos) and self.board_size != 10:
            self.sound_mgr.play('button')
            self.change_board_size(10)

        # AI Difficulty Buttons
        btn_easy = pygame.Rect(320, 280, 110, 40)
        btn_med = pygame.Rect(445, 280, 110, 40)
        btn_hard = pygame.Rect(570, 280, 110, 40)
        if btn_easy.collidepoint(pos):
            self.sound_mgr.play('button')
            self.ai_difficulty = EASY
        elif btn_med.collidepoint(pos):
            self.sound_mgr.play('button')
            self.ai_difficulty = MEDIUM
        elif btn_hard.collidepoint(pos):
            self.sound_mgr.play('button')
            self.ai_difficulty = HARD

        # Sound Toggle
        btn_sound = pygame.Rect(350, 360, 200, 40)
        if btn_sound.collidepoint(pos):
            self.sound_mgr.toggle_sound()
            self.sound_mgr.play('button')

        # Theme Buttons
        btn_t1 = pygame.Rect(260, 440, 150, 40)
        btn_t2 = pygame.Rect(420, 440, 150, 40)
        btn_t3 = pygame.Rect(580, 440, 150, 40)
        if btn_t1.collidepoint(pos):
            self.sound_mgr.play('button')
            self.current_theme_key = 'bois_classic'
        elif btn_t2.collidepoint(pos):
            self.sound_mgr.play('button')
            self.current_theme_key = 'acajou'
        elif btn_t3.collidepoint(pos):
            self.sound_mgr.play('button')
            self.current_theme_key = 'moderne'

    def handle_game_click(self, pos):
        # Menu / HUD Buttons
        btn_menu = pygame.Rect(710, 660, 120, 40)
        btn_restart = pygame.Rect(850, 660, 120, 40)

        if btn_menu.collidepoint(pos):
            self.sound_mgr.play('button')
            self.state = 'menu'
            return
        if btn_restart.collidepoint(pos):
            self.sound_mgr.play('button')
            self.start_new_game()
            return

        # Ignore board clicks if AI turn or game over
        if self.game.game_over:
            return

        if self.game_mode == 'vs_ai' and self.game.turn == self.ai_player_color:
            return

        # Check Board Clicks
        bx, by, bw, bh = self.board_rect
        if bx <= pos[0] < bx + bw and by <= pos[1] < by + bh:
            c = (pos[0] - bx) // self.sq_size
            r = (pos[1] - by) // self.sq_size

            # If square selected, check if click is valid destination
            if self.selected_sq:
                matched_move = None
                for m in self.valid_moves:
                    if m.end == (r, c):
                        matched_move = m
                        break

                if matched_move:
                    sound_evt = self.game.make_move(matched_move)
                    if sound_evt:
                        self.sound_mgr.play(sound_evt)

                    self.selected_sq = None
                    self.valid_moves = []

                    if self.game.game_over:
                        self.sound_mgr.play('win')
                        self.state = 'game_over'
                    return

            # Select piece
            piece = self.game.get_piece(r, c)
            if piece and ((self.game.turn == WHITE and is_white(piece)) or (self.game.turn == BLACK and is_black(piece))):
                all_legal = self.game.get_all_legal_moves()
                piece_moves = [m for m in all_legal if m.start == (r, c)]
                if piece_moves:
                    self.selected_sq = (r, c)
                    self.valid_moves = piece_moves
                    self.sound_mgr.play('button')
                else:
                    self.selected_sq = None
                    self.valid_moves = []
            else:
                self.selected_sq = None
                self.valid_moves = []

    def handle_game_over_click(self, pos):
        btn_replay = pygame.Rect(362, 430, 140, 45)
        btn_main = pygame.Rect(522, 430, 140, 45)

        if btn_replay.collidepoint(pos):
            self.sound_mgr.play('button')
            self.start_new_game()
        elif btn_main.collidepoint(pos):
            self.sound_mgr.play('button')
            self.state = 'menu'

    def update_ai(self):
        if self.state == 'game' and not self.game.game_over:
            if self.game_mode == 'vs_ai' and self.game.turn == self.ai_player_color:
                # Slight delay for natural AI response feel
                pygame.time.delay(200)
                ai_move = self.ai.get_best_move(self.game)
                if ai_move:
                    sound_evt = self.game.make_move(ai_move)
                    if sound_evt:
                        self.sound_mgr.play(sound_evt)

                    if self.game.game_over:
                        self.sound_mgr.play('win')
                        self.state = 'game_over'

    # --- Rendering Functions ---
    def render(self):
        self.screen.fill(COLOR_BG)

        if self.state == 'menu':
            self.render_menu()
        elif self.state == 'settings':
            self.render_settings()
        elif self.state in ('game', 'game_over'):
            self.render_game()
            if self.state == 'game_over':
                self.render_game_over_overlay()

        if not self.test_mode:
            pygame.display.flip()

    def render_menu(self):
        # Title
        title = self.font_title.render("JEU DE DAMES ÉLITE", True, COLOR_GOLD)
        sub = self.font_subtitle.render("Édition Réaliste Pygame", True, COLOR_TEXT_DIM)
        self.screen.blit(title, title.get_rect(center=(WIN_WIDTH // 2, 140)))
        self.screen.blit(sub, sub.get_rect(center=(WIN_WIDTH // 2, 195)))

        # Menu Buttons
        buttons = [
            ("1 Joueur (vs IA)", 280),
            ("2 Joueurs (Multijoueur Local)", 350),
            ("Paramètres & Options", 420),
            ("Quitter", 490)
        ]

        mx, my = pygame.mouse.get_pos()
        for label, y in buttons:
            rect = pygame.Rect(362, y, 300, 50)
            is_hover = rect.collidepoint((mx, my))
            bg_color = (60, 50, 40) if is_hover else (40, 35, 30)
            border_color = COLOR_GOLD if is_hover else (100, 90, 80)

            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=8)

            txt = self.font_main.render(label, True, COLOR_TEXT)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

    def render_settings(self):
        title = self.font_title.render("PARAMÈTRES DU JEU", True, COLOR_GOLD)
        self.screen.blit(title, title.get_rect(center=(WIN_WIDTH // 2, 80)))

        # Back Button
        btn_back = pygame.Rect(40, 40, 120, 40)
        pygame.draw.rect(self.screen, (50, 45, 40), btn_back, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_GOLD, btn_back, width=1, border_radius=6)
        bt = self.font_main.render("< Retour", True, COLOR_TEXT)
        self.screen.blit(bt, bt.get_rect(center=btn_back.center))

        # 1. Taille du Damier
        t1 = self.font_subtitle.render("Taille du Damier :", True, COLOR_TEXT)
        self.screen.blit(t1, (160, 205))

        b8 = pygame.Rect(350, 200, 120, 40)
        b10 = pygame.Rect(490, 200, 120, 40)
        for rect, sz, label in [(b8, 8, "8 x 8"), (b10, 10, "10 x 10")]:
            is_sel = (self.board_size == sz)
            col = COLOR_GOLD if is_sel else (50, 45, 40)
            txt_col = (0, 0, 0) if is_sel else COLOR_TEXT
            pygame.draw.rect(self.screen, col, rect, border_radius=6)
            txt = self.font_main.render(label, True, txt_col)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        # 2. Difficulté IA
        t2 = self.font_subtitle.render("Difficulté IA :", True, COLOR_TEXT)
        self.screen.blit(t2, (160, 285))

        b_easy = pygame.Rect(320, 280, 110, 40)
        b_med = pygame.Rect(445, 280, 110, 40)
        b_hard = pygame.Rect(570, 280, 110, 40)
        for rect, diff, label in [(b_easy, EASY, "Facile"), (b_med, MEDIUM, "Moyen"), (b_hard, HARD, "Difficile")]:
            is_sel = (self.ai_difficulty == diff)
            col = COLOR_GOLD if is_sel else (50, 45, 40)
            txt_col = (0, 0, 0) if is_sel else COLOR_TEXT
            pygame.draw.rect(self.screen, col, rect, border_radius=6)
            txt = self.font_main.render(label, True, txt_col)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        # 3. Son / Effets Sonores
        t3 = self.font_subtitle.render("Effets Sonores :", True, COLOR_TEXT)
        self.screen.blit(t3, (160, 365))
        b_sound = pygame.Rect(350, 360, 200, 40)
        s_label = "Activité (ON)" if self.sound_mgr.enabled else "Muet (OFF)"
        s_col = COLOR_SUCCESS if self.sound_mgr.enabled else COLOR_DANGER
        pygame.draw.rect(self.screen, s_col, b_sound, border_radius=6)
        stxt = self.font_main.render(s_label, True, COLOR_TEXT)
        self.screen.blit(stxt, stxt.get_rect(center=b_sound.center))

        # 4. Thème Visuel
        t4 = self.font_subtitle.render("Thème Visuel :", True, COLOR_TEXT)
        self.screen.blit(t4, (160, 445))

        b_t1 = pygame.Rect(260, 440, 150, 40)
        b_t2 = pygame.Rect(420, 440, 150, 40)
        b_t3 = pygame.Rect(580, 440, 150, 40)
        for rect, key, label in [(b_t1, 'bois_classic', "Bois Classique"), (b_t2, 'acajou', "Acajou Luxe"), (b_t3, 'moderne', "Sombre Moderne")]:
            is_sel = (self.current_theme_key == key)
            col = COLOR_GOLD if is_sel else (50, 45, 40)
            txt_col = (0, 0, 0) if is_sel else COLOR_TEXT
            pygame.draw.rect(self.screen, col, rect, border_radius=6)
            txt = self.font_small.render(label, True, txt_col)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

    def render_game(self):
        theme = THEMES[self.current_theme_key]
        bx, by, bw, bh = self.board_rect

        # Draw Bezel / Wooden Frame
        frame_rect = pygame.Rect(bx - 16, by - 16, bw + 32, bh + 32)
        pygame.draw.rect(self.screen, theme['border'], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_GOLD, frame_rect, width=2, border_radius=12)

        # Draw Squares
        for r in range(self.board_size):
            for c in range(self.board_size):
                sq_rect = pygame.Rect(bx + c * self.sq_size, by + r * self.sq_size, self.sq_size, self.sq_size)
                is_dark = (r + c) % 2 == 1
                color = theme['dark_sq'] if is_dark else theme['light_sq']
                pygame.draw.rect(self.screen, color, sq_rect)

        # Highlight Selected Square
        if self.selected_sq:
            sr, sc = self.selected_sq
            s_rect = pygame.Rect(bx + sc * self.sq_size, by + sr * self.sq_size, self.sq_size, self.sq_size)
            s_surf = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            s_surf.fill(theme['highlight'])
            self.screen.blit(s_surf, s_rect.topleft)

        # Highlight Valid Destination Moves
        for move in self.valid_moves:
            er, ec = move.end
            m_rect = pygame.Rect(bx + ec * self.sq_size, by + er * self.sq_size, self.sq_size, self.sq_size)
            m_surf = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            m_surf.fill(theme['valid_move'])
            self.screen.blit(m_surf, m_rect.topleft)
            # Center indicator dot
            center = (bx + ec * self.sq_size + self.sq_size // 2, by + er * self.sq_size + self.sq_size // 2)
            pygame.draw.circle(self.screen, (255, 255, 255), center, self.sq_size // 6)

        # Draw Pieces
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.game.get_piece(r, c)
                if piece:
                    cx = bx + c * self.sq_size + self.sq_size // 2
                    cy = by + r * self.sq_size + self.sq_size // 2
                    self.render_piece(cx, cy, piece)

        # Draw HUD Panel (Right Side)
        self.render_hud()

    def render_piece(self, cx, cy, piece):
        radius = int(self.sq_size * 0.4)

        # Color definitions
        if is_white(piece):
            main_color = (245, 240, 230)
            bevel_color = (200, 190, 175)
            shadow_color = (130, 120, 110)
        else:
            main_color = (40, 40, 40)
            bevel_color = (70, 70, 70)
            shadow_color = (15, 15, 15)

        # Drop shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 100), (cx + 3, cy + 4), radius)
        # Outer bevel ring
        pygame.draw.circle(self.screen, shadow_color, (cx, cy), radius)
        pygame.draw.circle(self.screen, bevel_color, (cx, cy), int(radius * 0.95))
        # Inner body
        pygame.draw.circle(self.screen, main_color, (cx, cy), int(radius * 0.82))
        # Concentric inner ring
        pygame.draw.circle(self.screen, shadow_color, (cx, cy), int(radius * 0.55), width=2)

        # Crown symbol if King
        if is_king(piece):
            crown_pts = [
                (cx - radius * 0.4, cy + radius * 0.25),
                (cx - radius * 0.4, cy - radius * 0.2),
                (cx - radius * 0.15, cy),
                (cx, cy - radius * 0.35),
                (cx + radius * 0.15, cy),
                (cx + radius * 0.4, cy - radius * 0.2),
                (cx + radius * 0.4, cy + radius * 0.25)
            ]
            pygame.draw.polygon(self.screen, COLOR_GOLD, crown_pts)
            pygame.draw.polygon(self.screen, (180, 130, 0), crown_pts, width=1)

    def render_hud(self):
        panel_x = 710
        panel_y = 60
        panel_w = 270

        # Current Turn Display
        turn_str = "Blanc (Joueur)" if self.game.turn == WHITE else ("Noir (IA)" if self.game_mode == 'vs_ai' else "Noir (Joueur 2)")
        t_color = (240, 240, 240) if self.game.turn == WHITE else (180, 180, 180)

        turn_lbl = self.font_subtitle.render("TOUR ACTUEL", True, COLOR_GOLD)
        turn_val = self.font_main.render(turn_str, True, t_color)
        self.screen.blit(turn_lbl, (panel_x, panel_y))
        self.screen.blit(turn_val, (panel_x, panel_y + 30))

        # Captured Pieces Counter
        cap_lbl = self.font_subtitle.render("PIÈCES CAPTURÉES", True, COLOR_GOLD)
        self.screen.blit(cap_lbl, (panel_x, panel_y + 90))

        c_w_txt = self.font_main.render(f"Blancs capturés: {self.game.captured_white}", True, COLOR_TEXT)
        c_b_txt = self.font_main.render(f"Noirs capturés: {self.game.captured_black}", True, COLOR_TEXT)
        self.screen.blit(c_w_txt, (panel_x, panel_y + 125))
        self.screen.blit(c_b_txt, (panel_x, panel_y + 155))

        # Mode & Difficulty Info
        mode_txt = "Mode: vs IA" if self.game_mode == 'vs_ai' else "Mode: 2 Joueurs"
        diff_txt = f"Difficulté: {self.ai_difficulty.capitalize()}" if self.game_mode == 'vs_ai' else ""
        self.screen.blit(self.font_main.render(mode_txt, True, COLOR_TEXT_DIM), (panel_x, panel_y + 210))
        if diff_txt:
            self.screen.blit(self.font_main.render(diff_txt, True, COLOR_TEXT_DIM), (panel_x, panel_y + 235))

        # Action Buttons
        btn_menu = pygame.Rect(panel_x, 660, 120, 40)
        btn_restart = pygame.Rect(panel_x + 140, 660, 120, 40)

        pygame.draw.rect(self.screen, (50, 45, 40), btn_menu, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_GOLD, btn_menu, width=1, border_radius=6)
        mtxt = self.font_main.render("Menu", True, COLOR_TEXT)
        self.screen.blit(mtxt, mtxt.get_rect(center=btn_menu.center))

        pygame.draw.rect(self.screen, (50, 45, 40), btn_restart, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_GOLD, btn_restart, width=1, border_radius=6)
        rtxt = self.font_main.render("Recommencer", True, COLOR_TEXT)
        self.screen.blit(rtxt, rtxt.get_rect(center=btn_restart.center))

    def render_game_over_overlay(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Modal Box
        box = pygame.Rect(262, 230, 500, 280)
        pygame.draw.rect(self.screen, (35, 30, 25), box, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_GOLD, box, width=2, border_radius=12)

        winner_str = "Victoire des Blancs !" if self.game.winner == WHITE else "Victoire des Noirs !"
        t = self.font_title.render("FIN DE PARTIE", True, COLOR_GOLD)
        w = self.font_subtitle.render(winner_str, True, COLOR_TEXT)

        self.screen.blit(t, t.get_rect(center=(WIN_WIDTH // 2, 290)))
        self.screen.blit(w, w.get_rect(center=(WIN_WIDTH // 2, 350)))

        # Buttons
        btn_replay = pygame.Rect(362, 430, 140, 45)
        btn_main = pygame.Rect(522, 430, 140, 45)

        pygame.draw.rect(self.screen, COLOR_SUCCESS, btn_replay, border_radius=8)
        rpt = self.font_main.render("Rejouer", True, COLOR_TEXT)
        self.screen.blit(rpt, rpt.get_rect(center=btn_replay.center))

        pygame.draw.rect(self.screen, (70, 60, 50), btn_main, border_radius=8)
        mnt = self.font_main.render("Menu Principal", True, COLOR_TEXT)
        self.screen.blit(mnt, mnt.get_rect(center=btn_main.center))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_ai()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Jeu de Dames Élite Pygame")
    parser.add_argument('--test-run', action='store_true', help="Run headless test iteration and exit")
    args = parser.parse_args()

    gui = CheckersGUI(test_mode=args.test_run)

    if args.test_run:
        print("[CheckersGUI] Executing headless verification test run...")
        gui.start_new_game()
        gui.render()
        gui.update_ai()
        print("[CheckersGUI] Verification test run successfully completed!")
        sys.exit(0)
    else:
        gui.run()
