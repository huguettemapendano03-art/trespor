# main.py
import sys
import os
import argparse
import pygame

from checkers.constants import (
    WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
)
from checkers.game import Game, MODE_TWO_PLAYER, MODE_AI
from checkers.ui import UI, HEADER_HEIGHT, BOARD_OFFSET_Y, WINDOW_WIDTH, WINDOW_HEIGHT
from checkers.ai import minimax, DIFFICULTY_DEPTH

FPS = 60

def get_row_col_from_mouse(pos):
    x, y = pos
    if y < BOARD_OFFSET_Y:
        return None, None
    row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    parser = argparse.ArgumentParser(description="Jeu de Dames Premium Pygame")
    parser.add_argument("--test-run", action="store_true", help="Execution de test headless")
    args = parser.parse_args()

    if args.test_run or os.environ.get("SDL_VIDEODRIVER") == "dummy":
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Jeu de Dames - Premium Python")
    clock = pygame.time.Clock()

    ui = UI(win)

    # App States: "MENU", "PLAYING", "GAME_OVER"
    app_state = "MENU"
    selected_mode = MODE_TWO_PLAYER
    selected_diff = "MEDIUM"

    game = None
    restart_btn = None

    run = True
    frames_count = 0

    while run:
        clock.tick(FPS)
        frames_count += 1

        if app_state == "MENU":
            buttons = ui.draw_menu(selected_mode, selected_diff)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mpos = event.pos
                    if buttons["2P"].collidepoint(mpos):
                        selected_mode = MODE_TWO_PLAYER
                    elif buttons["AI"].collidepoint(mpos):
                        selected_mode = MODE_AI
                    elif selected_mode == MODE_AI and buttons["EASY"].collidepoint(mpos):
                        selected_diff = "EASY"
                    elif selected_mode == MODE_AI and buttons["MEDIUM"].collidepoint(mpos):
                        selected_diff = "MEDIUM"
                    elif selected_mode == MODE_AI and buttons["HARD"].collidepoint(mpos):
                        selected_diff = "HARD"
                    elif buttons["START"].collidepoint(mpos):
                        game = Game(mode=selected_mode, ai_difficulty=selected_diff)
                        app_state = "PLAYING"

        elif app_state in ("PLAYING", "GAME_OVER"):
            # AI Move check
            if app_state == "PLAYING" and game.mode == MODE_AI and game.turn == WHITE and game.winner is None:
                pygame.time.delay(300) # Small delay for natural feel
                depth = DIFFICULTY_DEPTH.get(game.ai_difficulty, 3)
                _, new_board = minimax(game.get_board(), depth, float('-inf'), float('inf'), True, game)
                if new_board:
                    game.ai_move(new_board)
                else:
                    game.winner = RED

            # Check if game over reached
            if game.winner is not None:
                app_state = "GAME_OVER"

            # Draw Game Frame
            ui.draw_board()
            ui.draw_pieces(game.get_board())
            ui.draw_highlights(game)
            ui.draw_header(game)

            if app_state == "GAME_OVER":
                restart_btn = ui.draw_game_over(game.winner, game.mode)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                        app_state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        app_state = "MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if app_state == "GAME_OVER" and restart_btn and restart_btn.collidepoint(event.pos):
                        game.reset()
                        app_state = "PLAYING"
                    elif app_state == "PLAYING" and (game.mode == MODE_TWO_PLAYER or game.turn == RED):
                        row, col = get_row_col_from_mouse(event.pos)
                        if row is not None and col is not None:
                            game.select(row, col)

        # In test-run mode, simulate starting a game and making moves then exiting
        if args.test_run:
            if frames_count == 2 and app_state == "MENU":
                game = Game(mode=MODE_AI, ai_difficulty="EASY")
                app_state = "PLAYING"
            elif frames_count == 5 and app_state == "PLAYING":
                # Make a valid move
                game.select(2, 1)
                game.select(3, 0)
            elif frames_count == 10:
                # Save visual test frame screenshot
                pygame.image.save(win, "checkers_screenshot.png")
                run = False

    pygame.quit()

if __name__ == "__main__":
    main()
