from PIL import Image
import numpy as np
from pathlib import Path

block_colors = {
    "red_wool":    (176, 46, 38),
    "orange_wool": (240, 118, 19),
    "yellow_wool": (248, 197, 39),
    "lime_wool":   (112, 185, 25),
    "green_wool":  (94, 124, 22),
    "cyan_wool":   (22, 156, 156),
    "blue_wool":   (60, 68, 170),
    "purple_wool": (137, 50, 184),
    "pink_wool":   (237, 141, 172),
    "gray_wool":   (63, 68, 71),
    "white_wool":  (233, 236, 236),
    "black_wool":  (29, 29, 33),
    "brown_wool":  (131, 84, 50),
    "magenta_wool":(189, 68, 179),
    "light_blue_wool":(58, 175, 217),
    "light_gray_wool":(142, 142, 134),
}

size = 16
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
pixels = img.load()

values = list(block_colors.values())
for y in range(size):
    for x in range(size):
        idx = (x + y) % len(values)
        pixels[x, y] = values[idx] + (255,)

out = Path(__file__).parent / "mc_example_map.png"
img.save(str(out))
print(f"Created: {out.resolve()}")
print(f"Uses actual Minecraft wool colors for accurate matching")
