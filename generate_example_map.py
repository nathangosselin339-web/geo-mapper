from PIL import Image
import numpy as np
import sys
from pathlib import Path

if len(sys.argv) < 2:
    out = Path(__file__).parent / "example_map.png"
else:
    out = Path(sys.argv[1])

colors = {
    "red":    (255, 85, 85),
    "orange": (255, 170, 85),
    "yellow": (255, 255, 85),
    "lime":   (85, 255, 85),
    "green":  (85, 170, 85),
    "cyan":   (85, 255, 255),
    "blue":   (85, 85, 255),
    "purple": (170, 85, 255),
    "magenta":(255, 85, 255),
    "pink":   (255, 170, 255),
    "brown":  (129, 75, 49),
    "gray":   (136, 136, 136),
    "white":  (255, 255, 255),
    "black":  (0, 0, 0),
    "gold":   (255, 200, 0),
    "diamond":(85, 255, 200),
}

size = 16
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
pixels = img.load()

color_list = list(colors.values())
for y in range(size):
    for x in range(size):
        pixels[x, y] = color_list[(x + y) % len(color_list)] + (255,)

img.save(str(out))
print(f"Created example map: {out.resolve()}")
print(f"Size: {size}x{size} pixels")
