# -*- coding: utf-8 -*-
import json
from pathlib import Path

KG = Path(r"D:\cursor\数据学习平台\kg-data")
py = json.loads((KG / "python.json").read_text(encoding="utf-8"))
hits = []


def find_eng(n):
    tid = n.get("id") or ""
    title = n.get("title") or ""
    if any(k in tid or k in title for k in ("eng", "工程", "生态", "path-mid", "中级", "py-eng")):
        hits.append((tid, title, [c.get("id") for c in (n.get("children") or [])], n.get("content", "")[:200]))
    for c in n.get("children") or []:
        find_eng(c)


find_eng(py)
print("=== PYTHON hits ===")
for h in hits:
    print(h[0], "|", h[1], "| kids=", h[2])

bi = json.loads((KG / "bi.json").read_text(encoding="utf-8"))
print("=== BI L2 ===")
for c in bi.get("children") or []:
    print(c.get("id"), "|", c.get("title"), "|", c.get("level"), "| kids", len(c.get("children") or []))
