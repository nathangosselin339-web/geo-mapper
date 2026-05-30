import numpy as np
from PIL import Image
from pathlib import Path

BLOCK_COLORS = {
    "minecraft:white_wool": (233, 236, 236),
    "minecraft:orange_wool": (240, 118, 19),
    "minecraft:magenta_wool": (189, 68, 179),
    "minecraft:light_blue_wool": (58, 175, 217),
    "minecraft:yellow_wool": (248, 197, 39),
    "minecraft:lime_wool": (112, 185, 25),
    "minecraft:pink_wool": (237, 141, 172),
    "minecraft:gray_wool": (63, 68, 71),
    "minecraft:light_gray_wool": (142, 142, 134),
    "minecraft:cyan_wool": (22, 156, 156),
    "minecraft:purple_wool": (137, 50, 184),
    "minecraft:blue_wool": (60, 68, 170),
    "minecraft:brown_wool": (131, 84, 50),
    "minecraft:green_wool": (94, 124, 22),
    "minecraft:red_wool": (176, 46, 38),
    "minecraft:black_wool": (29, 29, 33),
    "minecraft:white_concrete": (207, 213, 214),
    "minecraft:orange_concrete": (224, 97, 1),
    "minecraft:magenta_concrete": (169, 48, 159),
    "minecraft:light_blue_concrete": (36, 137, 199),
    "minecraft:yellow_concrete": (241, 175, 21),
    "minecraft:lime_concrete": (94, 169, 24),
    "minecraft:pink_concrete": (212, 100, 142),
    "minecraft:gray_concrete": (55, 58, 62),
    "minecraft:light_gray_concrete": (125, 125, 115),
    "minecraft:cyan_concrete": (21, 137, 145),
    "minecraft:purple_concrete": (100, 32, 156),
    "minecraft:blue_concrete": (45, 47, 143),
    "minecraft:brown_concrete": (96, 60, 31),
    "minecraft:green_concrete": (73, 91, 36),
    "minecraft:red_concrete": (142, 33, 33),
    "minecraft:black_concrete": (8, 10, 15),
    "minecraft:oak_planks": (162, 129, 72),
    "minecraft:spruce_planks": (115, 87, 54),
    "minecraft:birch_planks": (192, 171, 111),
    "minecraft:dark_oak_planks": (68, 50, 28),
    "minecraft:acacia_planks": (171, 115, 58),
    "minecraft:cherry_planks": (197, 126, 125),
    "minecraft:stone": (128, 128, 128),
    "minecraft:cobblestone": (116, 116, 116),
    "minecraft:sandstone": (220, 211, 168),
    "minecraft:nether_bricks": (44, 28, 28),
    "minecraft:red_nether_bricks": (135, 50, 34),
    "minecraft:smooth_basalt": (74, 74, 77),
    "minecraft:polished_blackstone": (50, 46, 54),
    "minecraft:end_stone": (217, 217, 191),
    "minecraft:purpur_block": (169, 127, 167),
    "minecraft:prismarine": (91, 158, 145),
    "minecraft:dark_prismarine": (44, 84, 66),
    "minecraft:prismarine_bricks": (98, 167, 155),
    "minecraft:terracotta": (160, 97, 66),
    "minecraft:white_terracotta": (210, 178, 161),
    "minecraft:orange_terracotta": (159, 84, 28),
    "minecraft:magenta_terracotta": (149, 84, 112),
    "minecraft:light_blue_terracotta": (112, 108, 138),
    "minecraft:yellow_terracotta": (186, 133, 35),
    "minecraft:lime_terracotta": (103, 117, 52),
    "minecraft:pink_terracotta": (161, 77, 78),
    "minecraft:gray_terracotta": (57, 42, 36),
    "minecraft:light_gray_terracotta": (135, 106, 97),
    "minecraft:cyan_terracotta": (86, 91, 92),
    "minecraft:purple_terracotta": (118, 70, 86),
    "minecraft:blue_terracotta": (73, 59, 91),
    "minecraft:brown_terracotta": (76, 50, 32),
    "minecraft:green_terracotta": (74, 82, 42),
    "minecraft:red_terracotta": (142, 61, 47),
    "minecraft:black_terracotta": (37, 23, 16),
    "minecraft:gold_block": (248, 212, 23),
    "minecraft:iron_block": (221, 221, 221),
    "minecraft:diamond_block": (90, 201, 205),
    "minecraft:emerald_block": (0, 198, 93),
    "minecraft:redstone_block": (180, 2, 2),
    "minecraft:lapis_block": (44, 65, 140),
    "minecraft:netherite_block": (66, 55, 55),
    "minecraft:bone_block": (227, 221, 200),
    "minecraft:clay": (161, 161, 167),
    "minecraft:honeycomb_block": (255, 158, 15),
    "minecraft:ochre_froglight": (217, 174, 69),
    "minecraft:verdant_froglight": (120, 212, 126),
    "minecraft:pearlescent_froglight": (192, 144, 207),
}

