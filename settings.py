TILE_SIZE = 32
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_POWER = 15

TILE_TYPES = {
    "G": (50, 200, 50),    # Ground
    "W": (50, 50, 200),    # Water
    "P": (150, 75, 0),     # Platform
    "E": (200, 0, 0),      # Enemy
    "C": (255, 215, 0),    # Coin
    "S": (255, 255, 255),  # Spike
    " ": (0, 0, 0),        # Empty space (black)
}

TILE_NAMES = {
    "G": "Ground",
    "W": "Water",
    "P": "Platform",
    "E": "Enemy",
    "C": "Coin",
    "S": "Spike",
    " ": "Empty",
}
