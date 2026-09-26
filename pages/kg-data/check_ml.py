#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-ml.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["ml"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def print_tree(node, depth=0):
    prefix = "  " * depth
    print(f"{prefix}{node.get('id', '?')} | {node.get('title', '?')}")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

print("=== ML 一级节点 ===")
for child in data.get("children", []):
    print(f"  {child.get('id')} | {child.get('title')} ({len(child.get('children', []))} 子节点)")
