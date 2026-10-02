import os
from PIL import Image

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
samples = ["eSIM旅行功能图生成需求 (34).png",
           "eSIM旅行功能图生成需求 - 2026-09-29T003118.735.png",
           "eSIM旅行功能图生成需求 (95).png"]
grid = Image.new("RGB", (1210, 640), "white")
x = 0
for f in samples:
    img = Image.open(os.path.join(d, f))
    w, h = img.size
    tile = img.crop((w-400, h-200, w, h))
    grid.paste(tile, (x, 0))
    x += 405
grid.save(os.path.join(d, ".workbuddy", "verify_grid.png"))
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("grid saved")
