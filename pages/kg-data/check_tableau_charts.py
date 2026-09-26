#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, os

filepath = r"D:\cursor\数据学习平台\tableau-data\embed-tableau.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["tableau"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def print_tree(node, depth=0):
    prefix = "  " * depth
    content_len = len(node.get("content", ""))
    children_count = len(node.get("children", []))
    print(f"{prefix}{node.get('id', '?')} | {node.get('title', '?')} | {content_len}字符 | {children_count}子节点")
    for child in node.get("children", []):
        print_tree(child, depth + 1)

print("=" * 70)
print("Tableau 知识图谱完整结构")
print("=" * 70)
print_tree(data)

# 检查图表制作章节
print("\n" + "=" * 70)
print("图表制作相关节点详情")
print("=" * 70)

def find_node(node, keyword):
    if keyword in node.get("title", "") or keyword in node.get("id", ""):
        return node
    for child in node.get("children", []):
        result = find_node(child, keyword)
        if result:
            return result
    return None

chart_node = find_node(data, "图表")
if chart_node:
    print(f"\n找到节点: {chart_node['title']}")
    print_tree(chart_node)
    
    # 打印每个叶子的 content 前200字
    print("\n--- 各叶子内容预览 ---")
    def get_leaves(node, leaves=None):
        if leaves is None:
            leaves = []
        if not node.get("children") or len(node["children"]) == 0:
            leaves.append(node)
        else:
            for child in node["children"]:
                get_leaves(child, leaves)
        return leaves
    
    leaves = get_leaves(chart_node)
    for leaf in leaves:
        print(f"\n【{leaf['title']}】({len(leaf['content'])}字符)")
        print(leaf["content"][:300])
        print("...")
else:
    print("未找到图表制作节点")

# 搜索图表类型关键词
print("\n" + "=" * 70)
print("图表类型覆盖检查")
print("=" * 70)

all_content = ""
def collect_content(node):
    global all_content
    all_content += node.get("content", "") + " " + node.get("title", "") + " "
    for child in node.get("children", []):
        collect_content(child)

collect_content(data)

chart_types = [
    "条形图", "柱状图", "折线图", "面积图", "饼图", "环形图",
    "散点图", "气泡图", "树地图", "热力图", "词云", "箱线图",
    "甘特图", "子弹图", "标靶图", "漏斗图", "桑基图", "和弦图",
    "地图", "填充地图", "符号地图", "密度地图", "路径地图",
    "双轴图", "组合图", "多轴图", "小倍数", "小型多图",
    "帕累托图", "控制图", "瀑布图", "凹凸图", "斜坡图",
    "雷达图", "极坐标图", "直方图", "盒须图", "小提琴图",
    "动态图", "动画", "参数", "集", "详细级别表达式", "LOD",
    "仪表板", "交互", "筛选器", "操作", "突出显示", "工具提示",
    "格式", "配色", "字体", "样式", "模板"
]

print(f"{'图表类型':<15} {'标题中':<8} {'内容中':<8} {'状态'}")
print("-" * 55)
for ct in chart_types:
    in_title = ct in data.get("title", "") or any(ct in c.get("title", "") for c in data.get("children", []))
    # 更全面的标题搜索
    all_titles = ""
    def collect_titles(node):
        global all_titles
        all_titles += node.get("title", "") + " "
        for child in node.get("children", []):
            collect_titles(child)
    collect_titles(data)
    
    in_title = ct in all_titles
    in_content = ct in all_content
    status = "✓ 有独立节点" if in_title else ("△ 仅内容提及" if in_content else "✗ 缺失")
    print(f"{ct:<15} {'✓' if in_title else '✗':<8} {'✓' if in_content else '✗':<8} {status}")
