from tile import Tile
# Import the Tile class to create and manage individual tiles in the tetromino
from point import Point
# Point class is used for managing positions (x, y) cleanly
import copy as cp
# copy (cp) is imported to create deep copies of objects when needed
import random
# random is imported for generating random tetromino positions
import numpy as np
# numpy (np) is imported for efficient matrix operations


class Tetromino:
# The Tetromino class is responsible for managing a falling Tetris piece
# including its tile matrix, movement, rotation, and locking into the game grid
    # These will be set by the main program before any Tetromino is created
    grid_height, grid_width = None, None

    # clockwise rotation matrix helper
    @staticmethod
    def _rot90(mat):
        # A helper method that rotates a matrix 90 degrees clockwise
        return np.rot90(mat, k=3)   # 3×90° = -90° → clockwise

    def __init__(self, shape: str):
        # The constructor initializes a new Tetromino with a specific shape
        self.type = shape.upper()
        # Store the type of tetromino

        # every piece fits inside an N×N square
        self.tile_matrix, n = self._make_tiles(self.type)
        # Create the matrix of tiles based on the tetromino type

        # spawn above the grid at a random x so the piece body is inside
        self.bottom_left_cell = Point(
            (Tetromino.grid_width - n)//2,
            Tetromino.grid_height - 1
        )
        # Position the tetromino at the top of the grid, centered horizontally

    # build the initial orientation & tile objects
    def _make_tiles(self, t):
        # This method creates the initial tile matrix for a given tetromino type
        occ = []
        if t == 'I':
            n = 4
            occ = [(1, i) for i in range(4)]
        elif t == 'O':
            n = 2
            occ = [(0, 0), (1, 0), (0, 1), (1, 1)]
        elif t == 'Z':
            n = 3
            occ = [(0, 1), (1, 1), (1, 2), (2, 2)]
        elif t == 'S':
            n = 3
            occ = [(1, 1), (2, 1), (0, 2), (1, 2)]
        elif t == 'T':
            n = 3
            occ = [(0, 1), (1, 1), (2, 1), (1, 2)]
        elif t == 'L':
            n = 3
            occ = [(2, 0), (0, 1), (1, 1), (2, 1)]
        elif t == 'J':
            n = 3
            occ = [(0, 0), (0, 1), (1, 1), (2, 1)]
        else:
            raise ValueError("Unknown tetromino type")
            # Raise an error if the tetromino type is invalid

        m = np.full((n, n), None)
        # Create an empty n×n matrix filled with None
        for c, r in occ:
            m[r][c] = Tile()
            # Place Tile objects at the specified positions to form the tetromino shape
        return m, n
        # Return the tile matrix and its dimension

    def get_cell_position(self, row, col):
        # Convert matrix coordinates to actual grid coordinates
        n = len(self.tile_matrix)
        return Point(
            self.bottom_left_cell.x + col,
            self.bottom_left_cell.y + (n - 1) - row
        )
        # Takes into account the tetromino's position and orientation

    def get_min_bounded_tile_matrix(self, return_position=False):
        # Get a minimal bounded version of the tile matrix
        n = len(self.tile_matrix)
        rows, cols = np.where(self.tile_matrix != None)
        min_r, max_r = rows.min(), rows.max()
        min_c, max_c = cols.min(), cols.max()
        # Find the min/max row and column indices containing tiles

        sub = self.tile_matrix[min_r:max_r + 1, min_c:max_c + 1]
        copy = np.vectorize(lambda t: cp.deepcopy(t) if t else None)(sub)
        # Extract and make a deep copy of the bounded matrix

        if not return_position:
            return copy
        blc = cp.copy(self.bottom_left_cell)
        blc.translate(min_c, (n - 1) - max_r)
        # Calculate the new bottom-left position for the bounded matrix
        return copy, blc
        # Return both the bounded matrix and its position if requested

    def move(self, direction, grid):
        # Move the tetromino in the specified direction if possible
        if not self.can_be_moved(direction, grid):
            return False
            # If movement is not possible, return False
        if direction == "left":
            self.bottom_left_cell.x -= 1
        elif direction == "right":
            self.bottom_left_cell.x += 1
        elif direction == "down":
            self.bottom_left_cell.y -= 1
        elif direction == "rotate":
            self.tile_matrix = Tetromino._rot90(self.tile_matrix)
            # Rotate the tetromino 90 degrees clockwise.
        return True
        
    def can_be_moved(self, direction, grid):
        # Check if the tetromino can be moved in the specified direction
        # rotate: simulate and check collisions
        if direction == "rotate":
            test = Tetromino._rot90(self.tile_matrix)
            return self._fits(test, self.bottom_left_cell, grid)
            # For rotation, simulate the rotation and check if it fits

        dx = -1 if direction == "left" else 1 if direction == "right" else 0
        dy = -1 if direction == "down" else 0
        # Determine the change in position based on direction
        new_blc = Point(self.bottom_left_cell.x + dx,
                        self.bottom_left_cell.y + dy)
        # Calculate the new position.
        return self._fits(self.tile_matrix, new_blc, grid)
        # Check if the tetromino fits at the new position

    # Checks if the given matrix fit at the given bottom-left position
    def _fits(self, matrix, blc, grid):
        # Check if a tile matrix fits at a specific position without collisions
        n = len(matrix)
        for r in range(n):
            for c in range(n):
                # Iterate through every cell in the matrix
                if matrix[r][c] is None:
                    continue
                    # Skip empty cells.
                pos = Point(blc.x + c, blc.y + (n - 1) - r)
                # Calculate the actual grid position for this cell
                if pos.x < 0 or pos.x >= Tetromino.grid_width:
                    return False
                    # Return False if outside grid boundaries horizontally
                if pos.y < 0:
                    return False
                    # Return False if below the bottom of the grid
                if pos.y < Tetromino.grid_height and \
                        grid.is_occupied(pos.y, pos.x):
                    return False
                    # Return False if colliding with an existing tile
        return True

    def draw(self, preview=False, offset_x=0, offset_y=0):
        # Draw the tetromino on the game screen or in the preview area.
        n = len(self.tile_matrix)
        for r in range(n):
            for c in range(n):
                # Iterate through each cell in the matrix.
                t = self.tile_matrix[r][c]
                if t is None:
                    continue
                    # Skip empty cells.
                pos = self.get_cell_position(r, c)
                # Calculate the position to draw the tile.
                # preview mode draws in a small 4×4 box top-right
                if preview:
                    pos.x = offset_x + c
                    pos.y = offset_y + (n - 1) - r
                    # Adjust position for preview mode with offset.
                if pos.y < Tetromino.grid_height or preview:
                    t.draw(pos)
                    # Draw the tile if it's within the grid or in preview mode.
