#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-ml.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["ml"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def print_tree(node, depth=0):
    prefix = "  " * depth
    has_content = "有讲义" if len(node.get("content", "")) > 50 else "无讲义"
    print(f"{prefix}{node.get('id', '?')} | {node.get('title', '?')} | {has_content}")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

for child in data.get("children", []):
    cid = child.get("id", "")
    if cid in ["ml-models", "ml-eval-ops", "ml-foundation", "ml-tasks"]:
        print(f"\n=== {child['title']} ===")
        print_tree(child)
