#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 add_py_libs.py 中的三引号嵌套问题"""

filepath = r"D:\cursor\数据学习平台\kg-data\add_py_libs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 修复第一处：BeautifulSoup 示例中的 html = """ ... """
# 把这一段的三引号改成单引号三引号
old1 = '''# 方式1：从字符串解析
html = """
<html>
<head><title>测试页面</title></head>
<body>
  <h1 class="title">欢迎来到数据学习平台</h1>
  <div class="content">
    <p class="intro">这是一个段落。</p>
    <ul id="list">
      <li class="item">第一项</li>
      <li class="item">第二项</li>
      <li class="item special">第三项</li>
    </ul>
    <a href="https://example.com" id="link1">链接1</a>
    <a href="https://example.com/page2">链接2</a>
  </div>
  <table>
    <tr><th>姓名</th><th>年龄</th></tr>
    <tr><td>张三</td><td>25</td></tr>
    <tr><td>李四</td><td>30</td></tr>
  </table>
</body>
</html>
"""'''

new1 = '''# 方式1：从字符串解析
html = \\'\\'\\'
<html>
<head><title>测试页面</title></head>
<body>
  <h1 class="title">欢迎来到数据学习平台</h1>
  <div class="content">
    <p class="intro">这是一个段落。</p>
    <ul id="list">
      <li class="item">第一项</li>
      <li class="item">第二项</li>
      <li class="item special">第三项</li>
    </ul>
    <a href="https://example.com" id="link1">链接1</a>
    <a href="https://example.com/page2">链接2</a>
  </div>
  <table>
    <tr><th>姓名</th><th>年龄</th></tr>
    <tr><td>张三</td><td>25</td></tr>
    <tr><td>李四</td><td>30</td></tr>
  </table>
</body>
</html>
\\'\\'\\''''

if old1 in content:
    content = content.replace(old1, new1)
    print("✓ 第一处修复成功（BeautifulSoup html 示例）")
else:
    print("✗ 第一处未找到")

# 修复第二处：pd.read_sql(""" ... """)
old2 = '''df = pd.read_sql("""
    SELECT order_id, user_id, amount, order_date
    FROM orders
    WHERE order_date >= '2024-01-01'
""", source_engine)'''

new2 = '''df = pd.read_sql(\\'\\'\\'
    SELECT order_id, user_id, amount, order_date
    FROM orders
    WHERE order_date >= '2024-01-01'
\\'\\'\\', source_engine)'''

if old2 in content:
    content = content.replace(old2, new2)
    print("✓ 第二处修复成功（pd.read_sql 示例）")
else:
    print("✗ 第二处未找到")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("\n修复完成，文件已保存")
