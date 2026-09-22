# -*- coding: utf-8 -*-
import json
from pathlib import Path

KG = Path(r"D:\cursor\数据学习平台\kg-data")


def find(n, nid):
    if n.get("id") == nid:
        return n
    for c in n.get("children") or []:
        h = find(c, nid)
        if h:
            return h
    return None


py = json.loads((KG / "python.json").read_text(encoding="utf-8"))
eng = find(py, "py-eng")
leaf = find(py, "py-eng-error-log")
mid = find(py, "py-path-mid")
print("eng kids", [c["id"] for c in eng["children"]])
print("leaf len", len(leaf["content"]), "level", leaf["level"])
print("map has error-log", "异常处理与日志" in eng["content"])
print("mid has error-log", "异常处理与日志" in mid["content"])
# show map section
i = eng["content"].find("本章叶课地图")
print(eng["content"][i : i + 450])
print("--- mid order ---")
j = mid["content"].find("推荐顺序")
print(mid["content"][j : j + 280])

bi = json.loads((KG / "bi.json").read_text(encoding="utf-8"))
print("BI L2", [c["id"] for c in bi["children"]])
sem = find(bi, "BI.语义层")
print("sem kids", [c["id"] for c in sem["children"]])
assert (KG / "难度词典.md").exists()
for name in ["sql", "bi", "python", "database", "ml", "etl", "dwh"]:
    t = json.loads((KG / f"{name}.json").read_text(encoding="utf-8"))
    assert "难度词典.md" in t["content"]
print("ALL OK")
