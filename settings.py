# settings.py
TILE_SIZE = 40
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_POWER = 15

TILE_TYPES = {
    " ": (0, 0, 0),          # empty
    "G": (100, 100, 100),    # ground
    "P": (255, 0, 0),        # player
    "C": (255, 255, 0),      # coin
    "S": (0, 255, 0),        # spike
}
