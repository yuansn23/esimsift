import os
d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
pngs = sorted(f for f in os.listdir(d) if f.lower().endswith('.png'))
webp_set = set(os.path.splitext(f)[0] for f in os.listdir(d) if f.lower().endswith('.webp'))
missing = [f for f in pngs if os.path.splitext(f)[0] not in webp_set]
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(missing) if missing else "ALL MATCH")
