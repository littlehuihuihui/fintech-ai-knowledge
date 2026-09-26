#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-etl.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["etl"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def print_tree(node, depth=0):
    prefix = "  " * depth
    print(f"{prefix}{node.get('id', '?')} | {node.get('title', '?')}")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

# 只打印工具选型部分
def find_node(node, keyword):
    if keyword in node.get("title", "") or keyword in node.get("id", ""):
        return node
    for child in node.get("children", []):
        result = find_node(child, keyword)
        if result:
            return result
    return None

tool_node = find_node(data, "工具选型")
if tool_node:
    print("=== 工具选型子树 ===")
    print_tree(tool_node)
else:
    print("Not found 工具选型")
    print("\n=== 全部一级节点 ===")
    for child in data.get("children", []):
        print(f"  {child.get('id')} | {child.get('title')}")
