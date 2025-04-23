from tile import Tile
from point import Point
import copy as cp
import random
import numpy as np


class Tetromino:
    # will be set by main before any Tetromino is created
    grid_height, grid_width = None, None

    # clockwise rotation matrix helper
    @staticmethod
    def _rot90(mat):
        return np.rot90(mat, k=3)   # 3×90° = -90° → clockwise

    # ──────────────────────────────────────────────────────────

    def __init__(self, shape: str):
        self.type = shape.upper()

        # every piece fits inside an N×N square (N given per shape)
        self.tile_matrix, n = self._make_tiles(self.type)

        # spawn above the grid at a random x so the piece body is inside
        self.bottom_left_cell = Point(
            (Tetromino.grid_width - n)//2,
            Tetromino.grid_height - 1
        )

    # build the initial orientation & tile objects
    def _make_tiles(self, t):
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

        m = np.full((n, n), None)
        for c, r in occ:
            m[r][c] = Tile()
        return m, n

    # ──────────────────────────────────────────────────────────
    #      geometry helpers
    # ──────────────────────────────────────────────────────────
    def get_cell_position(self, row, col):
        n = len(self.tile_matrix)
        return Point(
            self.bottom_left_cell.x + col,
            self.bottom_left_cell.y + (n - 1) - row
        )

    def get_min_bounded_tile_matrix(self, return_position=False):
        n = len(self.tile_matrix)
        rows, cols = np.where(self.tile_matrix != None)
        min_r, max_r = rows.min(), rows.max()
        min_c, max_c = cols.min(), cols.max()

        sub = self.tile_matrix[min_r:max_r + 1, min_c:max_c + 1]
        copy = np.vectorize(lambda t: cp.deepcopy(t) if t else None)(sub)

        if not return_position:
            return copy
        blc = cp.copy(self.bottom_left_cell)
        blc.translate(min_c, (n - 1) - max_r)
        return copy, blc

    # ──────────────────────────────────────────────────────────
    #      movement
    # ──────────────────────────────────────────────────────────
    def move(self, direction, grid):
        if not self.can_be_moved(direction, grid):
            return False
        if direction == "left":
            self.bottom_left_cell.x -= 1
        elif direction == "right":
            self.bottom_left_cell.x += 1
        elif direction == "down":
            self.bottom_left_cell.y -= 1
        elif direction == "rotate":
            self.tile_matrix = Tetromino._rot90(self.tile_matrix)
        return True

    def can_be_moved(self, direction, grid):
        # rotate: simulate and check collisions
        if direction == "rotate":
            test = Tetromino._rot90(self.tile_matrix)
            return self._fits(test, self.bottom_left_cell, grid)

        dx = -1 if direction == "left" else 1 if direction == "right" else 0
        dy = -1 if direction == "down" else 0
        new_blc = Point(self.bottom_left_cell.x + dx,
                        self.bottom_left_cell.y + dy)
        return self._fits(self.tile_matrix, new_blc, grid)

    # does the given matrix fit at the given bottom-left position?
    def _fits(self, matrix, blc, grid):
        n = len(matrix)
        for r in range(n):
            for c in range(n):
                if matrix[r][c] is None:
                    continue
                pos = Point(blc.x + c, blc.y + (n - 1) - r)
                # outside grid horizontally?
                if pos.x < 0 or pos.x >= Tetromino.grid_width:
                    return False
                # below bottom?
                if pos.y < 0:
                    return False
                # collide with existing locked tile?
                if pos.y < Tetromino.grid_height and \
                        grid.is_occupied(pos.y, pos.x):
                    return False
        return True

    # ──────────────────────────────────────────────────────────
    #      rendering
    # ──────────────────────────────────────────────────────────
    def draw(self, preview=False, offset_x=0, offset_y=0):
        n = len(self.tile_matrix)
        for r in range(n):
            for c in range(n):
                t = self.tile_matrix[r][c]
                if t is None:
                    continue
                pos = self.get_cell_position(r, c)
                # preview mode draws in a small 4×4 box top-right
                if preview:
                    pos.x = offset_x + c
                    pos.y = offset_y + (n - 1) - r
                if pos.y < Tetromino.grid_height or preview:
                    t.draw(pos)
