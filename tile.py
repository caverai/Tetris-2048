import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles
import random

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # the value of the boundary thickness (for the boxes around the tiles)
   boundary_thickness = 0.004
   # font family and font size used for displaying the tile number
   font_family, font_size = "Arial", 14

   # A constructor that creates a tile with 2 as the number on it
   def __init__(self):
        self.number = random.choice((2, 4))
        self._set_colors()

   def _set_colors(self):
        palette = {
            2:  (151, 178, 199),
            4:  (118, 150, 175),
            8:  (100, 130, 155),
            16: (82, 110, 135),
            32: (68,  92, 115),
            64: (55,  75,  95),
            128:(230, 167, 70),
            256:(232, 149, 10),
            512:(237, 118, 15),
            1024:(237,  90,  2),
            2048:(242,  75, 12),
            4096:(255, 0, 0),
            8192:(255,0,0),
            16384:(255,0,0)
        }
        r, g, b = palette.get(self.number, (40, 40, 40))
        self.background_color = Color(r, g, b)
        self.foreground_color = Color(0, 25, 51)
        self.box_color = Color(0, 100, 200)
   def double(self):
        self.number *= 2
        self._set_colors()

   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1):  # length defaults to 1
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x, position.y, length / 2)
      # draw the bounding box around the tile as a square
      stddraw.setPenColor(self.box_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(position.x, position.y, length / 2)
      stddraw.setPenRadius()  # reset the pen radius to its default value
      # draw the number on the tile
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      stddraw.setFontSize(Tile.font_size)
      stddraw.text(position.x, position.y, str(self.number))
