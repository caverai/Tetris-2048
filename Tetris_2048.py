import lib.stddraw as stddraw  # for creating an animation with user interactions
from lib.picture import Picture  # used for displaying an image on the game menu
from lib.color import Color  # used for coloring the game menu
import os  # the os module is used for file and directory operations
from game_grid import GameGrid  # the class for modeling the game grid
from tetromino import Tetromino  # the class for modeling the tetrominoes
import random  # used for creating tetrominoes with random types (shapes)
import time  # used for timing operations like tracking tetromino falls

DIFFICULTIES = {
    "Easy":     0.75,  # Slower fall speed for easier gameplay
    "Normal":   0.40,  # Medium fall speed for balanced gameplay
    "Hard":     0.15,  # Fast fall speed for challenging gameplay
    "Lunatic":  0.05,  # Very fast fall speed for extreme difficulty
}
FPS        = 60  # Frames per second for smooth animation
FRAME_MS   = int(1000 / FPS)  # Milliseconds per frame


# The main function where this program starts execution
def play_one_game(fall_delay, grid_h=20, grid_w_main=12):
    # Set up the game area with a main grid and a side panel
    right_panel_w = 6  # Width of the panel showing next piece and score
    grid_w_total = grid_w_main + right_panel_w  # Total width of the game window
    
    # Set the coordinate scale for drawing
    stddraw.setXscale(-0.5, grid_w_total-0.5)
    stddraw.setYscale(-0.5, grid_h-0.5)

    # Initialize the Tetromino class with grid dimensions
    Tetromino.grid_height = grid_h
    Tetromino.grid_width  = grid_w_main
    grid = GameGrid(grid_h, grid_w_main)  # Create the game grid

    # Create initial tetrominoes
    next_tetromino   = create_tetromino()  # Generate the next piece
    current          = next_tetromino  # Set the current falling piece
    next_tetromino   = create_tetromino()  # Generate another piece for "next"
    grid.current_tetromino = current  # Assign current tetromino to the grid

    last_fall = time.time()  # Track time of last tetromino fall
    paused    = False  # Game starts unpaused

    # Main game loop
    while True:
        # Handle user input
        if stddraw.hasNextKeyTyped():  # Check if any key is pressed
            key = stddraw.nextKeyTyped()  # Get the key
            if key == "p":  # Toggle pause
                paused = not paused
            elif paused and key == "m":  # Return to menu when paused
                return "menu"             # back to menu
            elif paused:
                pass                      # ignore other keys while paused
            elif key in ("left", "right", "down"):  # Handle movement keys
                current.move(key, grid)
            elif key == "up":  # Handle rotation
                current.move("rotate", grid)
            elif key == "space":  # Hard drop - move down until collision
                while current.move("down", grid): pass
            stddraw.clearKeysTyped()  # Clear input buffer

        if paused:  # If game is paused
            draw_frame(grid, next_tetromino)  # Draw the current state
            draw_pause(grid_w_total, grid_h)  # Show pause message
            stddraw.show(FRAME_MS)  # Display frame and wait
            continue  # Skip the rest of the loop

        # Apply gravity to make pieces fall
        if time.time() - last_fall >= fall_delay:  # If it's time for piece to fall
            if not current.move("down", grid):  # Try to move down
                # If can't move down, handle piece locking
                tiles, pos = current.get_min_bounded_tile_matrix(True)  # Get minimal piece representation
                if grid.update_grid(tiles, pos):  # Lock piece and update grid
                    break  # Game over if update_grid returns True
                # Prepare the next piece
                current, next_tetromino = next_tetromino, create_tetromino()
                grid.current_tetromino = current
            last_fall = time.time()  # Reset the fall timer
        if grid.win:  # Check win condition
            break  # Exit game loop if won
            
        # Render game state
        draw_frame(grid, next_tetromino)  # Draw everything
        stddraw.show(FRAME_MS)  # Display frame and control timing

    # Game over loop
    while True:  # Loop until player chooses to go back to menu
        draw_frame(grid, next_tetromino)  # Draw final game state
        draw_game_over(grid_w_total, grid_h, grid.win)  # Show game over message
        stddraw.show(FRAME_MS)  # Display frame
        if stddraw.hasNextKeyTyped():  # Check for key press
            key = stddraw.nextKeyTyped()  # Get key
            stddraw.clearKeysTyped()  # Clear input buffer
            if key == "m":  # Return to menu
                return "menu"

# Draw pause message overlay
def draw_pause(grid_w_total, grid_h):
    # Display pause instructions in yellow text
    stddraw.setPenColor(Color(255, 255, 0))
    stddraw.boldText(grid_w_total/2, grid_h/2, "PAUSED  (P=res,  M=menu)")

# Draw game over/win message overlay
def draw_game_over(grid_w_total, grid_h, win):
    # Show appropriate message based on win status
    msg = "YOU WIN!" if win else "GAME OVER"
    stddraw.setPenColor(Color(0, 255, 0))
    stddraw.boldText(grid_w_total/2, grid_h/2 + 1, msg)
    stddraw.setFontSize(25)
    stddraw.boldText(grid_w_total/2, grid_h/2 - 1, "Press M for menu")

