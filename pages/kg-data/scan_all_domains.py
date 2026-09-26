#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描7大领域知识图谱完整结构"""

import json, re

domains = {
    "sql": "SQL",
    "python": "Python",
    "database": "数据库",
    "ml": "机器学习",
    "etl": "ETL",
    "dwh": "数据仓库",
    "bi": "BI",
}

def count_leaves(node):
    if not node.get("children") or len(node["children"]) == 0:
        return 1
    return sum(count_leaves(c) for c in node["children"])

def print_tree(node, depth=0, max_depth=3):
    if depth > max_depth:
        return
    prefix = "  " * depth
    leaves = count_leaves(node) if node.get("children") else 1
    content_len = len(node.get("content", ""))
    child_count = len(node.get("children", []))
    print(f"{prefix}{node.get('title', '?')} ({child_count}子/{leaves}叶, {content_len}字)")
    for child in node.get("children", []):
        print_tree(child, depth + 1, max_depth)

for key, name in domains.items():
    filepath = rf"D:\cursor\数据学习平台\kg-data\embed-{key}.js"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(rf'window\.__KG_EMBEDDED\["{key}"\]\s*=\s*(\{{.*\}})\s*;?\s*$', content, re.DOTALL)
    if not match:
        print(f"ERROR: {name} 解析失败")
        continue
    data = json.loads(match.group(1))
    
    total = count_leaves(data)
    print("\n" + "=" * 70)
    print(f"【{name}】总叶子数: {total}")
    print("=" * 70)
    print_tree(data, max_depth=3)
