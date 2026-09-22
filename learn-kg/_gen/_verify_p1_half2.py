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


dwh = json.loads((KG / "dwh.json").read_text(encoding="utf-8"))
etl = json.loads((KG / "etl.json").read_text(encoding="utf-8"))
why = find(dwh, "dwh-why")
print("dwh-why kids", [c["id"] for c in why["children"]])
print("map lakehouse", "湖仓一体" in why["content"])
print("order lakehouse", "湖仓一体" in why["content"])
# show map lines
for line in why["content"].splitlines():
    if line.startswith("|") or "推荐顺序" in line or "text" in line or "→" in line or "湖仓" in line:
        print(" W", line)
senior = find(dwh, "dwh-path-senior")
print("senior has lakehouse", "dwh-lakehouse-sec" in senior["content"] or "湖仓一体" in senior["content"])
for line in senior["content"].splitlines():
    if "湖仓" in line or line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
        print(" S", line)

q = find(etl, "etl-quality")
print("etl-quality kids", [c["id"] for c in q["children"]])
print("map dq", "质量规则引擎" in q["content"])
for line in q["content"].splitlines():
    if line.startswith("|") or "→" in line or "质量规则" in line or "校验" in line:
        print(" Q", line)
mid = find(etl, "etl-path-mid")
print("mid has dq", "etl-dq-engine-sec" in mid["content"] or "质量规则引擎" in mid["content"])
for line in mid["content"].splitlines():
    if "质量规则" in line or "etl-dq" in line or line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.")):
        print(" M", line)

# uniqueness sample
sec = find(dwh, "dwh-lakehouse-sec")
print("lake leaves", [c["id"] for c in sec["children"]])
dq = find(etl, "etl-dq-engine-sec")
print("dq leaves", [c["id"] for c in dq["children"]])
print("refs ok", "dwh-layers" in sec["content"], "etl-checks" in dq["content"])
