#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

filepath = r"D:\cursor\数据学习平台\kg-data\embed-sql.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["sql"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def find_node(node, node_id):
    if node.get("id") == node_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result:
            return result
    return None

# 读取窗口函数4个子节点的内容
for nid in ["SQL.聚合分析.窗口函数.排名函数", "SQL.聚合分析.窗口函数.聚合窗口", 
            "SQL.聚合分析.窗口函数.偏移函数", "SQL.聚合分析.窗口函数.窗口定义"]:
    node = find_node(data, nid)
    print("=" * 70)
    print(f"【{node['title']}】({len(node['content'])}字符)")
    print("=" * 70)
    print(node['content'])
    print()
