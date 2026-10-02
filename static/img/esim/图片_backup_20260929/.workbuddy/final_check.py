import os
from PIL import Image
d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
webps = sorted(f for f in os.listdir(d) if f.lower().endswith('.webp'))
total = 0
broken = []
sizes = []
for f in webps:
    p = os.path.join(d, f)
    s = os.path.getsize(p)
    total += s
    sizes.append(s)
    try:
        with Image.open(p) as img:
            img.verify()
    except Exception:
        broken.append(f)
lines = [
    "WEBP_COUNT: %d" % len(webps),
    "TOTAL_MB: %.1f" % (total/1048576),
    "AVG_KB: %.0f" % (sum(sizes)/len(sizes)/1024),
    "MIN_KB: %.0f" % (min(sizes)/1024),
    "MAX_KB: %.0f" % (max(sizes)/1024),
    "OVER_1MB: %d" % sum(1 for s in sizes if s > 1024*1024),
    "BROKEN: %s" % broken,
]
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
