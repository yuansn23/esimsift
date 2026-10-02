import os, time, traceback
from PIL import Image

d = r"D:\workbuddy\.workbuddy\图片_backup_20260929"
log_path = os.path.join(d, ".workbuddy", "process_log.txt")
CROP_BOTTOM = 130  # 裁掉底部130px去除右下角水印

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

files = [f for f in os.listdir(d) if f.lower().endswith('.png')]
log("START %s files=%d" % (time.strftime("%H:%M:%S"), len(files)))

done = 0
before_total = 0
after_total = 0
failed = []
t0 = time.time()
for i, f in enumerate(files, 1):
    path = os.path.join(d, f)
    tmp = path + ".tmp"
    try:
        before = os.path.getsize(path)
        before_total += before
        img = Image.open(path)
        w, h = img.size
        new_h = h - CROP_BOTTOM
        cropped = img.crop((0, 0, w, new_h))
        # 无损压缩: optimize=True 使用最高 zlib 压缩级别, 不损失任何像素
        cropped.save(tmp, format="PNG", optimize=True)
        img.close()
        os.replace(tmp, path)
        after = os.path.getsize(tmp)
        after_total += after
        done += 1
        if i % 10 == 0 or i == len(files):
            log("PROGRESS %d/%d elapsed=%.0fs" % (i, len(files), time.time()-t0))
    except Exception:
        failed.append(f)
        log("FAIL %s: %s" % (f, traceback.format_exc().splitlines()[-1]))
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

log("DONE files=%d done=%d failed=%d" % (len(files), done, len(failed)))
log("BEFORE_MB=%.1f AFTER_MB=%.1f SAVED_PCT=%.1f%%" % (
    before_total/1048576, after_total/1048576,
    100*(before_total-after_total)/max(before_total,1)))
if failed:
    log("FAILED_LIST: " + ", ".join(failed))
