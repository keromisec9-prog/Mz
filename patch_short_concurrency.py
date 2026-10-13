#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

OLD = "const _shortMaxConcurrent = 2;"
NEW = "const _shortMaxConcurrent = 4;"

count = content.count(OLD)
if count != 1:
    print(f"❌ Anchor found {count} times — aborting.")
    sys.exit(1)
content = content.replace(OLD, NEW, 1)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Patched — shorts queue now runs 4 concurrent uploads.")
