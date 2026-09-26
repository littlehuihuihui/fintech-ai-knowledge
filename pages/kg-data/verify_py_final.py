#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def count_leaves(node):
    if not node.get("children") or len(node["children"]) == 0:
        return 1
    return sum(count_leaves(c) for c in node["children"])

def print_tree(node, depth=0):
    prefix = "  " * depth
    leaves = count_leaves(node) if node.get("children") else 1
    print(f"{prefix}{node.get('title', '?')} ({leaves}叶)")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

print("=" * 60)
print("Python 知识图谱最终结构")
print("=" * 60)
print_tree(data)

total = count_leaves(data)
print(f"\n总叶子数: {total}")

# 检查常用库章节
libs = None
for child in data["children"]:
    if child.get("id") == "py-libs":
        libs = child
        break

if libs:
    print(f"\n常用库章节: {len(libs['children'])} 个库")
    for lib in libs["children"]:
        content_len = len(lib.get("content", ""))
        print(f"  - {lib['title']}: {content_len} 字符")
