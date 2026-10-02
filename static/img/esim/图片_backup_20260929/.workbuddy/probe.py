import os, random
from PIL import Image

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
files = [f for f in os.listdir(d) if f.lower().endswith('.png')]
random.seed(42)
sample = random.sample(files, 6)
# 拼接6张样本的右下角区域 (600x200) 成一张网格图
tiles = []
for f in sample:
    img = Image.open(os.path.join(d, f))
    w, h = img.size
    if (w, h) != (2848, 1600):
        tiles.append((f, (w, h), None))
        continue
    tiles.append((f, (w, h), img.crop((w-600, h-200, w, h))))

grid = Image.new("RGB", (610, 200*len(tiles)+10), "white")
y = 0
names = []
for f, size, tile in tiles:
    names.append("%s %s" % (f, size))
    if tile:
        grid.paste(tile, (0, y))
    y += 205
grid.save(os.path.join(d, ".workbuddy", "corner_grid.png"))
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(names))
