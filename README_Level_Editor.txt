Pygame Level Editor

A versatile 2D tile-based level editor built with Pygame. Create, edit, and save levels for platformers or other tile-based games. Supports multiple tile types, entities with customizable properties, undo/redo, copy-paste, zoom, and more.

---

Features

- Grid-based tile placement with customizable tile palette
- Support for multiple tile types, including solid blocks, enemies, player start, items, spikes, and more
- Entity property editor: Add custom properties to entities like enemies and moving platforms
- Undo and redo functionality
- Copy, cut, and paste tile selections with entities
- Zoom in and out for detailed editing
- Load and save level files in a simple text-based format
- Visual tooltips and UI buttons
- Keyboard and mouse support for intuitive editing
- Modular design allowing easy tile and property additions

---

Requirements

- Python 3.7+
- Pygame library

Install Pygame with:

pip install pygame

---

Getting Started

1. Download or clone the repository:

git clone https://github.com/yourusername/pygame-level-editor.git
cd pygame-level-editor

2. Run the editor:

python level_editor.py

---

Controls and Usage

Mouse

- Left Click: Place currently selected tile on the grid
- Right Click: Erase tile on the grid (set to empty)
- Middle Click: Start selecting a rectangular area for copy/cut
- Scroll Wheel: Zoom in/out on the level grid

Keyboard

- Arrow Keys: Pan camera view
- Z: Undo
- Y: Redo
- C: Copy selection
- X: Cut selection
- V: Paste clipboard contents at mouse position
- S: Save level to file (opens file dialog)
- L: Load level from file (opens file dialog)
- Escape: Cancel selection or deselect current input
- Enter: Confirm input in property editor
- Delete: Delete selected tiles or entities

UI

- Tile Palette: Click to select a tile type for placement
- Entity Property Editor: Opens when placing entities (like enemies or moving platforms), allowing you to customize properties like health, damage, speed, etc.

---

File Format

Levels are saved as simple text files:

- Each line represents a row in the level grid.
- Each character corresponds to a tile type.
- Entities and their properties are saved alongside.

Example level file:

####################
#S                 #
#       E          #
#    #######       #
#                  #
####################

---

Extending the Editor

- Adding Tiles: Add new tile characters and names in the TILE_TYPES dictionary.
- Adding Entities: Extend entity_properties dictionary and add property definitions in the EntityPropertyEditor.
- Custom Properties: Modify props_def in EntityPropertyEditor to add new editable properties.

---

Troubleshooting

- Black screen or window not responding? Make sure you have Pygame installed and your Python version is 3.7 or newer.
- Level file won't load? Check the file format and make sure it matches the expected grid size and tile characters.
- Undo/Redo not working? Undo stack only stores changes made during editing; try to save often.

---

License

MIT License

---

Credits

Developed by Your Name.

Based on Pygame framework.

---

If you want me to add anything else to the README, just ask!