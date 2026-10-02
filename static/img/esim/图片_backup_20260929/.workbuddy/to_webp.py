import os, time, traceback
from PIL import Image

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
log_path = os.path.join(d, ".workbuddy", "webp_log.txt")
UPPER = 1.25 * 1024 * 1024
QUALITIES = [85, 78, 70, 62]

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# 只处理还没有对应 webp 的 png
files = sorted(
    f for f in os.listdir(d)
    if f.lower().endswith('.png')
    and not os.path.exists(os.path.join(d, os.path.splitext(f)[0] + ".webp"))
)
log("RESUME %s remaining=%d (不删除PNG)" % (time.strftime("%H:%M:%S"), len(files)))

total_webp = 0
failed = []
t0 = time.time()
for i, f in enumerate(files, 1):
    src = os.path.join(d, f)
    dst = os.path.join(d, os.path.splitext(f)[0] + ".webp")
    tmp = dst + ".tmp"
    try:
        img = Image.open(src)
        if img.mode != "RGB":
            img = img.convert("RGB")
        final_size = None
        for q in QUALITIES:
            img.save(tmp, format="WEBP", quality=q, method=6)
            sz = os.path.getsize(tmp)
            final_size = sz
            if sz <= UPPER:
                break
        os.replace(tmp, dst)
        total_webp += final_size
        if i % 10 == 0 or i == len(files):
            log("PROGRESS %d/%d elapsed=%.0fs avg_webp=%.0fKB" % (
                i, len(files), time.time()-t0, total_webp/max(i,1)/1024))
    except Exception:
        failed.append(f)
        log("FAIL %s: %s" % (f, traceback.format_exc().splitlines()[-1]))
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

log("RESUME_DONE converted=%d failed=%d avg_webp=%.0fKB" % (
    len(files)-len(failed), len(failed), total_webp/max(len(files)-len(failed),1)/1024))
if failed:
    log("FAILED_LIST: " + ", ".join(failed))