# A function for creating random shaped tetrominoes to enter the game grid
def create_tetromino():
    # Define all possible tetromino shapes
    tetromino_types = ['I', 'O', 'Z', 'J', 'L', 'S', 'T']
    # Return a tetromino of random shape
    return Tetromino(random.choice(tetromino_types))

# A function for displaying a simple menu before starting the game
def show_menu(grid_h, grid_w_total):
    # Set up the canvas only if it hasn't been created
    if not stddraw._windowCreated:          # only first time
        stddraw.setCanvasSize(40*grid_h, 40*grid_w_total)
    # Set coordinate system
    stddraw.setXscale(-0.5, grid_w_total-0.5)
    stddraw.setYscale(-0.5, grid_h-0.5)

    # Draw static menu elements
    stddraw.clear(Color(42, 69, 99))  # Set background color
    stddraw.setFontFamily("Arial"); stddraw.setFontSize(32)  # Set font properties
    stddraw.setPenColor(Color(255, 255, 255))  # Set text color to white
    stddraw.boldText(grid_w_total/2, grid_h - 3, "TETRIS 2048")  # Draw title
    
    # Display credits
    stddraw.boldText(grid_w_total/2, grid_h - 15, "Made by:")
    stddraw.boldText(grid_w_total/2, grid_h - 17, "Murat Kayra Pamukçu")
    stddraw.boldText(grid_w_total/2, grid_h - 18, "Başar Metin")
    stddraw.boldText(grid_w_total/2, grid_h - 19, "Necati Onur Yaman")

    # Define button dimensions and starting position
    btn_w, btn_h = 6, 1.4
    btn_y0 = grid_h/2 + 2
    buttons = []
    
    # Create difficulty buttons
    for i, diff in enumerate(DIFFICULTIES.keys()):
        x0 = (grid_w_total - btn_w)/2
        y0 = btn_y0 - i*2.0
        buttons.append((diff, x0, y0, btn_w, btn_h))  # Store button data
        stddraw.setPenColor(Color(25, 255, 228))  # Button fill color
        stddraw.filledRectangle(x0, y0, btn_w, btn_h)  # Draw button
        stddraw.setPenColor(Color(31, 160, 239))  # Button text color
        stddraw.boldText(x0 + btn_w/2, y0 + btn_h/2, diff)  # Draw button label

    stddraw.show(10)    # Display the menu

    # Wait for mouse click on a difficulty button
    while True:  # Loop until a valid selection is made
        if stddraw.mousePressed():  # Check for mouse press
            ux = stddraw.mouseX()  # Get X coordinate of mouse
            uy = stddraw.mouseY()  # Get Y coordinate of mouse
            # Wait until mouse button is released (debounce)
            while stddraw.mousePressed():
                stddraw.show(10)

            # Check if click was on a button
            for diff, x0, y0, bw, bh in buttons:
                if x0 <= ux <= x0 + bw and y0 <= uy <= y0 + bh:
                    return diff  # Return selected difficulty
        stddraw.show(10)    # Small delay and update events


# Function to draw the game frame including grid, current piece, next piece, and score
def draw_frame(grid, next_piece):
    stddraw.clear(grid.empty_cell_color)  # Clear screen with background color
    grid.draw_grid()  # Draw the game grid with locked tiles
    if grid.current_tetromino:  # Draw the current falling tetromino
        grid.current_tetromino.draw()
    grid.draw_boundaries()  # Draw grid boundaries

    # Define position for the next piece preview
    ox, oy = grid.grid_width + 2, grid.grid_height - 5
    stddraw.setPenColor(Color(200, 200, 200))  # Set color for preview box
    stddraw.rectangle(ox - 1.5 , oy - 1, 4, 5)  # Draw preview box
    next_piece.draw(preview=True, offset_x=ox-0.5, offset_y=oy)  # Draw next piece
    
    # Display score and controls
    stddraw.setFontFamily("Arial"); stddraw.setFontSize(20)
    stddraw.setPenColor(Color(255, 255, 255))  # Set text color to white
    stddraw.boldText(grid.grid_width + 2.5, oy - 12,
                 f"SCORE: {grid.score}")  # Show current score
    
    # Display control instructions
    stddraw.text(grid.grid_width + 2.5, oy - 1.3, "Next Piece")
    stddraw.text(grid.grid_width + 2.5, oy - 5, "P for Pause")
    stddraw.text(grid.grid_width + 2.5, oy - 4, "Space for Hard Drop")
    stddraw.text(grid.grid_width + 2.5, oy - 3, "Up for Rotate")


# Entry point of the program
if __name__ == "__main__":
    grid_h, grid_w_main = 20, 12  # Set default grid dimensions
    right_panel_w = 6  # Width of information panel
    grid_w_total = grid_w_main + right_panel_w  # Total width of game window

    # Main program loop - menu → game → menu
    while True:
        diff = show_menu(grid_h, grid_w_total)  # Show menu and get difficulty selection
        result = play_one_game(DIFFICULTIES[diff], grid_h, grid_w_main)  # Play game with selected difficulty
        # Loop back to menu when game ends
