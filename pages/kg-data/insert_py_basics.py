#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 Python 基础模块插入到 embed-python.js"""

import json
import re

# 读取生成的 Python 基础节点
with open(r"D:\cursor\数据学习平台\kg-data\py-basics-temp.json", "r", encoding="utf-8") as f:
    py_basics = json.load(f)

# 读取 embed-python.js
with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "r", encoding="utf-8") as f:
    content = f.read()

# 提取 JSON 部分
# 格式：window.__KG_EMBEDDED["python"]={...JSON...}
match = re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
if not match:
    print("ERROR: Cannot find JSON in embed-python.js")
    exit(1)

json_str = match.group(1)
data = json.loads(json_str)

print(f"Original children count: {len(data['children'])}")
print(f"Original children titles: {[c['title'] for c in data['children']]}")

# 检查是否已经存在 py-basics
existing_ids = [c['id'] for c in data['children']]
if 'py-basics' in existing_ids:
    print("py-basics already exists, replacing...")
    data['children'] = [c for c in data['children'] if c['id'] != 'py-basics']

# 插入到"学习路径"之后，"pandas 数据表"之前
new_children = []
inserted = False
for child in data['children']:
    new_children.append(child)
    if child['id'] == 'py-learning-path' and not inserted:
        new_children.append(py_basics)
        inserted = True
        print(f"Inserted py-basics after {child['id']}")

if not inserted:
    # 如果没找到学习路径，就插到最前面
    new_children.insert(0, py_basics)
    print("Inserted py-basics at beginning")

data['children'] = new_children
print(f"New children count: {len(data['children'])}")
print(f"New children titles: {[c['title'] for c in data['children']]}")

# 更新根节点的 content 中的领域地图和推荐主线
root_content = data['content']

# 更新一级领域地图表格
old_table_row = "| 学习路径 | 先统一样例与路线，避免「今天用表 A、明天用表 B」导致口径对不上。 |"
new_table_row = """| 学习路径 | 先统一样例与路线，避免「今天用表 A、明天用表 B」导致口径对不上。 |
| Python 基础 | 语法、控制流、函数、数据结构——pandas 之前的基本功。 |"""
root_content = root_content.replace(old_table_row, new_table_row)

# 更新推荐主线
old_main = "```text\n学习路径 → pandas 数据表 → 可视化 → 生态与加速\n```"
new_main = "```text\n学习路径 → Python 基础 → pandas 数据表 → 可视化 → 生态与加速\n```"
root_content = root_content.replace(old_main, new_main)

# 更新体量（原27叶，新增13叶）
root_content = root_content.replace("本树约 **27** 片叶讲义", "本树约 **40** 片叶讲义")

data['content'] = root_content

# 序列化回 JSON
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# 构造完整的 JS 文件内容
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["python"]={new_json_str}\n'

# 写入文件
with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! File size: {len(new_content)} bytes")
print("Python 基础模块已成功插入 embed-python.js")
