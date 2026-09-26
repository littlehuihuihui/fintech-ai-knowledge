#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充 Python 核心库详细教程：requests+BS4、scipy、plotly、openpyxl、数据库连接"""

import json, re

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

# ========== 1. requests + BeautifulSoup 数据采集 ==========
leaf_requests = make_leaf("py-lib-requests", "requests 网络请求", "??", """### 课前

- **场景**：需要从网页 API 获取数据、下载文件、提交表单，是数据分析的数据来源第一步。
- **目标**：掌握 requests 库的 GET/POST 请求、参数传递、请求头、响应处理、会话保持、异常处理。
- **先修**：Python 基础、JSON 基础

### 是什么

- **一句话定义**：requests 是 Python 最流行的 HTTP 客户端库，用简洁优雅的 API 发送各种 HTTP 请求，是网络数据采集、API 调用的标配工具。
- 官方口号："HTTP for Humans"（给人类用的 HTTP 库），比内置 urllib 简单太多。

### 怎么写

```python
import requests

# ===== 1. 基础 GET 请求 =====
response = requests.get("https://api.example.com/users")
print(response.status_code)   # 200
print(response.text)          # 响应文本（字符串）
print(response.json())        # 响应 JSON（自动解析为字典）
print(response.headers)       # 响应头
print(response.encoding)      # 编码

# 带 URL 参数
params = {"page": 1, "size": 20, "category": "tech"}
response = requests.get("https://api.example.com/articles", params=params)
# 实际请求 URL: https://api.example.com/articles?page=1&size=20&category=tech

# 带请求头（模拟浏览器、传 Token）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Authorization": "Bearer your_token_here",
    "Accept": "application/json"
}
response = requests.get("https://api.example.com/data", headers=headers)

# ===== 2. POST 请求 =====
# 表单数据
data = {"username": "admin", "password": "123456"}
response = requests.post("https://api.example.com/login", data=data)

# JSON 数据（最常用）
payload = {"name": "张三", "age": 25, "email": "zhangsan@example.com"}
response = requests.post("https://api.example.com/users", json=payload)
# json= 参数会自动设置 Content-Type: application/json 并序列化

# 上传文件
files = {"file": open("report.pdf", "rb")}
response = requests.post("https://api.example.com/upload", files=files)
files["file"].close()  # 记得关闭文件

# ===== 3. 其他 HTTP 方法 =====
requests.put("https://api.example.com/users/1", json={"name": "李四"})     # 更新
requests.patch("https://api.example.com/users/1", json={"age": 26})         # 部分更新
requests.delete("https://api.example.com/users/1")                            # 删除
requests.head("https://api.example.com/users")                                # 只获取响应头
requests.options("https://api.example.com/users")                             # 获取支持的方法

# ===== 4. 响应处理 =====
response = requests.get("https://api.example.com/data")

# 检查请求是否成功（状态码 200-299）
if response.ok:
    print("请求成功")
else:
    print(f"请求失败: {response.status_code}")

# 抛出异常（如果状态码是 4xx/5xx）
response.raise_for_status()  # 失败会抛出 requests.exceptions.HTTPError

# 二进制内容（下载图片/文件）
response = requests.get("https://example.com/image.jpg")
with open("image.jpg", "wb") as f:
    f.write(response.content)  # response.content 是 bytes

# 流式下载大文件
response = requests.get("https://example.com/large_file.zip", stream=True)
with open("large_file.zip", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

# ===== 5. 会话保持（Session）=====
# 同一个 Session 内自动保持 Cookie，适合需要登录的场景
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# 登录
login_data = {"username": "admin", "password": "123456"}
session.post("https://api.example.com/login", data=login_data)

# 后续请求自动带上登录后的 Cookie
response = session.get("https://api.example.com/user/profile")
print(response.json())  # 已登录状态的数据

# ===== 6. 超时与重试 =====
# 超时设置（连接超时+读取超时）
try:
    response = requests.get("https://api.example.com/data", timeout=(5, 10))
    # (5, 10) = 连接超时5秒，读取超时10秒
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.ConnectionError:
    print("连接失败（网络问题/域名不存在）")
except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")

# 简单重试（3次）
for attempt in range(3):
    try:
        response = requests.get("https://api.example.com/data", timeout=10)
        response.raise_for_status()
        break
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        print(f"第 {attempt+1} 次尝试失败: {e}")
        if attempt == 2:
            print("全部重试失败")
            raise
        import time
        time.sleep(2 ** attempt)  # 指数退避：1秒、2秒、4秒

# ===== 7. 实际应用：调用公开 API =====
# 示例：调用天气 API
import json

api_key = "your_api_key"
city = "北京"
url = f"https://api.openweathermap.org/data/2.5/weather"
params = {"q": city, "appid": api_key, "units": "metric", "lang": "zh_cn"}

response = requests.get(url, params=params)
if response.ok:
    data = response.json()
    print(f"城市: {data['name']}")
    print(f"温度: {data['main']['temp']}°C")
    print(f"天气: {data['weather'][0]['description']}")
    print(f"湿度: {data['main']['humidity']}%")
```

### 常用 API 速查

| 功能 | 代码 |
|---|---|
| GET 请求 | `requests.get(url, params=..., headers=...)` |
| POST 表单 | `requests.post(url, data=...)` |
| POST JSON | `requests.post(url, json=...)` |
| 响应文本 | `response.text` |
| 响应 JSON | `response.json()` |
| 响应二进制 | `response.content` |
| 状态码 | `response.status_code` |
| 是否成功 | `response.ok` |
| 抛出异常 | `response.raise_for_status()` |
| 响应头 | `response.headers` |
| 会话 | `session = requests.Session()` |
| 超时 | `timeout=(connect, read)` |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 不设置超时 | 网络不好时程序永久卡住 | 始终设置 timeout，建议 (5, 10) |
| 不检查响应状态 | 直接 response.json() 可能报错 | 先检查 response.ok 或 raise_for_status() |
| 用 data= 传 JSON | 服务端收到的是表单格式 | 传 JSON 用 json= 参数，不要用 data= |
| 每次请求新建连接 | 性能差，Cookie 不保持 | 用 Session 对象复用连接和 Cookie |
| 忘记关闭上传文件 | 资源泄漏 | 用 with open() 或用完 close() |
| 硬编码 API Key | 安全风险 | 用环境变量 os.environ.get("API_KEY") |
| 不处理异常 | 网络波动时程序崩溃 | 用 try/except 捕获 Timeout/ConnectionError |

### 动手

1. 用 requests 调用一个公开 API（如 JSONPlaceholder 的 https://jsonplaceholder.typicode.com/users），获取并打印数据
2. 写一个带超时和3次重试的请求函数
3. 用 Session 模拟登录后访问需要登录的页面（可用 httpbin.org 测试）
""")

