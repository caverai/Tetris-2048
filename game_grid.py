import lib.stddraw as stddraw
# Import stddraw for drawing graphics on the screen.
from lib.color import Color
# Import the Color class to define colors for tiles and backgrounds.
from point import Point
# Point class is used to manage positions (x, y) cleanly.
import numpy as np
# numpy (np) is imported to manage efficient 2D arrays.
import copy as cp
# copy (cp) is imported to duplicate objects if necessary.

class GameGrid:
# We define the GameGrid class, which will manage the entire game board, the tiles, and game logic like merging and clearing rows.
    def __init__(self, grid_h, grid_w):
        # The constructor initializes a new game grid with a given height and width.
        self.grid_height = grid_h
        self.grid_width = grid_w
        # Save the dimensions of the grid.
        self.tile_matrix = np.full((grid_h, grid_w), None)
        # Create a 2D matrix filled with None, meaning every cell starts empty.
        self.current_tetromino = None
        # Placeholder for the currently falling Tetromino piece.
        self.game_over = False
        # A flag to indicate if the game has ended.
        self.score = 0
        # Initialize the player’s score to zero.
        self.empty_cell_color = Color(42, 69, 99)
        self.line_color = Color(0, 100, 200)
        self.boundary_color = Color(0, 100, 200)
        # Define colors for empty spaces, grid lines, and boundaries.
        self.line_thickness = 0.002
        self.box_thickness = 10 * self.line_thickness
        # Set visual thickness settings for drawing.
        self.win = False
        # A flag to indicate if the player has reached the 2048 tile.

    def update_grid(self, tiles_to_lock, blc_pos):
    # This method locks the tiles from a Tetromino into the game board once it lands.
        for r in range(len(tiles_to_lock)):
            for c in range(len(tiles_to_lock[0])):
            # Iterate over each tile inside the falling Tetromino.
                tile = tiles_to_lock[r][c]
                if tile is None:
                    continue
                # Skip empty cells.
                x = blc_pos.x + c
                y = blc_pos.y + (len(tiles_to_lock) - 1) - r
                # Calculate the position of each tile relative to the main grid.
                if y >= self.grid_height:
                    self.game_over = True
                    return True
                # If the tile tries to go above the top, it’s game over.
                self.tile_matrix[y][x] = tile
                # Otherwise, place the tile into the main grid.

        # Now, one by one we use the methods below to
        self._cascade_merge()
        # Merge identical tiles vertically.
        self._settle_floating()
        # Settle floating tiles downward.
        self._clear_rows()
        # Clear any full rows.
        self._settle_floating()
        # Settle again in case clearing created new floating tiles.

        return self.game_over
        # Return whether the game ended.

    def _cascade_merge(self):
    # Merge identical tiles vertically over and over until no more merges are possible.
        merged = True
        while merged:
        # Keep looping until no merges happen.
            merged = False
            for x in range(self.grid_width):
                y = 0
                while y < self.grid_height - 1:
                # Scan the grid bottom-up, column-by-column.
                    t1 = self.tile_matrix[y][x]
                    t2 = self.tile_matrix[y + 1][x]
                    # t1 is the tile above, t2 is below.
                    if t1 and t2 and t1.number == t2.number:
                    # If both tiles exist and have the same number:
                        t1.double()
                        self.score += t1.number
                        if t1.number == 2048:
                            self.win = True
                        self.tile_matrix[y + 1][x] = None
                        merged = True
                        # Double the tile value, add to score, mark win if 2048 is reached, delete the lower tile, and keep merging.
                    else:
                        y += 1
                    # Move upward if no merge.
            if merged:
                self._settle_floating()
            # If anything merged, settle again.
            
    def _settle_floating(self):
    # This method makes unsupported tiles fall downward until they land.
        while True:
            connected = self._connected_to_bottom()
            moved = False
            # Find all tiles connected to the bottom.
            for y in range(1, self.grid_height):
                for x in range(self.grid_width):
                # Check every tile (except bottom row).
                    tile = self.tile_matrix[y][x]
                    if tile is None or connected[y][x]:
                        continue
                    # Skip empty or already-supported tiles.
                    if self.tile_matrix[y - 1][x] is None:
                        self.tile_matrix[y - 1][x] = tile
                        self.tile_matrix[y][x] = None
                        moved = True
                    # If below is empty, move the tile down by one.
            if not moved:
                break
            # Stop when no more tiles fall.
            
    def _connected_to_bottom(self):
    # This method finds which tiles are supported by the ground or through a chain of connected tiles.
        visited = np.full(self.tile_matrix.shape, False)
        stack = [(0, x) for x in range(self.grid_width)
                 if self.tile_matrix[0][x] is not None]
        # Start from non-empty tiles at the bottom row.
        while stack:
            y, x = stack.pop()
            if visited[y][x]:
                continue
            visited[y][x] = True
            # Visit tiles and mark them as connected.
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.grid_height and 0 <= nx < self.grid_width \
                        and self.tile_matrix[ny][nx] is not None \
                        and not visited[ny][nx]:
                    stack.append((ny, nx))
                    # Explore all 4 directions.
        return visited
        # Return the map of connected tiles.

    def _collect_floating(self):
    # A method to Delete any tiles that are still floating after falling.
        visited = np.full(self.tile_matrix.shape, False)
        stack = [(0, x) for x in range(self.grid_width)]
        # Start flood-fill from every position on the bottom row.
        while stack:
            y, x = stack.pop()
            if y < 0 or y >= self.grid_height or x < 0 or x >= self.grid_width:
                continue
            # If the popped coordinate is out of bounds, skip.
            if visited[y][x] or self.tile_matrix[y][x] is None:
                continue
            # If already visited or empty tile, skip.
            visited[y][x] = True
            stack.extend([(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)])
            # Mark reachable tiles.

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.tile_matrix[y][x] is not None and not visited[y][x]:
                    self.score += self.tile_matrix[y][x].number
                    self.tile_matrix[y][x] = None
        # And for any tile not visited that is floating, we delete it and add its number to the score

    # clear any row that’s completely filled
    def _clear_rows(self):
        write_row = 0
        for read_row in range(self.grid_height):
            if None not in self.tile_matrix[read_row]:
                self.score += sum(tile.number for tile in self.tile_matrix[read_row])
                continue
            if write_row != read_row:
                self.tile_matrix[write_row] = self.tile_matrix[read_row]
            write_row += 1

        # blank the rows that were cleared
        for y in range(write_row, self.grid_height):
            self.tile_matrix[y] = np.full(self.grid_width, None)

    def display(self):
    # A method to draw everything, which includes background, grid, tetromino, and boundaries.
        stddraw.clear(self.empty_cell_color)
        self.draw_grid()
        if self.current_tetromino is not None:
            self.current_tetromino.draw()
        self.draw_boundaries()
        stddraw.show(250)

    def draw_grid(self):
    # A method to draw each tile and grid lines.
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.tile_matrix[row][col] is not None:
                    self.tile_matrix[row][col].draw(Point(col, row))
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()

    def draw_boundaries(self):
    # A method to draw a thick rectangle around the game area.
        stddraw.setPenColor(self.boundary_color)
        stddraw.setPenRadius(self.box_thickness)
        stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    def is_occupied(self, row, col):
    # A method to check if a specific grid cell is occupied.
        if not self.is_inside(row, col):
            return False
        return self.tile_matrix[row][col] is not None

    def is_inside(self, row, col):
    # A method to check if a given position is inside the bounds of the grid.
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width
