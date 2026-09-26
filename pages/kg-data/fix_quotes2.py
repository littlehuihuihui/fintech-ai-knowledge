#!/usr/bin/env python3
# -*- coding: utf-8 -*-
filepath = r"D:\cursor\数据学习平台\kg-data\add_py_libs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 修复1: BeautifulSoup 示例中的 html = """
content = content.replace(
    "# 方式1：从字符串解析\nhtml = \"\"\"\n<html>",
    "# 方式1：从字符串解析\nhtml = '''\n<html>"
)
content = content.replace(
    "</html>\n\"\"\"\nsoup = BeautifulSoup(html,",
    "</html>\n'''\nsoup = BeautifulSoup(html,"
)

# 修复2: pd.read_sql("""
content = content.replace(
    "df = pd.read_sql(\"\"\"\n    SELECT order_id",
    "df = pd.read_sql('''\n    SELECT order_id"
)
content = content.replace(
    "WHERE order_date >= '2024-01-01'\n\"\"\", source_engine)",
    "WHERE order_date >= '2024-01-01'\n''', source_engine)"
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("修复完成")
