#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-bi.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["bi"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def find_node(node, keyword):
    if keyword in node.get("title", "") or keyword in node.get("id", ""):
        return node
    for child in node.get("children", []):
        result = find_node(child, keyword)
        if result:
            return result
    return None

def print_tree(node, depth=0):
    prefix = "  " * depth
    has_content = "有讲义" if len(node.get("content", "")) > 50 else "无讲义"
    print(f"{prefix}{node.get('id', '?')} | {node.get('title', '?')} | {has_content}")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

pbi = find_node(data, "Power BI")
if pbi:
    print("=== Power BI 子树 ===")
    print_tree(pbi)
else:
    print("Not found Power BI")
    print("\n=== BI 一级节点 ===")
    for child in data.get("children", []):
        print(f"  {child.get('id')} | {child.get('title')}")