leaf_bs4 = make_leaf("py-lib-bs4", "BeautifulSoup 网页解析", "??", """### 课前

- **场景**：用 requests 获取了网页 HTML，需要从中提取标题、表格、链接等数据。
- **目标**：掌握 BeautifulSoup4 的解析器、标签查找、属性提取、文本获取、CSS 选择器。
- **先修**：requests 基础、HTML 基础

### 是什么

- **一句话定义**：BeautifulSoup4（bs4）是 Python 最流行的 HTML/XML 解析库，可以从网页源码中方便地提取标签、属性、文本，配合 requests 完成网页数据采集。
- 安装：`pip install beautifulsoup4 lxml`（lxml 是高性能解析器，建议一起装）

### 怎么写

```python
from bs4 import BeautifulSoup
import requests

# ===== 1. 创建 BeautifulSoup 对象 =====
# 方式1：从字符串解析
html = '''
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
'''
soup = BeautifulSoup(html, "lxml")  # 用 lxml 解析器（快）
# 也可以用 "html.parser"（Python内置，无需额外安装）

# 方式2：从网页获取
response = requests.get("https://example.com")
soup = BeautifulSoup(response.text, "lxml")

# ===== 2. 查找标签 =====
# find：找到第一个匹配的标签
title = soup.find("title")
print(title.text)  # 测试页面

h1 = soup.find("h1")
print(h1.text)  # 欢迎来到数据学习平台

# 按属性查找
first_link = soup.find("a", href="https://example.com")
special_li = soup.find("li", class_="special")  # class 是关键字，用 class_
list_ul = soup.find("ul", id="list")

# 按属性字典查找（更灵活）
soup.find("a", attrs={"href": "https://example.com", "id": "link1"})

# find_all：找到所有匹配的标签，返回列表
all_links = soup.find_all("a")
for link in all_links:
    print(link.text, link["href"])

all_items = soup.find_all("li", class_="item")
print(f"找到 {len(all_items)} 个 item")

# 限制返回数量
first_two = soup.find_all("li", limit=2)

# ===== 3. CSS 选择器（推荐，更强大简洁）=====
# select：用 CSS 选择器查找，返回列表
soup.select("title")          # 所有 title 标签
soup.select("h1.title")       # class="title" 的 h1
soup.select("#list")          # id="list" 的元素
soup.select("ul li")          # ul 下的所有 li（后代）
soup.select("ul > li")        # ul 的直接子 li
soup.select("li.special")     # class="special" 的 li
soup.select("a[href]")        # 有 href 属性的 a
soup.select("a#link1")        # id="link1" 的 a
soup.select("tr:nth-child(2)")  # 第二个 tr

# select_one：只返回第一个匹配（类似 find）
first_p = soup.select_one("p.intro")
print(first_p.text)

# ===== 4. 提取内容 =====
# 文本内容
tag = soup.find("h1")
print(tag.text)          # 所有文本（含子标签的文本，合并）
print(tag.get_text())    # 同上，可加参数
print(tag.get_text(strip=True))  # 去除首尾空白
print(tag.string)        # 直接子文本（如果只有一个文本子节点）

# 属性
link = soup.find("a")
print(link["href"])           # 获取属性（不存在会报错）
print(link.get("href"))       # 安全获取（不存在返回 None）
print(link.get("class", []))  # 带默认值
print(link.attrs)             # 所有属性（字典）

# 多值属性（如 class）
li = soup.find("li", class_="special")
print(li["class"])  # ['item', 'special']（列表）

# ===== 5. 遍历文档树 =====
ul = soup.find("ul")
print(ul.contents)   # 直接子节点列表（含空白文本节点）
print(ul.children)   # 直接子节点迭代器
for child in ul.children:
    print(child)

print(ul.descendants)  # 所有后代节点迭代器
for desc in ul.descendants:
    print(desc)

# 父节点、兄弟节点
li = soup.find("li")
print(li.parent)        # 父节点（ul）
print(li.find_parent("div"))  # 向上查找第一个匹配的祖先
print(li.next_sibling)  # 下一个兄弟节点
print(li.previous_sibling)  # 上一个兄弟节点
print(li.find_next_sibling("li"))  # 下一个 li 兄弟

# ===== 6. 解析表格 =====
table = soup.find("table")
rows = table.find_all("tr")
for row in rows:
    cells = row.find_all(["th", "td"])
    row_data = [cell.get_text(strip=True) for cell in cells]
    print(row_data)
# 输出：
# ['姓名', '年龄']
# ['张三', '25']
# ['李四', '30']

# 用 pandas 直接解析表格（更简单）
import pandas as pd
tables = pd.read_html(str(table))
df = tables[0]
print(df)

# ===== 7. 实际应用：爬取博客文章列表 =====
url = "https://example-blog.com/articles"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "lxml")

articles = []
for article in soup.select("div.article-item"):
    title = article.select_one("h2.title").get_text(strip=True)
    link = article.select_one("a")["href"]
    date = article.select_one("span.date").get_text(strip=True)
    summary = article.select_one("p.summary").get_text(strip=True)
    articles.append({
        "title": title,
        "link": link,
        "date": date,
        "summary": summary
    })

print(f"共找到 {len(articles)} 篇文章")
for a in articles[:5]:
    print(f"- {a['date']} | {a['title']}")

# 保存为 CSV
import csv
with open("articles.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "link", "date", "summary"])
    writer.writeheader()
    writer.writerows(articles)
```

### 常用查找方法对比

| 方法 | 用途 | 返回 |
|---|---|---|
| `find(name, attrs)` | 找第一个匹配 | 单个标签 / None |
| `find_all(name, attrs)` | 找所有匹配 | 标签列表 |
| `select(css_selector)` | CSS 选择器找所有 | 标签列表 |
| `select_one(css_selector)` | CSS 选择器找第一个 | 单个标签 / None |
| `find_parent(name)` | 向上找祖先 | 单个标签 / None |
| `find_next_sibling(name)` | 找后续兄弟 | 单个标签 / None |

### CSS 选择器速查

| 选择器 | 含义 | 示例 |
|---|---|---|
| `tag` | 标签名 | `div` |
| `.class` | class | `.title` |
| `#id` | id | `#header` |
| `tag.class` | 标签+class | `h1.title` |
| `ancestor descendant` | 后代 | `div p` |
| `parent > child` | 直接子元素 | `ul > li` |
| `[attr]` | 有属性 | `a[href]` |
| `[attr=value]` | 属性等于 | `a[href="xxx"]` |
| `:nth-child(n)` | 第n个子元素 | `tr:nth-child(2)` |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用 `tag["class"]` 以为是字符串 | 返回列表 | class 是多值属性，返回列表，用 `" ".join(tag["class"])` 转字符串 |
| 不指定解析器 | 警告或解析结果不同 | 明确指定 "lxml"（快）或 "html.parser"（内置） |
| `find` 找不到时直接 `.text` | AttributeError | 先判断是否为 None，或用 select_one + 条件判断 |
| 用 `.string` 获取多标签文本 | 返回 None | 有多个子标签时用 `.text` 或 `.get_text()` |
| 忘记设置 User-Agent | 被网站反爬拒绝 | requests 加 headers={"User-Agent": "Mozilla/5.0..."} |
| 直接解析 response.content（bytes） | 编码问题 | 用 response.text（自动识别编码），或指定 encoding |
| 用 find_all 找一个元素 | 多此一举，还要取 [0] | 找一个用 find 或 select_one |

### 动手

1. 用 requests + BeautifulSoup 解析一个网页，提取所有链接的文本和 URL
2. 解析一个 HTML 表格，转换为 pandas DataFrame
3. 写一个函数，输入网页 URL，返回页面中所有图片的 URL 列表
""")

