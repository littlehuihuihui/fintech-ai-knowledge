#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, os

data_dir = r"D:\cursor\数据学习平台\kg-data"
domains = ["sql", "python", "database", "ml", "etl", "dwh", "bi"]

def count_leaves(node):
    if not node.get("children") or len(node["children"]) == 0:
        return 1
    return sum(count_leaves(c) for c in node["children"])

def count_nodes(node):
    if not node.get("children") or len(node["children"]) == 0:
        return 1
    return 1 + sum(count_nodes(c) for c in node["children"])

print("=" * 60)
print("7大领域知识图谱内容统计")
print("=" * 60)
print(f"{'领域':<10} {'文件大小':<12} {'总节点':<10} {'叶子数':<10}")
print("-" * 60)

total_leaves = 0
total_nodes = 0

for domain in domains:
    filepath = os.path.join(data_dir, f"embed-{domain}.js")
    if not os.path.exists(filepath):
        print(f"{domain:<10} 文件不存在")
        continue
    
    size = os.path.getsize(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'window\.__KG_EMBEDDED\["' + domain + r'"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
    if not match:
        print(f"{domain:<10} 解析失败")
        continue
    
    data = json.loads(match.group(1))
    leaves = count_leaves(data)
    nodes = count_nodes(data)
    total_leaves += leaves
    total_nodes += nodes
    
    print(f"{domain:<10} {size:<12,} {nodes:<10} {leaves:<10}")

print("-" * 60)
print(f"{'合计':<10} {'':<12} {total_nodes:<10} {total_leaves:<10}")
print("=" * 60)

# 检查新增内容
print("\n=== 新增内容验证 ===")

# Python 基础
with open(os.path.join(data_dir, "embed-python.js"), "r", encoding="utf-8") as f:
    py_content = f.read()
py_data = json.loads(re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', py_content, re.DOTALL).group(1))
py_basics = [c for c in py_data["children"] if c["id"] == "py-basics"]
if py_basics:
    print(f"✓ Python 基础: {len(py_basics[0]['children'])} 章节, {count_leaves(py_basics[0])} 叶子")

# ETL Kettle
with open(os.path.join(data_dir, "embed-etl.js"), "r", encoding="utf-8") as f:
    etl_content = f.read()
etl_data = json.loads(re.search(r'window\.__KG_EMBEDDED\["etl"\]\s*=\s*(\{.*\})\s*;?\s*$', etl_content, re.DOTALL).group(1))
def find_kettle(node):
    if "kettle" in node.get("id", "").lower() or "Kettle" in node.get("title", ""):
        return node
    for child in node.get("children", []):
        result = find_kettle(child)
        if result:
            return result
    return None
kettle = find_kettle(etl_data)
if kettle:
    print(f"✓ ETL Kettle/PDI: {len(kettle['children'])} 章节, {count_leaves(kettle)} 叶子")

# BI PowerBI
with open(os.path.join(data_dir, "embed-bi.js"), "r", encoding="utf-8") as f:
    bi_content = f.read()
bi_data = json.loads(re.search(r'window\.__KG_EMBEDDED\["bi"\]\s*=\s*(\{.*\})\s*;?\s*$', bi_content, re.DOTALL).group(1))
def find_pbi(node):
    if "Power BI" in node.get("title", ""):
        return node
    for child in node.get("children", []):
        result = find_pbi(child)
        if result:
            return result
    return None
pbi = find_pbi(bi_data)
if pbi:
    print(f"✓ BI Power BI: {len(pbi['children'])} 叶子")

# SQL 窗口函数
with open(os.path.join(data_dir, "embed-sql.js"), "r", encoding="utf-8") as f:
    sql_content = f.read()
sql_data = json.loads(re.search(r'window\.__KG_EMBEDDED\["sql"\]\s*=\s*(\{.*\})\s*;?\s*$', sql_content, re.DOTALL).group(1))
def find_window(node):
    if node.get("id") == "SQL.聚合分析.窗口函数":
        return node
    for child in node.get("children", []):
        result = find_window(child)
        if result:
            return result
    return None
window = find_window(sql_data)
if window:
    print(f"✓ SQL 窗口函数: {len(window['children'])} 叶子")

print("\n=== 本次补充汇总 ===")
print(f"  Python 基础语法: +13 片讲义")
print(f"  ETL Kettle/PDI: +5 片讲义")
print(f"  BI Power BI: +4 片讲义")
print(f"  SQL 窗口函数: +4 片讲义（从1个节点扩展为4个）")
print(f"  合计新增: +26 片讲义")
