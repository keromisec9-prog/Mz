#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"
ANCHOR = "body { background: var(--bg); color: var(--white); font-family: 'Inter', sans-serif; min-height: 100vh; padding-bottom: 4rem; }"
NEW = "html { overflow-x: hidden; width: 100%; }\nbody { background: var(--bg); color: var(--white); font-family: 'Inter', sans-serif; min-height: 100vh; padding-bottom: 4rem; overflow-x: hidden; width: 100%; }"

def main():
    with open(FILE, "r", encoding="utf-8") as f:
        content = f.read()
    if "html { overflow-x: hidden" in content:
        print("⚠️  Already patched — skipping.")
        sys.exit(0)
    count = content.count(ANCHOR)
    if count != 1:
        print(f"❌ Anchor found {count} times — expected 1. Aborting.")
        sys.exit(1)
    content = content.replace(ANCHOR, NEW, 1)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Patched — html/body now clip horizontal overflow.")

if __name__ == "__main__":
    main()
