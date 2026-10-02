import os, sys, struct
import zlib

def png_size(path):
    with open(path, 'rb') as f:
        data = f.read(33)
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    w, h = struct.unpack('>II', data[16:24])
    return w, h

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
files = [f for f in os.listdir(d) if f.lower().endswith('.png')]
total = sum(os.path.getsize(os.path.join(d, f)) for f in files)
sizes = {}
for f in files:
    s = png_size(os.path.join(d, f))
    sizes[s] = sizes.get(s, 0) + 1
lines = []
lines.append("COUNT: %d" % len(files))
lines.append("TOTAL_MB: %.1f" % (total/1048576))
lines.append("DIMENSIONS: %s" % sizes)
mins = min(files, key=lambda f: os.path.getsize(os.path.join(d, f)))
maxs = max(files, key=lambda f: os.path.getsize(os.path.join(d, f)))
lines.append("MIN_FILE_KB: %.1f %s" % (os.path.getsize(os.path.join(d, mins))/1024, mins))
lines.append("MAX_FILE_KB: %.1f %s" % (os.path.getsize(os.path.join(d, maxs))/1024, maxs))
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
