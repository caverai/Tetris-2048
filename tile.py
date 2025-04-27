import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles
import random

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # These values are the same for all tile instances
   boundary_thickness = 0.004  # Sets the thickness of borders around tiles
   font_family, font_size = "Arial", 14  # Defines text appearance for tile numbers

   # A constructor that creates a tile with either 2 or 4 as the number on it
   def __init__(self):
        # Randomly choose between 2 and 4 for new tile value
        self.number = random.choice((2, 4))
        # Initialize colors based on the tile's number
        self._set_colors()

   # A method that assigns colors to the tile based on its number value
   def _set_colors(self):
        # Dictionary mapping each possible tile value to an RGB color tuple
        palette = {
            2:  (151, 178, 199),  # Light blue for lowest value
            4:  (118, 150, 175),
            8:  (100, 130, 155),
            16: (82, 110, 135),
            32: (68,  92, 115),
            64: (55,  75,  95),
            128:(230, 167, 70),   # Transitions to orange/yellow hues
            256:(232, 149, 10),
            512:(237, 118, 15),
            1024:(237,  90,  2),
            2048:(242,  75, 12),  # Target value is bright orange
            4096:(255, 0, 0),     # Higher values use red
            8192:(255,0,0),
            16384:(255,0,0)
        }
        # Get RGB values from palette or use dark gray (40,40,40) if not found
        r, g, b = palette.get(self.number, (40, 40, 40))
        # Create Color objects for the tile's appearance
        self.background_color = Color(r, g, b)  # Fill color for the tile
        self.foreground_color = Color(0, 25, 51)  # Color for the number text
        self.box_color = Color(0, 100, 200)  # Color for the tile's border

   # A method that doubles the number on the tile and updates its colors
   def double(self):
        # Multiply the current number by 2
        self.number *= 2
        # Update colors to match the new number
        self._set_colors()

   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1):  # length defaults to 1
      # Draw the tile as a filled square with the background color
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x, position.y, length / 2)
      
      # Draw the bounding box around the tile
      stddraw.setPenColor(self.box_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(position.x, position.y, length / 2)
      stddraw.setPenRadius()  # Reset the pen radius to its default value
      
      # Draw the number on the tile
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      stddraw.setFontSize(Tile.font_size)
      stddraw.text(position.x, position.y, str(self.number))
