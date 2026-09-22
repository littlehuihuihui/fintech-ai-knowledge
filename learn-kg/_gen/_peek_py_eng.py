# -*- coding: utf-8 -*-
import json
from pathlib import Path

KG = Path(r"D:\cursor\数据学习平台\kg-data")
py = json.loads((KG / "python.json").read_text(encoding="utf-8"))


def find(n, nid):
    if n.get("id") == nid:
        return n
    for c in n.get("children") or []:
        h = find(c, nid)
        if h:
            return h
    return None


for nid in ("py-eng", "py-path-mid", "py-perf", "py-repro"):
    n = find(py, nid)
    print("====", nid, "====")
    print(n.get("content", "")[:1200] if n else "MISSING")
    print()
