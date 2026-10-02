import os
d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
pngs = sorted(f for f in os.listdir(d) if f.lower().endswith('.png'))
webps = sorted(f for f in os.listdir(d) if f.lower().endswith('.webp'))
png_set = set(os.path.splitext(f)[0] for f in pngs)
webp_set = set(os.path.splitext(f)[0] for f in webps)
total_w = sum(os.path.getsize(os.path.join(d, f)) for f in webps)
sizes = []
big = 0
for f in webps:
    s = os.path.getsize(os.path.join(d, f))
    sizes.append(s)
    if s > 1.25*1024*1024:
        big += 1
lines = [
    "PNG_LEFT: %d" % len(pngs),
    "WEBP: %d" % len(webps),
    "MATCH: %s" % (png_set == webp_set),
    "WEBP_TOTAL_MB: %.1f" % (total_w/1048576),
    "AVG_KB: %.0f" % (sum(sizes)/max(len(sizes),1)/1024),
    "MIN_KB: %.0f" % (min(sizes)/1024 if sizes else 0),
    "MAX_KB: %.0f" % (max(sizes)/1024 if sizes else 0),
    "OVER_1.25MB: %d" % big,
]
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