# ========== 2. scipy 科学计算 ==========
leaf_scipy = make_leaf("py-lib-scipy", "scipy 科学计算", "???", """### 课前

- **场景**：numpy 只能做基础数组运算，需要积分、微分、优化、插值、统计检验、信号处理等高级科学计算。
- **目标**：掌握 scipy 的核心子模块（stats/optimize/interpolate/integrate/linalg），能解决常见科学计算问题。
- **先修**：numpy 基础、高等数学基础

### 是什么

- **一句话定义**：scipy 是基于 numpy 的高级科学计算库，提供积分、微分、优化、插值、统计检验、信号处理、线性代数等专业算法，是科研和数据分析的数学工具箱。
- 与 numpy 的关系：numpy 提供数组和基础运算，scipy 在 numpy 基础上提供更高级的数学算法。

### 怎么写

```python
import numpy as np
from scipy import stats, optimize, interpolate, integrate, linalg
import matplotlib.pyplot as plt

# ===== 1. 统计分析（scipy.stats）=====

# 描述性统计
data = np.array([12, 15, 18, 20, 22, 25, 28, 30, 32, 35])
desc = stats.describe(data)
print(f"样本数: {desc.nobs}")
print(f"均值: {desc.mean:.2f}")
print(f"方差: {desc.variance:.2f}")
print(f"偏度: {desc.skewness:.4f}")
print(f"峰度: {desc.kurtosis:.4f}")

# 常用分布
# 正态分布
norm_dist = stats.norm(loc=0, scale=1)  # 均值0，标准差1
print(norm_dist.pdf(0))    # 概率密度函数：0.3989
print(norm_dist.cdf(1.96)) # 累积分布函数：0.975
print(norm_dist.ppf(0.975)) # 分位点：1.96
print(norm_dist.rvs(10))    # 生成10个随机数

# t 分布、卡方分布、F 分布、二项分布、泊松分布...
t_dist = stats.t(df=10)
chi2_dist = stats.chi2(df=5)
binom_dist = stats.binom(n=10, p=0.5)
poisson_dist = stats.poisson(mu=3)

# 假设检验
# 单样本 t 检验：检验样本均值是否等于某个值
t_stat, p_value = stats.ttest_1samp(data, popmean=20)
print(f"t统计量: {t_stat:.4f}, p值: {p_value:.4f}")
# p > 0.05 则不能拒绝原假设（均值=20）

# 两独立样本 t 检验
group1 = np.array([12, 15, 18, 20, 22])
group2 = np.array([20, 25, 28, 30, 32])
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"两样本t检验: t={t_stat:.4f}, p={p_value:.4f}")

# 配对样本 t 检验（前后对比）
before = np.array([85, 88, 90, 92, 86])
after = np.array([88, 90, 92, 95, 89])
t_stat, p_value = stats.ttest_rel(before, after)

# 卡方检验（独立性检验）
observed = np.array([[20, 30], [30, 20]])
chi2, p, dof, expected = stats.chi2_contingency(observed)
print(f"卡方检验: chi2={chi2:.4f}, p={p:.4f}, dof={dof}")

# 皮尔逊相关系数
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])
r, p = stats.pearsonr(x, y)
print(f"皮尔逊相关: r={r:.4f}, p={p:.4f}")

# 斯皮尔曼等级相关
rho, p = stats.spearmanr(x, y)

# ===== 2. 优化（scipy.optimize）=====

# 求函数最小值
def f(x):
    return x**2 + 3*x + 2

result = optimize.minimize(f, x0=0)  # x0=初始猜测
print(f"最小值点: {result.x[0]:.4f}, 最小值: {result.fun:.4f}")
# 最小值点: -1.5, 最小值: -0.25

# 多元函数优化
def rosenbrock(x):
    return (1 - x[0])**2 + 100*(x[1] - x[0]**2)**2

result = optimize.minimize(rosenbrock, x0=[0, 0], method="BFGS")
print(f"Rosenbrock最小值点: {result.x}")  # 接近 [1, 1]

# 求方程根
def equation(x):
    return x**3 - 2*x - 5

root = optimize.root(equation, x0=2)
print(f"方程的根: {root.x[0]:.4f}")  # 约 2.0946

# 曲线拟合
x_data = np.array([0, 1, 2, 3, 4, 5])
y_data = np.array([1, 3, 7, 13, 21, 31])  # y = x^2 + x + 1

def model(x, a, b, c):
    return a*x**2 + b*x + c

popt, pcov = optimize.curve_fit(model, x_data, y_data)
print(f"拟合参数: a={popt[0]:.4f}, b={popt[1]:.4f}, c={popt[2]:.4f}")
# 输出接近 a=1, b=1, c=1

# ===== 3. 插值（scipy.interpolate）=====

# 已知离散点
x_known = np.array([0, 1, 2, 3, 4, 5])
y_known = np.array([0, 1, 4, 9, 16, 25])  # y = x^2

# 线性插值
f_linear = interpolate.interp1d(x_known, y_known, kind="linear")
print(f"线性插值 x=2.5: {f_linear(2.5):.2f}")  # 12.5

# 三次样条插值（更平滑）
f_cubic = interpolate.interp1d(x_known, y_known, kind="cubic")
print(f"三次插值 x=2.5: {f_cubic(2.5):.4f}")  # 6.25（接近真实值）

# 插值更多点
x_interp = np.linspace(0, 5, 50)
y_interp = f_cubic(x_interp)

# 二维插值（网格数据）
x = np.linspace(0, 4, 5)
y = np.linspace(0, 4, 5)
z = np.outer(np.sin(x), np.cos(y))
f_2d = interpolate.interp2d(x, y, z, kind="cubic")
z_interp = f_2d(2.5, 2.5)

# ===== 4. 积分（scipy.integrate）=====

# 定积分：∫₀¹ x² dx = 1/3
result, error = integrate.quad(lambda x: x**2, 0, 1)
print(f"积分结果: {result:.6f}, 误差估计: {error:.2e}")
# 积分结果: 0.333333

# 二重积分：∫₀¹∫₀¹ (x+y) dx dy
result, error = integrate.dblquad(lambda y, x: x + y, 0, 1, lambda x: 0, lambda x: 1)
print(f"二重积分: {result:.4f}")  # 1.0

# 数值积分（离散数据）
x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 1, 4, 9, 16])
result = integrate.trapz(y, x)  # 梯形法
print(f"梯形积分: {result:.2f}")
result = integrate.simpson(y, x)  # 辛普森法（更精确）
print(f"辛普森积分: {result:.2f}")

# 解微分方程（初值问题）
# dy/dt = -2*y, y(0) = 1
def ode(y, t):
    return -2 * y

t = np.linspace(0, 5, 100)
y = integrate.odeint(ode, y0=1, t=t)
# 解析解: y = e^(-2t)

# ===== 5. 线性代数（scipy.linalg）=====

# 解线性方程组 Ax = b
A = np.array([[2, 1], [1, 3]])
b = np.array([5, 10])
x = linalg.solve(A, b)
print(f"方程组的解: {x}")  # [1, 3]

# 矩阵分解
# LU 分解
P, L, U = linalg.lu(A)
# QR 分解
Q, R = linalg.qr(A)
# 特征值和特征向量
eigenvalues, eigenvectors = linalg.eig(A)
print(f"特征值: {eigenvalues}")
# SVD 奇异值分解
U, s, Vh = linalg.svd(A)

# 矩阵求逆、行列式
A_inv = linalg.inv(A)
det_A = linalg.det(A)
print(f"行列式: {det_A:.2f}")  # 5

# 范数
norm = linalg.norm(A)  # Frobenius 范数
```

### scipy 核心子模块

| 子模块 | 功能 | 常用函数 |
|---|---|---|
| `scipy.stats` | 统计分布与检验 | norm, ttest_ind, pearsonr, chi2_contingency |
| `scipy.optimize` | 优化与拟合 | minimize, root, curve_fit, least_squares |
| `scipy.interpolate` | 插值 | interp1d, interp2d, splrep |
| `scipy.integrate` | 积分与微分方程 | quad, dblquad, trapz, simpson, odeint |
| `scipy.linalg` | 线性代数 | solve, eig, lu, qr, svd, inv, det |
| `scipy.signal` | 信号处理 | find_peaks, butter, filtfilt, spectrogram |
| `scipy.spatial` | 空间算法 | distance, cKDTree, ConvexHull, Delaunay |
| `scipy.ndimage` | 图像处理 | gaussian_filter, median_filter, label |
| `scipy.fft` | 傅里叶变换 | fft, ifft, fft2 |
| `scipy.special` | 特殊函数 | gamma, beta, erf, bessel |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用 scipy 做 numpy 能做的事 | 多此一举 | 基础数组运算用 numpy，高级算法用 scipy |
| optimize.minimize 不设 x0 | 报错 | 必须提供初始猜测 x0，不同 x0 可能收敛到不同局部最优 |
| curve_fit 模型参数顺序错 | 拟合结果不对 | 模型函数第一个参数是 x，后面是待拟合参数 |
| 假设检验不看前提条件 | 结果不可靠 | t 检验要求正态分布，非正态用 Mann-Whitney U 检验 |
| 插值超出已知范围 | 不准确或报错 | interp1d 默认不允许外推，需要时设 fill_value="extrapolate" |
| 用 integrate.trapz 处理非均匀间距 | 结果错误 | trapz(y, x) 必须传 x，不能只传 y（默认等间距） |

### 动手

1. 用 scipy.stats 对一组数据做正态性检验和单样本 t 检验
2. 用 scipy.optimize.curve_fit 拟合一组实验数据到指数衰减模型 y = a*e^(-bx) + c
3. 用 scipy.integrate.quad 计算一个定积分，并用解析解验证
""")

