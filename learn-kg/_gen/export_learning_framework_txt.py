# -*- coding: utf-8 -*-
"""Export learning-framework outline of all KG hubs to Desktop TXT for review."""
from __future__ import annotations

import json
import re
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


def load_tree(hub_id: str, hub_file: str, fallback: str):
    for name in (hub_file, fallback):
        p = KG / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(hub_id)


def summarize_content(content: str, max_chars: int = 420) -> str:
    text = (content or "").strip()
    if not text:
        return "【空】暂无讲义正文"
    # strip code fences to keep outline readable
    text = re.sub(r"```[\s\S]*?```", "[代码示例已省略]", text)
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("|---"):
            continue
        lines.append(s)
    joined = " ".join(lines)
    joined = re.sub(r"\s+", " ", joined)
    if len(joined) > max_chars:
        joined = joined[: max_chars - 1] + "…"
    return joined


def section_heads(content: str) -> list[str]:
    heads = []
    for m in re.finditer(r"^###\s+(.+)$", content or "", re.M):
        heads.append(m.group(1).strip())
    return heads


def walk(node, depth, path, rows):
    kids = node.get("children") or []
    is_leaf = len(kids) == 0
    title = node.get("title") or "?"
    nid = node.get("id") or ""
    level = node.get("level") or ""
    content = node.get("content") or ""
    kind = "叶讲义" if is_leaf else ("根总览" if depth == 1 else ("领域/章节" if depth <= 3 else "目录"))
    rows.append(
        {
            "depth": depth,
            "path": path + [title],
            "id": nid,
            "title": title,
            "level": level,
            "kind": kind,
            "is_leaf": is_leaf,
            "child_count": len(kids),
            "content_len": len(content),
            "heads": section_heads(content),
            "summary": summarize_content(content),
        }
    )
    for c in kids:
        walk(c, depth + 1, path + [title], rows)


def render_hub(hub_label: str, hub_id: str, tree: dict) -> str:
    rows = []
    walk(tree, 1, [], rows)
    leaves = [r for r in rows if r["is_leaf"]]
    nonleaves = [r for r in rows if not r["is_leaf"]]
    depths = sorted({r["depth"] for r in rows})
    lines = []
    lines.append("=" * 78)
    lines.append(f"学科：{hub_label}（hub_id={hub_id}）")
    lines.append(
        f"节点总数={len(rows)} | 叶讲义={len(leaves)} | 目录/章节={len(nonleaves)} | 最大层级=L{max(depths)}"
    )
    lines.append("=" * 78)
    lines.append("")
    lines.append("【层级说明】")
    lines.append("  L1 = 学科根（总览）")
    lines.append("  L2 = 一级领域 / 一级模块")
    lines.append("  L3 = 二级章节 / 主题")
    lines.append("  L4 = 三级主题或叶讲义")
    lines.append("  L5+ = 更深叶讲义（如 LOD.FIXED）")
    lines.append("  难度标记：? 初级 / ?? 中级 / ??? 高级（若有）")
    lines.append("")
    lines.append("【树形大纲】")
    for r in rows:
        indent = "  " * (r["depth"] - 1)
        mark = "◆" if r["is_leaf"] else "◇"
        lv = f" [{r['level']}]" if r["level"] else ""
        kids = "" if r["is_leaf"] else f"  (子节点 {r['child_count']})"
        lines.append(f"{indent}{mark} L{r['depth']} {r['title']}{lv} · {r['kind']}{kids}")
        lines.append(f"{indent}   id: {r['id']}")
    lines.append("")
    lines.append("【逐节点内容框架】（供审查：是否缺课、是否过浅、是否缺练习）")
    lines.append("")
    for r in rows:
        path_s = " / ".join(r["path"])
        lines.append("-" * 78)
        lines.append(f"L{r['depth']} | {r['kind']} | {path_s}")
        lines.append(f"node_id: {r['id']}")
        lines.append(f"难度: {r['level'] or '（未标）'} | 正文约 {r['content_len']} 字 | 子节点 {r['child_count']}")
        if r["heads"]:
            lines.append("讲义小节: " + " → ".join(r["heads"]))
        else:
            lines.append("讲义小节: （无 ### 标题，可能是短导读）")
        lines.append("内容摘要: " + r["summary"])
        if r["is_leaf"]:
            need = []
            if r["content_len"] < 500:
                need.append("正文偏短，建议补「怎么写/易错/动手」")
            heads_l = " ".join(r["heads"])
            if "动手" not in heads_l and "练习" not in heads_l:
                need.append("可能缺少动手/练习小节")
            if "易错" not in heads_l and "常见" not in heads_l:
                need.append("可能缺少易错对照")
            if need:
                lines.append("自检提示: " + "；".join(need))
            else:
                lines.append("自检提示: 结构基本完整（仍可按业务场景加厚）")
        else:
            if r["content_len"] < 200:
                lines.append("自检提示: 章节导读偏短，建议补地图/顺序/验收")
            else:
                lines.append("自检提示: 目录节点，检查是否写清学习顺序与下级地图")
        lines.append("")
    return "\n".join(lines)


def main():
    parts = []
    parts.append("DATA NEXUS 学习平台 · 知识图谱学习框架导出")
    parts.append("用途：交给 DeepSeek 审查「缺什么 / 哪些节点过浅 / 教程结构是否完整」")
    parts.append("导出源：D:\\cursor\\数据学习平台\\kg-data")
    parts.append("")
    parts.append("请重点审查：")
    parts.append("1) 每个学科 L1→叶节点的学习路径是否闭环")
    parts.append("2) 叶讲义是否具备：目标、概念、做法、易错、动手、验收")
    parts.append("3) 章节导读是否有地图与推荐顺序")
    parts.append("4) 难度标记 ?/??/??? 是否合理")
    parts.append("5) SQL/BI 与 Python/数仓等是否口径一致（统一样例）")
    parts.append("")
    parts.append("")

    totals = []
    for hub_id, label, hub_file, fallback in HUBS:
        tree = load_tree(hub_id, hub_file, fallback)
        parts.append(render_hub(label, hub_id, tree))
        rows = []
        walk(tree, 1, [], rows)
        totals.append((label, len(rows), sum(1 for r in rows if r["is_leaf"]), max(r["depth"] for r in rows)))

    parts.append("=" * 78)
    parts.append("汇总")
    parts.append("=" * 78)
    for label, n, leaves, depth in totals:
        parts.append(f"- {label}: 节点 {n}，叶讲义 {leaves}，最深 L{depth}")
    parts.append("")
    parts.append("（完）")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print("wrote", OUT)
    print("bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
