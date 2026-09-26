#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核查 Python 知识图谱中的库覆盖情况"""

import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def print_tree(node, depth=0):
    prefix = "  " * depth
    has_content = "有讲义" if len(node.get("content", "")) > 100 else "无讲义/短"
    children_count = len(node.get("children", []))
    print(f"{prefix}{node.get('id', '?')} | {node.get('title', '?')} | {has_content} | {children_count}子节点")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

print("=" * 70)
print("Python 知识图谱完整结构")
print("=" * 70)
print_tree(data)

# 统计每个叶子的 content 长度
print("\n" + "=" * 70)
print("各叶子讲义详细程度（content 字符数）")
print("=" * 70)

def get_leaves(node, leaves=None):
    if leaves is None:
        leaves = []
    if not node.get("children") or len(node["children"]) == 0:
        leaves.append(node)
    else:
        for child in node["children"]:
            get_leaves(child, leaves)
    return leaves

leaves = get_leaves(data)
print(f"总叶子数: {len(leaves)}")
print(f"\n按内容长度排序（最短的在前，可能需要补充）:")
sorted_leaves = sorted(leaves, key=lambda x: len(x.get("content", "")))
for leaf in sorted_leaves[:20]:
    print(f"  {len(leaf.get('content', '')):>6} 字符 | {leaf['title']}")

# 搜索库相关关键词
print("\n" + "=" * 70)
print("库相关关键词覆盖检查")
print("=" * 70)

all_titles = " ".join([n.get("title", "") for n in leaves])
all_content = " ".join([n.get("content", "") for n in leaves])
all_text = all_titles + " " + all_content

libs_to_check = [
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "scikit-learn", "sklearn", "scipy", "statsmodels",
    "requests", "beautifulsoup", "bs4", "selenium", "scrapy",
    "flask", "django", "fastapi",
    "openpyxl", "xlrd", "xlsxwriter", "pymysql", "psycopg2",
    "sqlalchemy", "pymongo", "redis",
    "os", "sys", "re", "json", "csv", "datetime", "time",
    "collections", "itertools", "functools", "pathlib",
    "typing", "dataclasses", "logging", "unittest", "pytest",
    "threading", "multiprocessing", "asyncio",
    "git", "pip", "venv", "conda", "jupyter", "virtualenv"
]

print(f"{'库名':<20} {'标题中':<8} {'内容中':<8} {'状态'}")
print("-" * 60)
for lib in libs_to_check:
    in_title = lib.lower() in all_titles.lower()
    in_content = lib.lower() in all_content.lower()
    status = "✓ 有独立节点" if in_title else ("△ 仅内容提及" if in_content else "✗ 缺失")
    print(f"{lib:<20} {'✓' if in_title else '✗':<8} {'✓' if in_content else '✗':<8} {status}")
