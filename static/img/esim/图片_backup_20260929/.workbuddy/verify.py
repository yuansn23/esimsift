import os, struct
from PIL import Image

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
files = [f for f in os.listdir(d) if f.lower().endswith('.png')]
tmps = [f for f in os.listdir(d) if f.endswith('.tmp')]
dims = {}
total = 0
bad = []
for f in files:
    p = os.path.join(d, f)
    total += os.path.getsize(p)
    try:
        with Image.open(p) as img:
            s = img.size
            dims[s] = dims.get(s, 0) + 1
    except Exception as e:
        bad.append(f)
lines = []
lines.append("COUNT: %d" % len(files))
lines.append("TMP_LEFT: %d" % len(tmps))
lines.append("TOTAL_MB: %.1f" % (total/1048576))
lines.append("DIMS: %s" % dims)
lines.append("BROKEN: %s" % bad)
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
