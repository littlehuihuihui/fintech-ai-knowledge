#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-sql.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["sql"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
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

# 找聚合分析节点
agg = find_node(data, "聚合分析")
if agg:
    print("=== 聚合分析子树 ===")
    print_tree(agg)