BLOCK_NAMES = list(BLOCK_COLORS.keys())
BLOCK_RGB = np.array(list(BLOCK_COLORS.values()), dtype=np.int32)

GREEN_MARK = (0, 230, 0, 220)
RED_MARK = (230, 0, 0, 220)


class MapEngine:
    def __init__(self, reference_path, block_scale=1.0):
        self.ref_path = Path(reference_path)
        self.ref_img = Image.open(self.ref_path).convert("RGBA")
        self.ref_array = np.array(self.ref_img, dtype=np.uint8)
        self.height, self.width = self.ref_array.shape[:2]
        self.block_scale = block_scale

        self.plan = {}
        self.completed = set()
        self.wrong = set()

    def world_to_pixel(self, wx, wz, origin_x=0, origin_z=0):
        px = int((wx - origin_x) / self.block_scale)
        py = int((wz - origin_z) / self.block_scale)
        return px, py

    def generate_plan(self):
        self.plan.clear()
        pixels = self.ref_array[:, :, :3].astype(np.int32)
        diffs = pixels[:, :, np.newaxis, :] - BLOCK_RGB[np.newaxis, np.newaxis, :, :]
        dists = np.sqrt(np.sum(diffs ** 2, axis=3))
        best = np.argmin(dists, axis=2)
        for y in range(self.height):
            for x in range(self.width):
                self.plan[(x, y)] = BLOCK_NAMES[int(best[y, x])]

    def get_plan_at(self, wx, wz, origin_x=0, origin_z=0):
        px, py = self.world_to_pixel(wx, wz, origin_x, origin_z)
        if px < 0 or px >= self.width or py < 0 or py >= self.height:
            return None
        return self.plan.get((px, py))

    def check_placement(self, wx, wz, block_id, origin_x=0, origin_z=0):
        px, py = self.world_to_pixel(wx, wz, origin_x, origin_z)
        if px < 0 or px >= self.width or py < 0 or py >= self.height:
            return False, (px, py), None
        expected = self.plan.get((px, py))
        if expected is None:
            return False, (px, py), None
        correct = block_id == expected
        if correct:
            self.completed.add((px, py))
            self.wrong.discard((px, py))
        else:
            self.wrong.add((px, py))
        return correct, (px, py), expected

    def generate_overlay(self):
        overlay = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        for (px, py) in self.completed:
            overlay[py, px] = GREEN_MARK
        for (px, py) in self.wrong:
            overlay[py, px] = RED_MARK
        return Image.fromarray(overlay, "RGBA")

    def generate_composite(self):
        ref = self.ref_array.copy()
        overlay_a = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        for (px, py) in self.completed:
            overlay_a[py, px] = GREEN_MARK
        for (px, py) in self.wrong:
            overlay_a[py, px] = RED_MARK
        overlay_f = overlay_a.astype(np.float32) / 255.0
        ref_f = ref.astype(np.float32) / 255.0
        a = overlay_f[:, :, 3:4]
        blended = ref_f * (1 - a) + overlay_f[:, :, :4] * a
        blended = np.clip(blended * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(blended, "RGBA")

    def generate_build_plan_image(self):
        img = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        for (px, py), block_id in self.plan.items():
            color = BLOCK_COLORS.get(block_id, (128, 128, 128))
            img[py, px] = (*color, 255)
        return Image.fromarray(img, "RGBA")

    def get_stats(self):
        total = len(self.plan)
        done = len(self.completed)
        wrong_count = len(self.wrong)
        remaining = total - done - wrong_count
        return {
            "total": total,
            "completed": done,
            "wrong": wrong_count,
            "remaining": remaining,
            "progress_pct": (done / total * 100) if total > 0 else 0,
        }
