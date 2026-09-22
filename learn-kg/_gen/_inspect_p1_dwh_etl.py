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


def dump_hits(tree, keys):
    hits = []

    def walk(n):
        tid = n.get("id") or ""
        title = n.get("title") or ""
        if any(k in tid or k in title for k in keys):
            hits.append(
                (
                    tid,
                    title,
                    n.get("level"),
                    [c.get("id") for c in (n.get("children") or [])],
                )
            )
        for c in n.get("children") or []:
            walk(c)

    walk(tree)
    return hits


dwh = json.loads((KG / "dwh.json").read_text(encoding="utf-8"))
etl = json.loads((KG / "etl.json").read_text(encoding="utf-8"))
print("=== DWH hits ===")
for h in dump_hits(
    dwh,
    [
        "dwh-why",
        "仓是什么",
        "path-senior",
        "高级",
        "分层",
        "增量",
        "分区",
        "ssot",
        "SSOT",
    ],
):
    print(h)
print("=== ETL hits ===")
for h in dump_hits(
    etl,
    [
        "etl-quality",
        "质量",
        "path-mid",
        "中级",
        "校验",
        "dbt",
        "选型",
        "对账",
    ],
):
    print(h)

# show chapter maps
for nid in ("dwh-why", "etl-quality", "dwh-path-senior", "etl-path-mid"):
    n = find(dwh, nid) or find(etl, nid)
    print("====", nid, "found", bool(n))
    if n:
        print("kids", [c.get("id") for c in (n.get("children") or [])])
        print((n.get("content") or "")[:900])
        print()
