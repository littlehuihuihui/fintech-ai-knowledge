#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步BI领域Tableau图表制作为26图版本"""

import json, re

# 1. 从 embed-tableau.js 读取26图版本的图表制作节点
tableau_path = r"D:\cursor\数据学习平台\tableau-data\embed-tableau.js"
with open(tableau_path, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["tableau"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
tableau_data = json.loads(match.group(1))

def find_node(node, node_id):
    if node.get("id") == node_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result:
            return result
    return None

chart_node_26 = find_node(tableau_data, "Tableau.图表制作")
print(f"独立Tableau图谱的图表制作节点: {len(chart_node_26['children'])} 子章节")
for ch in chart_node_26["children"]:
    print(f"  - {ch['title']}: {len(ch['children'])} 图")

# 2. 修改节点id前缀：Tableau.图表制作 → BI.Tableau.图表制作
#    因为BI领域下的节点id是 BI.Tableau.xxx 格式
def update_ids(node, old_prefix, new_prefix):
    if node.get("id"):
        node["id"] = node["id"].replace(old_prefix, new_prefix)
    for child in node.get("children", []):
        update_ids(child, old_prefix, new_prefix)

update_ids(chart_node_26, "Tableau.图表制作", "BI.Tableau.图表制作")
print(f"\n更新后根节点id: {chart_node_26['id']}")

# 3. 读取 embed-bi.js
bi_path = r"D:\cursor\数据学习平台\kg-data\embed-bi.js"
with open(bi_path, "r", encoding="utf-8") as f:
    bi_content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["bi"\]\s*=\s*(\{.*\})\s*;?\s*$', bi_content, re.DOTALL)
bi_data = json.loads(match.group(1))

# 4. 找到BI领域下的Tableau节点，然后找到其下的图表制作节点
def find_node_by_title(node, title):
    if node.get("title") == title:
        return node
    for child in node.get("children", []):
        result = find_node_by_title(child, title)
        if result:
            return result
    return None

tableau_node_bi = find_node_by_title(bi_data, "Tableau")
print(f"\nBI领域下的Tableau节点: {len(tableau_node_bi['children'])} 子节点")

# 找到旧的图表制作节点并替换
old_chart_idx = None
for i, child in enumerate(tableau_node_bi["children"]):
    if child.get("title") == "图表制作":
        old_chart_idx = i
        print(f"旧图表制作节点位置: index={i}, {len(child['children'])} 子节点")
        break

if old_chart_idx is not None:
    tableau_node_bi["children"][old_chart_idx] = chart_node_26
    print(f"已替换为26图版本: {len(chart_node_26['children'])} 子章节")
else:
    print("ERROR: 未找到旧图表制作节点")
    exit(1)

# 5. 保存
new_json_str = json.dumps(bi_data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["bi"]={new_json_str}\n'

with open(bi_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-bi.js size: {len(new_content)} bytes")
print("BI领域Tableau图表制作已同步为26图版本！")
