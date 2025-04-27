import lib.stddraw as stddraw
from lib.color import Color
from point import Point
import numpy as np
import copy as cp


class GameGrid:
    def __init__(self, grid_h, grid_w):
        self.grid_height = grid_h
        self.grid_width = grid_w
        self.tile_matrix = np.full((grid_h, grid_w), None)
        self.current_tetromino = None
        self.game_over = False
        self.score = 0
        self.empty_cell_color = Color(42, 69, 99)
        self.line_color = Color(0, 100, 200)
        self.boundary_color = Color(0, 100, 200)
        self.line_thickness = 0.002
        self.box_thickness = 10 * self.line_thickness
        self.win = False   # 2048 reached flag

    # ────────────── locking & post-processing ──────────────
    def update_grid(self, tiles_to_lock, blc_pos):
        # place locked tiles
        for r in range(len(tiles_to_lock)):
            for c in range(len(tiles_to_lock[0])):
                tile = tiles_to_lock[r][c]
                if tile is None:
                    continue
                x = blc_pos.x + c
                y = blc_pos.y + (len(tiles_to_lock) - 1) - r
                if y >= self.grid_height:          # above top
                    self.game_over = True
                    return True
                self.tile_matrix[y][x] = tile

        # 1) cascading merges
        self._cascade_merge()

        # 2) settle any floating tiles (repeat until stable)
        self._settle_floating()

        # 3) clear full rows and settle again (rows removed can
        #    leave new floaters)
        self._clear_rows()
        self._settle_floating()

        return self.game_over

    # ───────────────────────────────────────────────────────
    def _cascade_merge(self):
        merged = True
        while merged:
            merged = False
            for x in range(self.grid_width):
                y = 0
                while y < self.grid_height - 1:
                    t1 = self.tile_matrix[y][x]
                    t2 = self.tile_matrix[y + 1][x]
                    if t1 and t2 and t1.number == t2.number:
                        t1.double()          # updates colour + value
                        self.score += t1.number
                        if t1.number == 2048:
                            self.win = True
                        self.tile_matrix[y + 1][x] = None
                        merged = True        # keep looping
                        # don’t advance y – need to check new t1 with new neighbour
                    else:
                        y += 1
            if merged:
                self._settle_floating() 
    def _settle_floating(self):
        while True:
            connected = self._connected_to_bottom()
            moved = False
            for y in range(1, self.grid_height):          # skip bottom row (y==0)
                for x in range(self.grid_width):
                    tile = self.tile_matrix[y][x]
                    if tile is None or connected[y][x]:
                        continue            # empty or already supported
                    if self.tile_matrix[y - 1][x] is None:   # empty below
                        self.tile_matrix[y - 1][x] = tile
                        self.tile_matrix[y][x] = None
                        moved = True
            if not moved:
                break
    def _connected_to_bottom(self):
        visited = np.full(self.tile_matrix.shape, False)
        stack = [(0, x) for x in range(self.grid_width)
                 if self.tile_matrix[0][x] is not None]

        while stack:
            y, x = stack.pop()
            if visited[y][x]:
                continue
            visited[y][x] = True
            # explore four neighbours
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.grid_height and 0 <= nx < self.grid_width \
                        and self.tile_matrix[ny][nx] is not None \
                        and not visited[ny][nx]:
                    stack.append((ny, nx))
        return visited

    # flood-fill from bottom, remove unvisited tiles
    def _collect_floating(self):
        visited = np.full(self.tile_matrix.shape, False)

        # DFS stack seeded with bottom-row tiles
        stack = [(0, x) for x in range(self.grid_width)]
        while stack:
            y, x = stack.pop()
            if y < 0 or y >= self.grid_height or x < 0 or x >= self.grid_width:
                continue
            if visited[y][x] or self.tile_matrix[y][x] is None:
                continue
            visited[y][x] = True
            # 4-connect neighbours
            stack.extend([(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)])

        # delete floating
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.tile_matrix[y][x] is not None and not visited[y][x]:
                    self.score += self.tile_matrix[y][x].number
                    self.tile_matrix[y][x] = None

    # clear any row that’s completely filled
    def _clear_rows(self):
        write_row = 0
        for read_row in range(self.grid_height):
            if None not in self.tile_matrix[read_row]:      # full row
                self.score += sum(tile.number for tile in self.tile_matrix[read_row])
                continue
            if write_row != read_row:
                self.tile_matrix[write_row] = self.tile_matrix[read_row]
            write_row += 1

        # blank the rows that were cleared
        for y in range(write_row, self.grid_height):
            self.tile_matrix[y] = np.full(self.grid_width, None)

    # ────────────── draw helpers (unchanged) ──────────────
    def display(self):
        stddraw.clear(self.empty_cell_color)
        self.draw_grid()
        if self.current_tetromino is not None:
            self.current_tetromino.draw()
        self.draw_boundaries()
        stddraw.show(250)

    def draw_grid(self):
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
        stddraw.setPenColor(self.boundary_color)
        stddraw.setPenRadius(self.box_thickness)
        stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    # external collision helpers stay unchanged
    def is_occupied(self, row, col):
        if not self.is_inside(row, col):
            return False
        return self.tile_matrix[row][col] is not None

    def is_inside(self, row, col):
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width
