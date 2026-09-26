#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

print("Root:", data["title"])
print("Children:", [c["title"] for c in data["children"]])

basics = [c for c in data["children"] if c["id"] == "py-basics"][0]
print("\nPython 基础 chapters:")
for ch in basics["children"]:
    leaves = [l["title"] for l in ch["children"]]
    print(f"  {ch['title']} ({len(leaves)} leaves): {leaves}")

# 统计总叶子数
def count_leaves(node):
    if not node.get("children"):
        return 1
    return sum(count_leaves(c) for c in node["children"])

total = count_leaves(data)
print(f"\nTotal leaves in Python tree: {total}")