# ========== 3. plotly 交互式可视化 ==========
leaf_plotly = make_leaf("py-lib-plotly", "plotly 交互式可视化", "??", """### 课前

- **场景**：matplotlib 生成的是静态图片，需要可交互的图表（悬停显示数据、缩放、筛选、导出），适合做网页和仪表板。
- **目标**：掌握 plotly 的基础图表、子图布局、交互设置、与 pandas 结合、导出 HTML。
- **先修**：pandas 基础、matplotlib 基础

### 是什么

- **一句话定义**：plotly 是 Python 最流行的交互式可视化库，生成基于 D3.js 的网页图表，支持悬停提示、缩放、平移、筛选、导出等交互功能，是做数据仪表板和网页报告的首选。
- 两大接口：`plotly.graph_objects`（go，底层灵活）、`plotly.express`（px，高层简洁，推荐）。

### 怎么写

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ===== 1. plotly.express 快速绘图（推荐）=====

# 折线图
df = pd.DataFrame({
    "月份": ["1月", "2月", "3月", "4月", "5月", "6月"],
    "销售额": [120, 150, 135, 180, 165, 200],
    "利润": [30, 45, 35, 55, 50, 65]
})
fig = px.line(df, x="月份", y=["销售额", "利润"], 
              title="上半年销售趋势", markers=True)
fig.show()  # 在浏览器中打开交互图

# 柱状图
df_category = pd.DataFrame({
    "品类": ["电子产品", "服装", "食品", "家居", "图书"],
    "2023年": [450, 320, 280, 200, 150],
    "2024年": [520, 350, 310, 230, 170]
})
# 长格式（plotly 推荐）
df_long = df_category.melt(id_vars="品类", var_name="年份", value_name="销售额")
fig = px.bar(df_long, x="品类", y="销售额", color="年份", 
              barmode="group", title="各品类销售额对比")
fig.show()

# 散点图（气泡图）
df_iris = px.data.iris()  # 内置鸢尾花数据集
fig = px.scatter(df_iris, x="sepal_width", y="sepal_length", 
                 color="species", size="petal_length",
                 hover_data=["petal_width"],
                 title="鸢尾花数据散点图")
fig.show()

# 饼图
fig = px.pie(df_category, values="2024年", names="品类", 
             title="2024年销售品类占比")
fig.show()

# 直方图
np.random.seed(42)
data = np.random.randn(1000)
fig = px.histogram(data, nbins=30, title="数据分布直方图")
fig.show()

# 箱线图
fig = px.box(df_iris, x="species", y="sepal_length", 
             title="各品种花萼长度分布")
fig.show()

# 热力图
df_corr = df_iris.drop(columns=["species_id"]).corr()
fig = px.imshow(df_corr, text_auto=True, aspect="auto", 
                title="特征相关性热力图")
fig.show()

# ===== 2. 自定义图表样式 =====
fig = px.line(df, x="月份", y="销售额", title="销售额趋势")

# 更新布局
fig.update_layout(
    title={
        "text": "上半年销售额趋势",
        "font": {"size": 20, "family": "SimHei"},
        "x": 0.5  # 标题居中
    },
    xaxis_title="月份",
    yaxis_title="销售额（万元）",
    template="plotly_white",  # 主题：plotly, plotly_white, plotly_dark, ggplot2, seaborn
    width=800,
    height=500,
    showlegend=True,
    legend={"x": 0.8, "y": 0.9}
)

# 更新轨迹（线条样式）
fig.update_traces(
    line={"color": "#1f77b4", "width": 3},
    marker={"size": 10, "color": "red"},
    hovertemplate="月份: %{x}<br>销售额: %{y}万元<extra></extra>"
)

fig.show()

# ===== 3. 子图布局 =====
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("销售趋势", "品类占比", "品类对比", "利润趋势"),
    specs=[[{"type": "xy"}, {"type": "domain"}],
           [{"type": "xy"}, {"type": "xy"}]]
)

# 添加图表到子图
fig.add_trace(go.Scatter(x=df["月份"], y=df["销售额"], mode="lines+markers", name="销售额"), row=1, col=1)
fig.add_trace(go.Pie(labels=df_category["品类"], values=df_category["2024年"], name="占比"), row=1, col=2)
fig.add_trace(go.Bar(x=df_category["品类"], y=df_category["2023年"], name="2023年"), row=2, col=1)
fig.add_trace(go.Bar(x=df_category["品类"], y=df_category["2024年"], name="2024年"), row=2, col=1)
fig.add_trace(go.Scatter(x=df["月份"], y=df["利润"], mode="lines+markers", name="利润"), row=2, col=2)

fig.update_layout(height=800, width=1000, title_text="销售数据综合仪表板", showlegend=True)
fig.show()

# ===== 4. 交互功能 =====
# 下拉菜单切换数据
fig = px.line(df, x="月份", y=["销售额", "利润"])
fig.update_layout(
    updatemenus=[{
        "buttons": [
            {"method": "restyle", "args": [{"visible": [True, False]}], "label": "只看销售额"},
            {"method": "restyle", "args": [{"visible": [False, True]}], "label": "只看利润"},
            {"method": "restyle", "args": [{"visible": [True, True]}], "label": "全部显示"}
        ],
        "direction": "down",
        "showactive": True,
        "x": 0.1, "y": 1.15
    }]
)
fig.show()

# 范围滑块（时间序列）
fig = px.line(df, x="月份", y="销售额")
fig.update_xaxes(rangeslider_visible=True)
fig.show()

# ===== 5. 导出与保存 =====
# 导出为 HTML（可交互，推荐）
fig.write_html("sales_dashboard.html", include_plotlyjs="cdn")
# include_plotlyjs="cdn"：用 CDN 加载 plotly.js，文件更小
# include_plotlyjs=True：内嵌 plotly.js，文件大但可离线使用

# 导出为静态图片（需要安装 kaleido）
# pip install -U kaleido
fig.write_image("sales_chart.png", scale=2)  # scale=2 高清
fig.write_image("sales_chart.pdf")
fig.write_image("sales_chart.svg")

# ===== 6. 实际应用：动态仪表板 =====
# 模拟销售数据
np.random.seed(42)
dates = pd.date_range("2024-01-01", periods=180, freq="D")
regions = ["华东", "华南", "华北", "西南"]
products = ["手机", "电脑", "耳机", "平板"]

records = []
for date in dates:
    for region in regions:
        for product in products:
            amount = np.random.randint(1000, 10000)
            records.append({"日期": date, "区域": region, "产品": product, "销售额": amount})

df_sales = pd.DataFrame(records)

# 按区域和产品汇总
df_summary = df_sales.groupby(["区域", "产品"])["销售额"].sum().reset_index()

# 交互式柱状图（悬停显示详细数据）
fig = px.bar(df_summary, x="区域", y="销售额", color="产品", 
             barmode="stack", title="各区域各产品销售额",
             hover_data={"销售额": ":,.0f"})
fig.update_layout(template="plotly_white")
fig.write_html("sales_dashboard.html")
print("仪表板已保存为 sales_dashboard.html")
```

### plotly.express 常用图表

| 图表类型 | 函数 | 适用场景 |
|---|---|---|
| 折线图 | `px.line()` | 时间趋势、变化 |
| 柱状图 | `px.bar()` | 类别对比、排名 |
| 散点图 | `px.scatter()` | 相关性、分布 |
| 气泡图 | `px.scatter(size=...)` | 三维关系 |
| 饼图 | `px.pie()` | 占比构成 |
| 直方图 | `px.histogram()` | 数据分布 |
| 箱线图 | `px.box()` | 分布与异常值 |
| 热力图 | `px.imshow()` | 矩阵、相关性 |
| 3D散点 | `px.scatter_3d()` | 三维数据 |
| 地图 | `px.choropleth()` | 地理数据 |
| 漏斗图 | `px.funnel()` | 转化漏斗 |
| 桑基图 | `px.sankey()` | 流向分析 |
| 动画 | `px.scatter(animation_frame=...)` | 动态变化 |

### plotly vs matplotlib 对比

| 维度 | matplotlib | plotly |
|---|---|---|
| 输出 | 静态图片（PNG/SVG/PDF） | 交互式网页（HTML） |
| 交互 | 无（保存后不能交互） | 悬停、缩放、平移、筛选、导出 |
| 语法 | 偏底层，代码多 | express 高层，代码少 |
| 中文支持 | 需要配置字体 | 自动支持（浏览器渲染） |
| 适用场景 | 论文、报告、印刷 | 仪表板、网页、交互探索 |
| 文件大小 | 图片小 | HTML 较大（含 JS） |
| 3D/地图 | 较弱 | 强大（内置） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用宽格式数据传 px | 图表不符合预期 | plotly 推荐长格式（melt），一列维度一列值 |
| 不指定 template | 默认样式不够美观 | 用 template="plotly_white" 或其他主题 |
| 导出图片报错 | 缺少 kaleido | 先 pip install -U kaleido |
| HTML 文件太大 | 内嵌了 plotly.js | 用 include_plotlyjs="cdn" 减小文件 |
| 中文显示为方框 | 字体问题 | plotly 用浏览器渲染，一般自动支持；服务器环境需安装中文字体 |
| 子图类型不匹配 | 报错 | make_subplots 的 specs 要指定 type（pie 用 "domain"） |
| 以为 plotly 只能做网页 | 不知道能导出静态图 | 用 write_image 可导出 PNG/PDF/SVG |

### 动手

1. 用 plotly.express 画一个交互式折线图，包含销售额和利润两条线，悬停显示详细数据
2. 画一个包含 4 个子图的仪表板（折线图+柱状图+饼图+散点图），导出为 HTML
3. 用 px.data.gapminder() 数据集做一个动画散点图（animation_frame="year"），展示各国人均 GDP 随时间变化
""")

