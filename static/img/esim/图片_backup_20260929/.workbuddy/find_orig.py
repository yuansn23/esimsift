import os
results = []
for root, dirs, files in os.walk(r"D:\workbuddy"):
    dirs[:] = [x for x in dirs if x not in ('node_modules', '.git')]
    for f in files:
        if f == "eSIM旅行功能图生成需求.png":
            p = os.path.join(root, f)
            results.append("%s | %.1f KB | %s" % (p, os.path.getsize(p)/1024, __import__('time').strftime('%Y-%m-%d %H:%M', __import__('time').localtime(os.path.getmtime(p)))))
with open(r"D:\workbuddy\.workbuddy\图片_backup_20260929\.workbuddy\scan_out.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(results) if results else "NOT FOUND")
