from PIL import Image
import os

# Define tile colors (RGBA will be added automatically)
TILE_TYPES = {
    "G": (50, 200, 50),    # Ground - green
    "W": (50, 50, 200),    # Water - blue
    "P": (150, 75, 0),     # Platform - brown
    "E": (200, 0, 0),      # Enemy - red
    "C": (255, 215, 0),    # Coin - gold/yellow
    "S": (255, 255, 255),  # Spike - white
    " ": (0, 0, 0),        # Empty - black
}

ICON_SIZE = (32, 32)

def create_icon(color):
    # Create a new image with the given color
    img = Image.new("RGBA", ICON_SIZE, color + (255,))
    pixels = img.load()
    
    # Draw white border
    for x in range(ICON_SIZE[0]):
        for y in range(ICON_SIZE[1]):
            if x == 0 or y == 0 or x == ICON_SIZE[0] - 1 or y == ICON_SIZE[1] - 1:
                pixels[x, y] = (255, 255, 255, 255)
    return img

def main():
    os.makedirs("icons", exist_ok=True)

    for tile_key, color in TILE_TYPES.items():
        icon = create_icon(color)
        filename = f"icons/{tile_key}.png"
        icon.save(filename)
        print(f"Saved {filename}")

if __name__ == "__main__":
    main()