# ========== 4. openpyxl Excel 处理 ==========
leaf_openpyxl = make_leaf("py-lib-openpyxl", "openpyxl Excel处理", "??", """### 课前

- **场景**：需要用 Python 自动生成 Excel 报表、设置格式、公式、图表，或者读取复杂的 Excel 文件。
- **目标**：掌握 openpyxl 的工作簿/工作表/单元格操作、格式设置、公式、图表、数据验证。
- **先修**：Python 基础、pandas 基础

### 是什么

- **一句话定义**：openpyxl 是 Python 最流行的 Excel（.xlsx）读写库，支持创建和修改工作簿、设置单元格格式、写入公式、插入图表、数据验证等，是自动化 Excel 报表的首选工具。
- 注意：只支持 .xlsx 格式，不支持旧版 .xls（用 xlrd/xlwt）。

### 怎么写

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side, numbers
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation
import pandas as pd

# ===== 1. 创建工作簿和工作表 =====
wb = Workbook()  # 新建工作簿，默认有一个 Sheet
ws = wb.active   # 获取活动工作表
ws.title = "销售数据"  # 重命名工作表

# 新建工作表
ws2 = wb.create_sheet("汇总报表")
ws3 = wb.create_sheet("数据验证", 0)  # 插入到第一个位置

# 查看所有工作表
print(wb.sheetnames)  # ['数据验证', '销售数据', '汇总报表']

# ===== 2. 写入数据 =====
# 直接赋值
ws["A1"] = "订单号"
ws["B1"] = "产品"
ws["C1"] = "数量"
ws["D1"] = "单价"
ws["E1"] = "金额"

# 用 cell 方法
ws.cell(row=2, column=1, value="ORD001")
ws.cell(row=2, column=2, value="手机")
ws.cell(row=2, column=3, value=2)
ws.cell(row=2, column=4, value=3000)

# 追加行（从最后一行之后开始）
ws.append(["ORD002", "电脑", 1, 5000])
ws.append(["ORD003", "耳机", 5, 200])
ws.append(["ORD004", "平板", 3, 2500])

# 批量写入（二维列表）
data = [
    ["ORD005", "手机", 1, 3000],
    ["ORD006", "电脑", 2, 5000],
    ["ORD007", "耳机", 10, 200]
]
for row in data:
    ws.append(row)

# ===== 3. 读取数据 =====
# 读取已有工作簿
wb = load_workbook("sales.xlsx", data_only=True)
# data_only=True：读取公式计算后的值（而不是公式本身）
ws = wb["销售数据"]

# 读取单元格
print(ws["A1"].value)
print(ws.cell(row=1, column=1).value)

# 遍历行
for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
    print(row)  # ('订单号', '产品', '数量', '单价', '金额')

# 遍历列
for col in ws.iter_cols(min_col=1, max_col=3, values_only=True):
    print(col)

# 获取所有数据
all_data = list(ws.values)
print(f"共 {len(all_data)} 行")

# 最大行/列
print(f"最大行: {ws.max_row}, 最大列: {ws.max_column}")

# ===== 4. 公式 =====
ws["E2"] = "=C2*D2"  # 金额 = 数量 * 单价
ws["E3"] = "=C3*D3"
# 批量设置公式
for row in range(2, ws.max_row + 1):
    ws[f"E{row}"] = f"=C{row}*D{row}"

# 汇总公式
ws["A10"] = "合计"
ws["E10"] = "=SUM(E2:E9)"
ws["C10"] = "=SUM(C2:C9)"
ws["D10"] = '=AVERAGE(D2:D9)'  # 平均单价

# ===== 5. 格式设置 =====
# 字体
header_font = Font(name="微软雅黑", size=12, bold=True, color="FFFFFF")
data_font = Font(name="微软雅黑", size=11)

# 填充（背景色）
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
highlight_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

# 对齐
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="center")

# 边框
thin_border = Border(
    left=Side(style="thin", color="000000"),
    right=Side(style="thin", color="000000"),
    top=Side(style="thin", color="000000"),
    bottom=Side(style="thin", color="000000")
)

# 应用格式到表头
for col in range(1, 6):
    cell = ws.cell(row=1, column=col)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

# 应用格式到数据行
for row in range(2, ws.max_row + 1):
    for col in range(1, 6):
        cell = ws.cell(row=row, column=col)
        cell.font = data_font
        cell.border = thin_border
        if col in [3, 4, 5]:  # 数字列居中
            cell.alignment = center_align
        else:
            cell.alignment = left_align

# 数字格式
for row in range(2, ws.max_row + 1):
    ws[f"D{row}"].number_format = '#,##0.00'  # 单价保留2位小数
    ws[f"E{row}"].number_format = '¥#,##0.00'   # 金额带货币符号

# 列宽和行高
ws.column_dimensions["A"].width = 12
ws.column_dimensions["B"].width = 10
ws.column_dimensions["C"].width = 8
ws.column_dimensions["D"].width = 12
ws.column_dimensions["E"].width = 14
ws.row_dimensions[1].height = 25

# 合并单元格
ws.merge_cells("A10:B10")
ws["A10"].alignment = center_align
ws["A10"].font = Font(bold=True)

# 冻结窗格（冻结首行）
ws.freeze_panes = "A2"

# ===== 6. 条件格式 =====
# 金额列色阶（从低到高渐变）
color_scale = ColorScaleRule(
    start_type="min", start_color="FFEB9C",
    mid_type="percentile", mid_value=50, mid_color="FFC000",
    end_type="max", end_color="FF0000"
)
ws.conditional_formatting.add("E2:E9", color_scale)

# 数量大于5的单元格高亮
highlight_rule = CellIsRule(
    operator="greaterThan",
    formula=["5"],
    fill=PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
    font=Font(color="9C0006")
)
ws.conditional_formatting.add("C2:C9", highlight_rule)

# ===== 7. 插入图表 =====
# 柱状图
chart = BarChart()
chart.type = "col"
chart.style = 10
chart.title = "各订单金额"
chart.y_axis.title = "金额（元）"
chart.x_axis.title = "订单号"

data_ref = Reference(ws, min_col=5, min_row=1, max_row=9)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=9)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
chart.width = 15
chart.height = 10
ws.add_chart(chart, "G2")

# 饼图（在汇总表）
ws2["A1"] = "产品"
ws2["B1"] = "销售数量"
products = ["手机", "电脑", "耳机", "平板"]
quantities = [3, 3, 15, 3]
for i, (p, q) in enumerate(zip(products, quantities), 2):
    ws2[f"A{i}"] = p
    ws2[f"B{i}"] = q

pie = PieChart()
pie.title = "产品销售占比"
data_ref = Reference(ws2, min_col=2, min_row=1, max_row=5)
cats_ref = Reference(ws2, min_col=1, min_row=2, max_row=5)
pie.add_data(data_ref, titles_from_data=True)
pie.set_categories(cats_ref)
ws2.add_chart(pie, "D2")

# ===== 8. 数据验证（下拉菜单）=====
dv = DataValidation(type="list", formula1='"手机,电脑,耳机,平板"', allow_blank=True)
dv.error = "请从列表中选择产品"
dv.errorTitle = "输入错误"
dv.prompt = "请选择产品类型"
dv.promptTitle = "产品选择"
ws3.add_data_validation(dv)
dv.add("B2:B100")  # 应用到 B2:B100

# 数字范围验证
dv_num = DataValidation(type="whole", operator="between", formula1=1, formula2=100)
dv_num.error = "数量必须在1-100之间"
ws3.add_data_validation(dv_num)
dv_num.add("C2:C100")

# ===== 9. 与 pandas 结合 =====
# pandas DataFrame 写入 Excel（带格式）
df = pd.DataFrame({
    "订单号": ["ORD001", "ORD002", "ORD003"],
    "产品": ["手机", "电脑", "耳机"],
    "数量": [2, 1, 5],
    "单价": [3000, 5000, 200]
})

# 简单写入
df.to_excel("output.xlsx", index=False, sheet_name="数据")

# 用 openpyxl 引擎追加到已有工作簿
with pd.ExcelWriter("output.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    df.to_excel(writer, sheet_name="新数据", index=False)

# ===== 10. 保存工作簿 =====
wb.save("销售报表.xlsx")
print("Excel 文件已保存")

# 关闭
wb.close()
```

### 常用操作速查

| 操作 | 代码 |
|---|---|
| 新建工作簿 | `wb = Workbook()` |
| 打开工作簿 | `wb = load_workbook("file.xlsx", data_only=True)` |
| 获取工作表 | `ws = wb["Sheet名"]` 或 `wb.active` |
| 新建工作表 | `ws = wb.create_sheet("名称")` |
| 写入单元格 | `ws["A1"] = value` 或 `ws.cell(row=1, column=1, value=...)` |
| 追加行 | `ws.append([...])` |
| 读取单元格 | `ws["A1"].value` |
| 遍历行 | `for row in ws.iter_rows(values_only=True):` |
| 设置公式 | `ws["E2"] = "=C2*D2"` |
| 设置字体 | `cell.font = Font(name=..., size=..., bold=...)` |
| 设置填充 | `cell.fill = PatternFill(start_color=..., fill_type="solid")` |
| 设置对齐 | `cell.alignment = Alignment(horizontal="center", vertical="center")` |
| 设置边框 | `cell.border = Border(left=Side(style="thin"), ...)` |
| 列宽 | `ws.column_dimensions["A"].width = 15` |
| 行高 | `ws.row_dimensions[1].height = 25` |
| 合并单元格 | `ws.merge_cells("A1:B1")` |
| 冻结窗格 | `ws.freeze_panes = "A2"` |
| 插入图表 | `ws.add_chart(chart, "G2")` |
| 保存 | `wb.save("file.xlsx")` |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用 openpyxl 读 .xls 文件 | 报错 | openpyxl 只支持 .xlsx，.xls 用 xlrd/pandas |
| load_workbook 不设 data_only | 读到公式字符串而不是值 | 读计算结果设 data_only=True（但文件必须用 Excel 打开保存过） |
| 修改后不 save | 改动丢失 | 所有修改后必须 wb.save() |
| 行号列号从0开始 | 数据写错位置 | openpyxl 行号列号从1开始（不是0） |
| 公式中用中文列名 | 公式错误 | 公式用单元格引用（A1/B2），不是列标题 |
| 图表数据范围包含标题但不设 titles_from_data | 标题被当成数据 | add_data 时设 titles_from_data=True |
| 大量数据逐行写入 | 性能差 | 用 append 批量写入，或用 pandas to_excel |
| 忘记关闭工作簿 | 文件被占用 | wb.close()，或用 with 语句 |

### 动手

1. 用 openpyxl 创建一个销售报表，包含表头格式、数据、金额公式、合计行、柱状图
2. 给报表添加条件格式（金额列色阶、数量大于5高亮）和数据验证（产品下拉菜单）
3. 用 pandas 读取一个 CSV，用 openpyxl 设置格式后导出为美观的 Excel
""")

