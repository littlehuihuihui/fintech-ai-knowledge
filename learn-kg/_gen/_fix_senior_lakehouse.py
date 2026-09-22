# -*- coding: utf-8 -*-
"""Insert lakehouse into dwh-path-senior 必学顺序 and resync."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"D:\cursor\数据学习平台")
KG = ROOT / "kg-data"
LESSONS = ROOT / "_gen" / "lessons"
MIRRORS = [
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\kg-data"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\kg-data"),
]
HTMLS = [
    ROOT / "数据知识图谱.html",
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\learn.html"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\learn.html"),
]


def find(n, nid):
    if n.get("id") == nid:
        return n
    for c in n.get("children") or []:
        h = find(c, nid)
        if h:
            return h
    return None


def sync(name: str, tree: dict):
    compact = json.dumps(tree, ensure_ascii=False, separators=(",", ":"))
    pretty = json.dumps(tree, ensure_ascii=False, indent=2)
    (KG / f"{name}.json").write_text(compact, encoding="utf-8")
    if LESSONS.exists():
        (LESSONS / f"{name}.json").write_text(pretty, encoding="utf-8")
    hub = "hub-dwh.json" if name == "dwh" else "hub-etl.json"
    (KG / hub).write_text(compact, encoding="utf-8")
    emb = (
        'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {};\n'
        f'window.__KG_EMBEDDED["{name}"]={compact}\n'
    )
    (KG / f"embed-{name}.js").write_text(emb, encoding="utf-8")
    for m in MIRRORS:
        if not m.exists():
            continue
        (m / f"{name}.json").write_text(compact, encoding="utf-8")
        (m / hub).write_text(compact, encoding="utf-8")
        (m / f"embed-{name}.js").write_text(emb, encoding="utf-8")


def patch_order(content: str) -> str:
    order = ""
    if "### 必学顺序" in content:
        order = content.split("### 必学顺序", 1)[1].split("###", 1)[0]
    if "dwh-lakehouse-sec" in order:
        return content
    needle = "5. 与 BI 语义层 / 认证数据集对齐"
    insert = "5. 湖仓一体（`dwh-lakehouse-sec`）  \n6. 与 BI 语义层 / 认证数据集对齐"
    if needle not in content:
        raise SystemExit("needle missing in dwh-path-senior")
    return content.replace(needle, insert, 1)


def main():
    dwh = json.loads((KG / "dwh.json").read_text(encoding="utf-8"))
    senior = find(dwh, "dwh-path-senior")
    if not senior:
        raise SystemExit("dwh-path-senior missing")
    senior["content"] = patch_order(senior.get("content") or "")
    sync("dwh", dwh)

    for html in HTMLS:
        if not html.exists():
            continue
        t = html.read_text(encoding="utf-8")
        t2 = re.sub(
            r'const KG_DATA_VER = "[^"]+"',
            'const KG_DATA_VER = "20260922e"',
            t,
            count=1,
        )
        html.write_text(t2, encoding="utf-8")

    c2 = find(dwh, "dwh-path-senior")["content"]
    block = c2.split("### 必学顺序")[1].split("###")[0]
    print("ORDER_BLOCK:")
    print(block)
    print("HAS_SEC", "dwh-lakehouse-sec" in block)


if __name__ == "__main__":
    main()
