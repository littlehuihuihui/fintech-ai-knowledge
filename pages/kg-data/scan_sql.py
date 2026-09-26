#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

filepath = r"D:\cursor\数据学习平台\kg-data\embed-sql.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["sql"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def count_leaves(node):
    if not node.get("children") or len(node["children"]) == 0:
        return 1
    return sum(count_leaves(c) for c in node["children"])

def print_tree(node, depth=0):
    prefix = "  " * depth
    leaves = count_leaves(node) if node.get("children") else 1
    content_len = len(node.get("content", ""))
    print(f"{prefix}{node.get('title', '?')} ({leaves}叶, {content_len}字符) [id={node.get('id','?')}]")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

print("=" * 60)
print("SQL 知识图谱结构")
print("=" * 60)
print_tree(data)