# ========== 5. 数据库连接 ==========
leaf_db_conn = make_leaf("py-lib-db", "数据库连接与操作", "??", """### 课前

- **场景**：数据分析需要从 MySQL/PostgreSQL 等数据库读取数据，或者把处理结果写回数据库。
- **目标**：掌握 pymysql/psycopg2 原生连接、SQLAlchemy ORM、pandas 读写数据库、连接池。
- **先修**：SQL 基础、Python 基础

### 是什么

- **一句话定义**：Python 通过数据库驱动库（pymysql 连接 MySQL、psycopg2 连接 PostgreSQL）与数据库交互，执行 SQL 查询和写入；SQLAlchemy 提供更高级的 ORM 和连接池，是 Python 数据库操作的标准方案。

### 怎么写

```python
# ===== 1. MySQL 连接（pymysql）=====
# 安装：pip install pymysql

import pymysql
from pymysql.cursors import DictCursor

# 建立连接
conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="your_password",
    database="sales_db",
    charset="utf8mb4",
    cursorclass=DictCursor  # 查询结果返回字典（默认是元组）
)

# 创建游标
cursor = conn.cursor()

# 查询
cursor.execute("SELECT * FROM orders WHERE amount > %s", (1000,))
# 注意：pymysql 用 %s 占位符（不是字符串格式化！）
results = cursor.fetchall()  # 获取所有结果（列表[字典]）
for row in results:
    print(row["order_id"], row["amount"])

one_row = cursor.fetchone()  # 获取一条
many_rows = cursor.fetchmany(10)  # 获取10条

# 插入/更新/删除（需要 commit）
sql = "INSERT INTO orders (order_id, user_id, amount) VALUES (%s, %s, %s)"
cursor.execute(sql, ("ORD001", 101, 3000))
conn.commit()  # 必须提交！否则不生效

# 批量插入（更高效）
data = [
    ("ORD002", 102, 5000),
    ("ORD003", 103, 200),
    ("ORD004", 104, 2500)
]
cursor.executemany(sql, data)
conn.commit()

# 更新
cursor.execute("UPDATE orders SET amount = %s WHERE order_id = %s", (3500, "ORD001"))
conn.commit()

# 删除
cursor.execute("DELETE FROM orders WHERE order_id = %s", ("ORD001",))
conn.commit()

# 事务回滚
try:
    cursor.execute("INSERT ...")
    conn.commit()
except Exception as e:
    conn.rollback()  # 出错回滚
    print(f"错误: {e}")
finally:
    cursor.close()
    conn.close()  # 必须关闭连接！

# 上下文管理器（自动关闭）
with pymysql.connect(host="localhost", user="root", password="xxx", database="db") as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM table")
        results = cursor.fetchall()
# 退出 with 块自动关闭连接和游标

# ===== 2. PostgreSQL 连接（psycopg2）=====
# 安装：pip install psycopg2-binary

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="your_password",
    dbname="sales_db"
)

# psycopg2 用 %s 占位符（和 pymysql 一样）
cursor = conn.cursor(cursor_factory=RealDictCursor)  # 字典游标
cursor.execute("SELECT * FROM orders WHERE amount > %s", (1000,))
results = cursor.fetchall()

# 其他操作（INSERT/UPDATE/DELETE/commit/rollback）和 pymysql 基本一致
cursor.execute("INSERT INTO orders VALUES (%s, %s, %s)", ("ORD001", 101, 3000))
conn.commit()

cursor.close()
conn.close()

# ===== 3. SQLAlchemy（推荐，更高级）=====
# 安装：pip install sqlalchemy

from sqlalchemy import create_engine, text
import pandas as pd

# 创建引擎（连接池）
# MySQL:
engine = create_engine("mysql+pymysql://root:password@localhost:3306/sales_db?charset=utf8mb4")
# PostgreSQL:
# engine = create_engine("postgresql+psycopg2://postgres:password@localhost:5432/sales_db")
# SQLite:
# engine = create_engine("sqlite:///data.db")

# URL 格式：dialect+driver://username:password@host:port/database

# 执行原生 SQL
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM orders WHERE amount > :amount"), {"amount": 1000})
    # SQLAlchemy 用 :name 命名参数（不是 %s）
    for row in result:
        print(row)

# ===== 4. pandas 读写数据库（最常用）=====
import pandas as pd

# 读取数据库到 DataFrame
df = pd.read_sql("SELECT * FROM orders", engine)
print(df.head())

# 带参数查询
df = pd.read_sql(
    "SELECT * FROM orders WHERE amount > %s AND order_date >= %s",
    engine,
    params=(1000, "2024-01-01")
)

# 用 SQLAlchemy text（命名参数）
df = pd.read_sql(
    text("SELECT * FROM orders WHERE amount > :amount"),
    engine,
    params={"amount": 1000}
)

# 分块读取（大表）
chunk_iter = pd.read_sql("SELECT * FROM big_table", engine, chunksize=10000)
for chunk in chunk_iter:
    process(chunk)  # 每次处理1万行

# 写入数据库
df.to_sql(
    name="orders_new",      # 表名
    con=engine,             # 连接
    if_exists="replace",    # 表已存在时：fail/replace/append
    index=False,            # 不写入 DataFrame 索引
    chunksize=1000,         # 批量写入大小
    method="multi"          # 多行插入（更快）
)

# 追加数据
df.to_sql("orders", engine, if_exists="append", index=False)

# ===== 5. 连接池配置 =====
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:password@localhost/db",
    pool_size=10,          # 连接池大小
    max_overflow=20,        # 超出 pool_size 后最多创建的连接数
    pool_timeout=30,        # 获取连接超时时间（秒）
    pool_recycle=3600,      # 连接回收时间（秒），MySQL 默认 8 小时断开
    pool_pre_ping=True      # 每次获取连接前先 ping，确保连接有效
)

# ===== 6. 实际应用：数据 ETL =====
# 从 MySQL 读取 → pandas 处理 → 写入 PostgreSQL

# 1. 从源数据库读取
source_engine = create_engine("mysql+pymysql://user:pass@source-host/source_db")
df = pd.read_sql('''
    SELECT order_id, user_id, amount, order_date
    FROM orders
    WHERE order_date >= '2024-01-01'
''', source_engine)

print(f"读取 {len(df)} 条数据")

# 2. 数据清洗和转换
df["amount"] = df["amount"].fillna(0)
df["order_date"] = pd.to_datetime(df["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)
df_monthly = df.groupby("month")["amount"].agg(["sum", "count"]).reset_index()
df_monthly.columns = ["月份", "总销售额", "订单数"]

# 3. 写入目标数据库
target_engine = create_engine("postgresql+psycopg2://user:pass@target-host/target_db")
df_monthly.to_sql("monthly_sales", target_engine, if_exists="replace", index=False)
print("数据已写入目标数据库")

# ===== 7. 安全：不要硬编码密码 =====
import os

# 从环境变量读取
db_password = os.environ.get("DB_PASSWORD", "default_password")
engine = create_engine(f"mysql+pymysql://root:{db_password}@localhost/db")

# 或从配置文件读取（.env）
# pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
```

### 数据库驱动对比

| 数据库 | 驱动库 | 安装 | 连接 URL |
|---|---|---|---|
| MySQL | pymysql | `pip install pymysql` | `mysql+pymysql://user:pass@host:3306/db` |
| MySQL | mysql-connector | `pip install mysql-connector-python` | `mysql+mysqlconnector://...` |
| PostgreSQL | psycopg2 | `pip install psycopg2-binary` | `postgresql+psycopg2://user:pass@host:5432/db` |
| SQLite | 内置 | 无需安装 | `sqlite:///data.db` |
| SQL Server | pyodbc | `pip install pyodbc` | `mssql+pyodbc://...` |
| Oracle | cx_Oracle | `pip install cx_Oracle` | `oracle+cx_oracle://...` |
| MongoDB | pymongo | `pip install pymongo` | （NoSQL，用 pymongo 直接连接） |
| Redis | redis-py | `pip install redis` | （NoSQL，用 redis 直接连接） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用字符串拼接 SQL | SQL 注入风险 + 转义问题 | 始终用参数化查询（%s 或 :name），不要 f-string 拼 SQL |
| 执行 INSERT 后不 commit | 数据没写入 | 写操作必须 conn.commit()，查询不需要 |
| 用完不关闭连接 | 连接泄漏，数据库连接数满 | 用 with 语句或 finally 中 close() |
| pymysql 用 ? 占位符 | 报错 | pymysql/psycopg2 用 %s，SQLAlchemy 用 :name |
| 大表一次 read_sql | 内存溢出 | 用 chunksize 分块读取 |
| to_sql 不设 index=False | 多了一列索引 | 通常不需要索引列，设 index=False |
| 硬编码数据库密码 | 安全风险 | 用环境变量或 .env 配置文件 |
| 不设 pool_recycle | MySQL 8小时后连接断开报错 | 设 pool_recycle=3600（1小时回收） |
| pandas read_sql 用 SQLAlchemy 1.x 语法 | 警告或报错 | pandas 2.x 配合 SQLAlchemy 2.x，用 text() 包裹 SQL |

### 动手

1. 用 pymysql 连接 MySQL，创建一张表，插入 10 条测试数据，查询并打印
2. 用 pandas 从数据库读取一张表，做简单的聚合分析，然后用 to_sql 写入另一张表
3. 写一个 ETL 脚本：从 MySQL 读取原始数据 → pandas 清洗聚合 → 写入 PostgreSQL
""")

