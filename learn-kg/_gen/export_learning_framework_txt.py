# -*- coding: utf-8 -*-
"""Export full KG lesson content to Desktop TXT for external review."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

KG = Path(r"D:\cursor\数据学习平台\kg-data")
OUT = Path.home() / "Desktop" / "学习平台_知识图谱学习框架.txt"

HUBS = [
    ("sql", "SQL", "hub-query.json", "sql.json"),
    ("bi", "BI", "hub-viz.json", "bi.json"),
    ("python", "Python", "hub-python.json", "python.json"),
    ("database", "数据库", "hub-database.json", "database.json"),
    ("ml", "机器学习/算法", "hub-ml.json", "ml.json"),
    ("etl", "ETL", "hub-etl.json", "etl.json"),
    ("dwh", "数据仓库", "hub-dwh.json", "dwh.json"),
]


def load_tree(hub_file: str, fallback: str):
    for name in (hub_file, fallback):
        p = KG / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(hub_file)


def walk(node, depth, path, rows):
    kids = node.get("children") or []
    title = node.get("title") or "?"
    rows.append(
        {
            "depth": depth,
            "path": path + [title],
            "id": node.get("id") or "",
            "title": title,
            "level": node.get("level") or "",
            "is_leaf": len(kids) == 0,
            "child_count": len(kids),
            "content": (node.get("content") or "").rstrip(),
        }
    )
    for c in kids:
        walk(c, depth + 1, path + [title], rows)


def render_hub(hub_label: str, hub_id: str, tree: dict) -> str:
    rows = []
    walk(tree, 1, [], rows)
    leaves = sum(1 for r in rows if r["is_leaf"])
    lines = []
    lines.append("=" * 78)
    lines.append(f"【{hub_label}】 hub_id={hub_id}")
    lines.append(f"节点={len(rows)} | 叶讲义={leaves} | 最深=L{max(r['depth'] for r in rows)}")
    lines.append("=" * 78)
    lines.append("")

    # tree outline (titles only)
    lines.append("【目录树】")
    for r in rows:
        indent = "  " * (r["depth"] - 1)
        mark = "●" if r["is_leaf"] else "○"
        lv = f" [{r['level']}]" if r["level"] else ""
        kid = "" if r["is_leaf"] else f" · {r['child_count']}子"
        lines.append(f"{indent}{mark} {r['title']}{lv} ({r['id']}){kid}")
    lines.append("")
    lines.append("【正文】")
    lines.append("")

    for r in rows:
        path_s = " / ".join(r["path"])
        kind = "叶讲义" if r["is_leaf"] else ("根" if r["depth"] == 1 else "章节/目录")
        lines.append("-" * 78)
        lines.append(f"{kind} | L{r['depth']} | {path_s}")
        lines.append(f"node_id: {r['id']}")
        lines.append(f"难度: {r['level'] or '（未标）'}")
        lines.append("")
        body = r["content"].strip()
        if body:
            lines.append(body)
        else:
            lines.append("（本节点暂无正文）")
        lines.append("")
    return "\n".join(lines)


def main():
    parts = []
    parts.append("DATA NEXUS 学习平台 · 知识图谱全文导出")
    parts.append(f"导出日期：{date.today().isoformat()}")
    parts.append("说明：以下为各学科节点的完整讲义正文（含代码与表格），供内容复查。")
    parts.append("难度标记：? 初级 / ?? 中级 / ??? 高级")
    parts.append("同源样例约定：users / orders / order_items / order_events")
    parts.append("")

    totals = []
    for hub_id, label, hub_file, fallback in HUBS:
        tree = load_tree(hub_file, fallback)
        parts.append(render_hub(label, hub_id, tree))
        rows = []
        walk(tree, 1, [], rows)
        totals.append(
            (
                label,
                len(rows),
                sum(1 for r in rows if r["is_leaf"]),
                max(r["depth"] for r in rows),
            )
        )

    parts.append("=" * 78)
    parts.append("【汇总】")
    parts.append("=" * 78)
    for label, n, leaves, depth in totals:
        parts.append(f"- {label}: 节点 {n}，叶讲义 {leaves}，最深 L{depth}")
    parts.append("")
    parts.append("（全文结束）")

    text = "\n".join(parts)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT)
    print("chars", len(text))
    print("bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
