import os, traceback
from PIL import Image

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
f = "eSIM旅行功能图生成需求.png"
path = os.path.join(d, f)
tmp = path + ".tmp"
out = []
try:
    img = Image.open(path)
    out.append("opened %s mode=%s size=%s" % (f, img.mode, img.size))
    cropped = img.crop((0, 0, img.size[0], img.size[1]-130))
    out.append("cropped ok")
    cropped.save(tmp, format="PNG", optimize=True)
    out.append("saved tmp exists=%s size=%d" % (os.path.exists(tmp), os.path.getsize(tmp)))
    os.replace(tmp, path)
    out.append("replaced ok, new size=%d" % os.path.getsize(path))
except Exception:
    out.append(traceback.format_exc())
with open(os.path.join(d, ".workbuddy", "scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))