# ========== 组装"常用库"章节并插入 ==========
chapter_libs = {
    "id": "py-libs",
    "title": "常用库",
    "level": "??",
    "content": """### 课前 · 章节导读

- **章节**：常用库
- **为什么学本章**：Python 的强大在于丰富的第三方库生态，数据分析工作中 80% 的任务都靠这些库完成。
- **学习目标**：掌握数据采集（requests+BS4）、科学计算（scipy）、交互式可视化（plotly）、Excel处理（openpyxl）、数据库连接（pymysql/psycopg2/SQLAlchemy）。
- **先修**：Python 基础、pandas 基础

### 本章叶课地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | requests 网络请求 | ?? | HTTP 请求、API 调用、会话、超时重试 |
| 2 | BeautifulSoup 网页解析 | ?? | HTML 解析、标签查找、CSS 选择器、提取数据 |
| 3 | scipy 科学计算 | ??? | 统计检验、优化、插值、积分、线性代数 |
| 4 | plotly 交互式可视化 | ?? | 交互图表、子图、样式、导出 HTML |
| 5 | openpyxl Excel处理 | ?? | 工作簿操作、格式、公式、图表、数据验证 |
| 6 | 数据库连接与操作 | ?? | pymysql/psycopg2、SQLAlchemy、pandas 读写 |

### 推荐顺序

```text
requests → BeautifulSoup → scipy → plotly → openpyxl → 数据库连接
```

### 怎么学本章

1. **每个库先跑通示例**：把代码示例复制到 Jupyter 中运行
2. **理解 API 设计**：每个库都有自己的设计模式，理解后举一反三
3. **结合实际项目**：用这些库完成一个完整的数据分析项目
4. **查官方文档**：遇到问题先查官方文档，比搜索更可靠

### 章末验收

| 检查项 | 通过标准 |
|---|---|
| 主路径 | 每个库的示例代码能跑通 |
| 易错 | 能举本章至少 3 个常见错误 |
| 迁移 | 能独立用这些库完成一个数据采集→分析→可视化的小项目 |

### 下一动

点开第 1 片绿色叶节点。本章合计约 **6** 片叶讲义。
""",
    "lessonParent": True,
    "children": [leaf_requests, leaf_bs4, leaf_scipy, leaf_plotly, leaf_openpyxl, leaf_db_conn]
}

# 读取 embed-python.js
with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

# 检查是否已存在
root_children = data["children"]
if not any(c.get("id") == "py-libs" for c in root_children):
    # 插入到"生态与加速"之前
    insert_idx = len(root_children)
    for i, child in enumerate(root_children):
        if child.get("id") == "py-stack":
            insert_idx = i
            break
    root_children.insert(insert_idx, chapter_libs)
    print(f"✓ 常用库章节已插入（包含6个库教程）")
else:
    print("常用库章节已存在")

# 序列化
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["python"]={new_json_str}\n'

with open(r"D:\cursor\数据学习平台\kg-data\embed-python.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-python.js size: {len(new_content)} bytes")
print("Python 核心库详细教程补充完成")
