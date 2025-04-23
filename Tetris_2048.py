################################################################################
#                                                                              #
# The main program of Tetris 2048 Base Code                                    #
#                                                                              #
################################################################################

import lib.stddraw as stddraw  # for creating an animation with user interactions
from lib.picture import Picture  # used for displaying an image on the game menu
from lib.color import Color  # used for coloring the game menu
import os  # the os module is used for file and directory operations
from game_grid import GameGrid  # the class for modeling the game grid
from tetromino import Tetromino  # the class for modeling the tetrominoes
import random  # used for creating tetrominoes with random types (shapes)
import time

DIFFICULTIES = {
    "Easy":     0.75,
    "Normal":   0.40,
    "Hard":     0.15,
    "Lunatic":  0.05,
}
FPS        = 60
FRAME_MS   = int(1000 / FPS)


# The main function where this program starts execution
def play_one_game(fall_delay, grid_h=20, grid_w_main=12):
    right_panel_w = 6
    grid_w_total = grid_w_main + right_panel_w
    
    stddraw.setXscale(-0.5, grid_w_total-0.5)
    stddraw.setYscale(-0.5, grid_h-0.5)

    Tetromino.grid_height = grid_h
    Tetromino.grid_width  = grid_w_main
    grid = GameGrid(grid_h, grid_w_main)

    next_tetromino   = create_tetromino()
    current          = next_tetromino
    next_tetromino   = create_tetromino()
    grid.current_tetromino = current

    last_fall = time.time()
    paused    = False

    while True:
        # — INPUT — ---------------------------------------------------
        if stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == "p":
                paused = not paused
            elif paused and key == "m":
                return "menu"             # back to menu
            elif paused:
                pass                      # ignore other keys
            elif key in ("left", "right", "down"):
                current.move(key, grid)
            elif key == "up":
                current.move("rotate", grid)
            elif key == "space":
                while current.move("down", grid): pass
            stddraw.clearKeysTyped()

        if paused:
            draw_frame(grid, next_tetromino)
            draw_pause(grid_w_total, grid_h)
            stddraw.show(FRAME_MS)
            continue

        # — GRAVITY — -------------------------------------------------
        if time.time() - last_fall >= fall_delay:
            if not current.move("down", grid):
                tiles, pos = current.get_min_bounded_tile_matrix(True)
                if grid.update_grid(tiles, pos):
                    break
                current, next_tetromino = next_tetromino, create_tetromino()
                grid.current_tetromino = current
            last_fall = time.time()
        if grid.win:
            break
        # — RENDER — --------------------------------------------------
        draw_frame(grid, next_tetromino)
        stddraw.show(FRAME_MS)

    # — GAME-OVER LOOP — ---------------------------------------------
    while True:
        draw_frame(grid, next_tetromino)
        draw_game_over(grid_w_total, grid_h, grid.win)
        stddraw.show(FRAME_MS)
        if stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            stddraw.clearKeysTyped()
            if key == "m":
                return "menu"
def draw_pause(grid_w_total, grid_h):
    stddraw.setPenColor(Color(255, 255, 0))
    stddraw.boldText(grid_w_total/2, grid_h/2, "PAUSED  (P=res,  M=menu)")
def draw_game_over(grid_w_total, grid_h, win):
    msg = "YOU WIN!" if win else "GAME OVER"
    stddraw.setPenColor(Color(0, 255, 0))
    stddraw.boldText(grid_w_total/2, grid_h/2 + 1, msg)
    stddraw.setFontSize(25)
    stddraw.boldText(grid_w_total/2, grid_h/2 - 1, "Press M for menu")
# A function for creating random shaped tetrominoes to enter the game grid
def create_tetromino():
    tetromino_types = ['I', 'O', 'Z', 'J', 'L', 'S', 'T']
    return Tetromino(random.choice(tetromino_types))

# A function for displaying a simple menu before starting the game
# ---------------------------------------------------------
def show_menu(grid_h, grid_w_total):
    if not stddraw._windowCreated:          # only first time
        stddraw.setCanvasSize(40*grid_h, 40*grid_w_total)
    stddraw.setXscale(-0.5, grid_w_total-0.5)
    stddraw.setYscale(-0.5, grid_h-0.5)


    # ----- static drawing -------------------------------------------------
    stddraw.clear(Color(42, 69, 99))
    stddraw.setFontFamily("Arial"); stddraw.setFontSize(32)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.boldText(grid_w_total/2, grid_h - 3, "TETRIS 2048")

    btn_w, btn_h = 6, 1.4
    btn_y0 = grid_h/2 + 2
    buttons = []
    for i, diff in enumerate(DIFFICULTIES.keys()):
        x0 = (grid_w_total - btn_w)/2
        y0 = btn_y0 - i*2.0
        buttons.append((diff, x0, y0, btn_w, btn_h))
        stddraw.setPenColor(Color(25, 255, 228))
        stddraw.filledRectangle(x0, y0, btn_w, btn_h)
        stddraw.setPenColor(Color(31, 160, 239))
        stddraw.boldText(x0 + btn_w/2, y0 + btn_h/2, diff)

    stddraw.show(10)    # paint once

    # ----- wait for left-click -------------------------------------------
    while True:

        if stddraw.mousePressed():                  # public API call

            ux = stddraw.mouseX()                   # user-space coords
            uy = stddraw.mouseY()
            # debounce – wait until button released so we don't
            # register the same click repeatedly
            while stddraw.mousePressed():

                stddraw.show(10)

            for diff, x0, y0, bw, bh in buttons:
                if x0 <= ux <= x0 + bw and y0 <= uy <= y0 + bh:
                    return diff
        stddraw.show(10)    # small delay & event pump


def draw_frame(grid, next_piece):
    stddraw.clear(grid.empty_cell_color)
    grid.draw_grid()
    if grid.current_tetromino:
        grid.current_tetromino.draw()
    grid.draw_boundaries()

    # next piece preview
    ox, oy = grid.grid_width + 2, grid.grid_height - 5
    stddraw.setPenColor(Color(200, 200, 200))
    stddraw.rectangle(ox - 1.5 , oy - 1, 4, 5)
    next_piece.draw(preview=True, offset_x=ox-0.5, offset_y=oy),
    

    # score text
    stddraw.setFontFamily("Arial"); stddraw.setFontSize(20)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.boldText(grid.grid_width + 2.5, oy - 12,
                 f"SCORE: {grid.score}")
    
    stddraw.text(grid.grid_width + 2.5, oy - 1.3, "Next Piece")
    stddraw.text(grid.grid_width + 2.5, oy - 5, "P for Pause")
    stddraw.text(grid.grid_width + 2.5, oy - 4, "Space for Hard Drop")
    stddraw.text(grid.grid_width + 2.5, oy - 3, "Up for Rotate")


# start() function is specified as the entry point (main function) from which
# the program starts execution
if __name__ == "__main__":
    grid_h, grid_w_main = 20, 12
    right_panel_w = 6
    grid_w_total = grid_w_main + right_panel_w

    while True:
        diff = show_menu(grid_h, grid_w_total)  # blocks until click
        result = play_one_game(DIFFICULTIES[diff], grid_h, grid_w_main)
        # otherwise loop back to menu
