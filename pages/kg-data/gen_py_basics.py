#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Python 基础模块的 JSON 节点"""

import json
import os

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

def make_chapter(node_id, title, level, leaves):
    leaf_titles = "、".join([l["title"] for l in leaves])
    leaf_count = len(leaves)
    
    # 生成叶课地图表格
    leaf_table_rows = []
    for i, l in enumerate(leaves, 1):
        # 从content中提取一句话定义
        one_line = "..."
        for line in l["content"].split("\n"):
            if "一句话定义" in line:
                one_line = line.split("：", 1)[-1].strip()[:50]
                break
        leaf_table_rows.append(f"| {i} | {l['title']} | {l['level']} | {one_line} |")
    
    leaf_table = "\n".join(leaf_table_rows)
    
    content = f"""### 课前 · 章节导读

- **章节**：{title}
- **为什么学本章**：本章把「{title}」拆成可练习的叶课，避免只记名词。
- **学习目标**：学完本章叶课，能独立完成主路径代码，并讲清适用边界。
- **先修**：Python 基础语法；相邻前一章叶课。

### 本章故事线

```text
{leaf_titles}
```

### 本章叶课地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
{leaf_table}

### 推荐顺序

```text
{leaf_titles}
```

### 怎么学本章

1. **先扫地图**：知道本章有哪些叶、各自解决什么
2. **按序开叶**：每叶走完「怎么写 → 易错对照 → 动手」
3. **章末串讲**：用 3 分钟向同伴复述本章故事线

### 章末验收

| 检查项 | 通过标准 |
|---|---|
| 主路径 | 每叶示例可跑通或可手推结果 |
| 易错 | 能举本章至少 2 个反例 |
| 口述 | 不看笔记讲清「{title}」解决什么问题 |

### 下一动

点开地图中的第 1 片绿色叶节点。本章合计约 **{leaf_count}** 片叶讲义。
"""
    return {"id": node_id, "title": title, "level": level, "content": content, "lessonParent": True, "children": leaves}

# ========== 叶子节点内容 ==========

leaf_vars = make_leaf("py-basic-variables", "变量与数据类型", "?", """### 课前

- **场景**：刚打开 Python，要存一个用户名和年龄。
- **目标**：掌握变量赋值、基本数据类型、类型转换与动态类型直觉。
- **先修**：无（Python 第一课）

### 是什么

- **一句话定义**：变量是贴在值上的名字标签；Python 是动态类型语言，变量不需要声明类型。
- **基本类型**：int（整数）、float（浮点数）、str（字符串）、bool（布尔）、None（空值）。
- **直觉**：变量像便利贴，贴在哪个值上就指向哪个值；重新赋值只是换张贴的位置。

### 怎么写

```python
# 变量赋值
name = "Ada"
age = 28
height = 1.68
is_student = False
note = None

# 查看类型
print(type(name))    # <class 'str'>
print(type(age))     # <class 'int'>

# 类型转换
age_str = str(age)           # "28"
height_int = int(height)     # 1（截断小数）
score = float("95.5")        # 95.5
flag = bool(0)               # False

# 多变量赋值
a, b, c = 1, 2, 3
x = y = z = 0

# 链式赋值与交换
a, b = b, a  # 交换 a 和 b 的值
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 变量名用数字开头 | SyntaxError | 变量名只能字母/下划线开头 |
| 用关键字当变量名（如 list=1） | 覆盖内置函数 | 避免用 list/str/int 等当变量名 |
| 整数除以整数期望整数 | 3/2=1.5（Python3） | 整除用 // |
| 比较 None 用 == | 能工作但不规范 | 用 is None / is not None |

### 动手

1. 定义变量 city="上海"、population=2487，打印类型
2. 把 population 转成字符串后和 city 拼接
3. 写一句「Python 动态类型和 C/Java 静态类型有什么不同」
""")

leaf_operators = make_leaf("py-basic-operators", "运算符与表达式", "?", """### 课前

- **场景**：要算折扣价、判断用户是否满足活动条件。
- **目标**：掌握算术、比较、逻辑、赋值运算符及运算符优先级。
- **先修**：变量与数据类型

### 是什么

- **一句话定义**：运算符是对值进行计算和比较的符号；表达式是值和运算符的组合。
- **分类**：算术（+ - * / // % **）、比较（== != > < >= <=）、逻辑（and or not）、赋值（= += -= *= /=）、成员（in not in）、身份（is is not）。

### 怎么写

```python
# 算术运算符
a, b = 10, 3
print(a + b)    # 13  加
print(a - b)    # 7   减
print(a * b)    # 30  乘
print(a / b)    # 3.333...  除（结果是float）
print(a // b)   # 3   整除（向下取整）
print(a % b)    # 1   取余
print(a ** b)   # 1000  幂运算

# 比较运算符（结果是bool）
print(a > b)     # True
print(a == b)    # False
print(a != b)    # True

# 逻辑运算符
age = 25
has_vip = True
print(age >= 18 and has_vip)   # True（两个都True才True）
print(age < 18 or has_vip)     # True（一个True就True）
print(not has_vip)              # False

# 赋值运算符
count = 0
count += 1   # count = count + 1
count *= 2   # count = count * 2

# 成员运算符
fruits = ["apple", "banana", "orange"]
print("apple" in fruits)       # True
print("grape" not in fruits)   # True

# 运算符优先级：括号 > 幂 > 乘除 > 加减 > 比较 > 逻辑
result = (2 + 3) * 4 ** 2 / 2  # 先括号，再幂，再乘除
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 比较用 = 而不是 == | 赋值而非比较，可能不报错 | 相等比较用 == |
| 整数除法用 / | 得到 float | 整除用 // |
| 逻辑运算用 && / \\|\\| | SyntaxError | Python 用 and / or |
| 优先级记错导致结果错 | 计算顺序不对 | 不确定就加括号 |

### 动手

1. 计算 100 元打 85 折后的价格（保留2位小数）
2. 判断 age=20, score=85 是否满足「年龄>=18 且 分数>=60」
3. 用 in 判断 "py" 是否在 "python" 中
""")

leaf_strings = make_leaf("py-basic-strings", "字符串操作", "?", """### 课前

- **场景**：要处理用户输入的姓名、拼接提示信息、提取订单号前缀。
- **目标**：掌握字符串定义、索引切片、常用方法、f-string 格式化。
- **先修**：变量与数据类型

### 是什么

- **一句话定义**：字符串是字符的有序序列，Python 中用引号包裹，不可变。
- **核心能力**：索引/切片、拼接、查找替换、分割合并、大小写转换、格式化输出。

### 怎么写

```python
# 字符串定义
s1 = 'hello'
s2 = "world"
s3 = '''多行
字符串'''

# 索引与切片（从0开始，左闭右开）
s = "Python"
print(s[0])      # P（第一个字符）
print(s[-1])     # n（最后一个字符）
print(s[1:4])    # yth（索引1到3）
print(s[:3])     # Pyt（前3个）
print(s[3:])     # hon（从第3个到末尾）
print(s[::-1])   # nohtyP（反转）

# 常用方法
text = "  Hello World  "
print(text.strip())           # "Hello World"（去首尾空格）
print(text.lower())           # "  hello world  "
print(text.upper())           # "  HELLO WORLD  "
print(text.replace("World", "Python"))  # 替换
print(text.find("World"))    # 查找位置（找不到返回-1）
print(text.count("o"))       # 统计出现次数

# 分割与合并
csv_line = "Ada,28,上海"
parts = csv_line.split(",")   # ["Ada", "28", "上海"]
joined = "-".join(parts)       # "Ada-28-上海"

# f-string 格式化（Python 3.6+）
name = "Ada"
age = 28
print(f"姓名：{name}，年龄：{age}")
print(f"明年{age + 1}岁")
price = 99.99
print(f"价格：{price:.2f}元")   # 保留2位小数

# 字符串不可变（不能 s[0] = 'x'）
s = "hello"
# s[0] = 'H'  # TypeError！
s = "H" + s[1:]  # 正确：重新赋值
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 索引越界 s[100] | IndexError | 索引范围 0 到 len(s)-1 |
| 试图修改单个字符 s[0]='x' | TypeError | 字符串不可变，用拼接或 replace |
| split 后忘记是列表 | 直接当字符串用 | split 返回 list |
| f-string 用了单引号嵌套 | 语法冲突 | 内外用不同引号 |

### 动手

1. 把 "  data engineer  " 去空格后转大写
2. 用 f-string 打印 "用户Ada在上海，订单数5"（变量代入）
3. 把 "a-b-c-d" 按 - 分割后再用 | 合并
""")

# --- 控制流 ---
leaf_if = make_leaf("py-basic-if", "条件判断 if", "?", """### 课前

- **场景**：根据用户等级给不同折扣，根据订单状态走不同流程。
- **目标**：掌握 if/elif/else 结构、条件表达式、嵌套判断。
- **先修**：运算符与表达式

### 是什么

- **一句话定义**：条件判断让程序根据布尔表达式的结果选择执行不同代码块。
- **结构**：if（如果）→ elif（否则如果，可多个）→ else（否则，可选）。
- **缩进**：Python 用缩进来表示代码块，通常4个空格。

### 怎么写

```python
# 基本 if-else
score = 85
if score >= 60:
    print("及格")
else:
    print("不及格")

# if-elif-else 多分支
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"
print(grade)  # B

# 条件表达式（三元运算符）
result = "通过" if score >= 60 else "不通过"

# 嵌套判断
is_vip = True
amount = 200
if amount >= 100:
    if is_vip:
        discount = 0.8
    else:
        discount = 0.9
else:
    discount = 1.0
print(f"折扣：{discount}")

# 复杂条件
age = 25
has_id = True
if age >= 18 and has_id:
    print("可以进入")
elif age >= 16 and not has_id:
    print("需要监护人陪同")
else:
    print("禁止进入")

# 空值/空集合判断（Pythonic 写法）
name = ""
if not name:        # 空字符串为 False
    print("名字不能为空")

items = []
if not items:       # 空列表为 False
    print("列表为空")
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| if 后面忘加冒号 | SyntaxError | if/elif/else 后必须加 : |
| 缩进不一致 | IndentationError | 同一代码块缩进必须一致（4空格） |
| 用 = 做条件判断 | 赋值而非比较 | 相等用 == |
| elif 写成 else if | SyntaxError | Python 用 elif |
| 多个独立 if 而非 elif | 每个都判断，可能多个都执行 | 互斥条件用 elif |

### 动手

1. 写一个判断：amount>=200 且 is_vip 则打8折，amount>=100 打9折，否则不打折
2. 用条件表达式写「成年人」/「未成年人」判断
3. 写一句「什么时候用 if-elif-else，什么时候用多个独立 if」
""")

leaf_loops = make_leaf("py-basic-loops", "循环 for/while", "?", """### 课前

- **场景**：遍历订单列表计算总金额，重试连接直到成功。
- **目标**：掌握 for 循环遍历、while 循环、break/continue、range。
- **先修**：条件判断 if

### 是什么

- **一句话定义**：循环让一段代码重复执行；for 用于遍历可迭代对象，while 用于条件满足时重复。
- **控制语句**：break（跳出循环）、continue（跳过本次继续下一次）、else（循环正常结束后执行）。

### 怎么写

```python
# for 循环遍历列表
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)

# for + range（数字序列）
for i in range(5):        # 0,1,2,3,4
    print(i)
for i in range(2, 10, 2): # 2,4,6,8（起始,结束,步长）
    print(i)

# for + enumerate（同时取索引和值）
for idx, fruit in enumerate(fruits):
    print(f"{idx}: {fruit}")

# 遍历字典
user = {"name": "Ada", "age": 28, "city": "上海"}
for key in user:              # 遍历键
    print(key)
for key, value in user.items():  # 遍历键值对
    print(f"{key}: {value}")

# 计算总金额（for 循环累加）
amounts = [80, 120, 50, 200]
total = 0
for amt in amounts:
    total += amt
print(f"总金额：{total}")  # 450

# while 循环
count = 0
while count < 3:
    print(f"第{count}次")
    count += 1

# while + break（模拟重试）
attempts = 0
max_attempts = 3
while attempts < max_attempts:
    attempts += 1
    print(f"尝试第{attempts}次连接...")
    # 模拟：第2次成功
    if attempts == 2:
        print("连接成功！")
        break
else:
    # 循环正常结束（没遇到 break）才执行
    print("连接失败，已达最大重试次数")

# continue（跳过本次）
for i in range(10):
    if i % 2 == 0:
        continue  # 跳过偶数
    print(i)      # 只打印奇数：1,3,5,7,9

# 嵌套循环（九九乘法表）
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i}x{j}={i*j}", end=" ")
    print()
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| while 循环忘记更新条件变量 | 死循环 | 确保循环体内有改变条件的语句 |
| range(5) 以为是 1-5 | 实际是 0-4 | range 左闭右开，从0开始 |
| 遍历字典用 for v in dict 以为是值 | 实际遍历的是键 | 用 .values() 取值，.items() 取键值对 |
| break 只跳出内层循环 | 外层还在继续 | 多层跳出用标志位或函数 return |

### 动手

1. 用 for 循环计算 [1,2,3,4,5] 的乘积
2. 用 while 循环实现：从10倒数到1，打印每个数
3. 用 for + continue 打印 1-20 中所有不能被3整除的数
""")

leaf_comprehensions = make_leaf("py-basic-comprehensions", "推导式", "??", """### 课前

- **场景**：要把列表中每个元素做变换、筛选，写 for 循环太啰嗦。
- **目标**：掌握列表推导式、字典推导式、集合推导式，写出 Pythonic 代码。
- **先修**：循环 for/while

### 是什么

- **一句话定义**：推导式是用一行表达式从可迭代对象生成新列表/字典/集合的简洁写法。
- **优势**：比 for 循环更简洁、可读性更好、性能略优。
- **格式**：[表达式 for 变量 in 可迭代对象 if 条件]

### 怎么写

```python
# 列表推导式基本形式
nums = [1, 2, 3, 4, 5]
squares = [x ** 2 for x in nums]
print(squares)  # [1, 4, 9, 16, 25]

# 带条件筛选（if 在 for 后面）
evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8]

# 带条件变换（if-else 在 for 前面）
labels = ["高" if x >= 80 else "低" for x in [60, 85, 90, 40]]
print(labels)  # ['低', '高', '高', '低']

# 等价的 for 循环写法（对比）
squares2 = []
for x in nums:
    squares2.append(x ** 2)

# 嵌套推导式（展平二维列表）
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [x for row in matrix for x in row]
print(flat)  # [1, 2, 3, 4, 5, 6]

# 字典推导式
names = ["Ada", "Bob", "Cara"]
name_len = {name: len(name) for name in names}
print(name_len)  # {'Ada': 3, 'Bob': 3, 'Cara': 4}

# 字典推导式带条件
filtered = {k: v for k, v in name_len.items() if v >= 4}
print(filtered)  # {'Cara': 4}

# 集合推导式（自动去重）
nums_with_dup = [1, 2, 2, 3, 3, 3, 4]
unique_squares = {x ** 2 for x in nums_with_dup}
print(unique_squares)  # {1, 4, 9, 16}

# 实际应用：清洗数据
orders = ["  Apple ", " Banana ", "  Orange "]
cleaned = [s.strip().lower() for s in orders]
print(cleaned)  # ['apple', 'banana', 'orange']

# 生成器表达式（用圆括号，惰性计算，省内存）
gen = (x ** 2 for x in range(1000000))
# 不立即生成所有值，按需计算
print(sum(gen))  # 可以直接用于 sum/max/min 等
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 筛选条件写在 for 前面 | 语法错误或逻辑错 | 筛选（if 无 else）写 for 后面；变换（if-else）写 for 前面 |
| 推导式嵌套过多 | 可读性差 | 超过2层嵌套改用普通 for 循环 |
| 用列表推导式处理超大列表 | 内存爆 | 用生成器表达式（圆括号） |
| 字典推导式键重复 | 后面的覆盖前面的 | 确保键唯一，或先聚合 |

### 动手

1. 用列表推导式生成 1-20 中所有奇数的平方
2. 用字典推导式把 {"a":1, "b":2, "c":3} 的值都乘2
3. 用集合推导式从 ["apple", "banana", "apple", "orange", "banana"] 得到去重集合
""")

# --- 函数 ---
leaf_func_def = make_leaf("py-basic-func-def", "函数定义与调用", "?", """### 课前

- **场景**：一段计算折扣的代码要在多处使用，不想重复写。
- **目标**：掌握函数定义、调用、返回值、文档字符串。
- **先修**：控制流

### 是什么

- **一句话定义**：函数是可复用的代码块，接收输入参数，执行特定逻辑，返回输出结果。
- **核心要素**：def 关键字、函数名、参数列表、函数体、return 返回值。
- **好处**：代码复用、模块化、可读性、易维护。

### 怎么写

```python
# 基本函数定义
def greet(name):
    '''向指定的人打招呼。'''
    return f"你好，{name}！"

# 调用函数
result = greet("Ada")
print(result)  # 你好，Ada！

# 多参数函数
def calculate_total(price, quantity, discount=1.0):
    '''计算订单总金额。
    Args:
        price: 单价
        quantity: 数量
        discount: 折扣率，默认1.0（不打折）
    Returns:
        总金额
    '''
    subtotal = price * quantity
    total = subtotal * discount
    return round(total, 2)

# 调用（位置参数）
print(calculate_total(100, 2))         # 200.0
print(calculate_total(100, 2, 0.8))    # 160.0

# 调用（关键字参数，顺序可换）
print(calculate_total(price=50, quantity=3, discount=0.9))  # 135.0
print(calculate_total(discount=0.9, quantity=3, price=50))  # 同上

# 无 return 的函数（返回 None）
def print_welcome():
    print("欢迎使用系统")
    # 没有 return，默认返回 None

val = print_welcome()
print(val)  # None

# 多返回值（实际是元组）
def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(f"最小：{lo}，最大：{hi}")

# 函数作为变量传递
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

ops = {"+": add, "*": multiply}
print(ops["+"](3, 4))   # 7
print(ops["*"](3, 4))   # 12
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 函数定义后忘加冒号 | SyntaxError | def 行末尾必须加 : |
| 调用函数忘加括号 | 得到函数对象而非执行结果 | 调用必须加 () |
| 函数内修改全局变量不生效 | 局部变量遮蔽全局 | 用 global 声明，或通过参数/返回值传递 |
| 可变默认参数（如 def f(x=[])） | 多次调用共享同一个列表 | 默认参数用 None，函数内初始化 |

### 动手

1. 定义函数 bmi(weight, height)，返回 BMI 值（weight/height²）
2. 定义函数 is_even(n)，返回 True/False 判断是否偶数
3. 写一句「函数和直接写代码相比有什么好处」
""")

leaf_func_args = make_leaf("py-basic-func-args", "参数与返回值", "??", """### 课前

- **场景**：函数要接收不定数量的参数，要区分必填和可选参数。
- **目标**：掌握默认参数、可变参数 *args/**kwargs、关键字-only 参数、解包调用。
- **先修**：函数定义与调用

### 是什么

- **一句话定义**：参数是函数的输入接口；Python 支持灵活的参数传递方式，适配各种调用场景。
- **参数类型**：位置参数、默认参数、*args（可变位置参数）、**kwargs（可变关键字参数）。

### 怎么写

```python
# 默认参数（可选参数）
def power(base, exp=2):
    return base ** exp

print(power(3))     # 9（exp用默认值2）
print(power(3, 3))  # 27

# *args：接收任意数量的位置参数（元组）
def sum_all(*args):
    print(f"args类型：{type(args)}")  # tuple
    total = 0
    for num in args:
        total += num
    return total

print(sum_all(1, 2, 3))        # 6
print(sum_all(1, 2, 3, 4, 5))  # 15
print(sum_all())                # 0

# **kwargs：接收任意数量的关键字参数（字典）
def print_user(**kwargs):
    print(f"kwargs类型：{type(kwargs)}")  # dict
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print_user(name="Ada", age=28, city="上海")
print_user(name="Bob", role="admin")

# 组合使用（标准写法：位置参数, *args, 默认参数, **kwargs）
def flexible_func(a, b, *args, mode="normal", **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"mode={mode}")
    print(f"kwargs={kwargs}")

flexible_func(1, 2, 3, 4, mode="fast", key1="v1", key2="v2")

# 解包调用（* 解包列表/元组，** 解包字典）
def add_three(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add_three(*nums))  # 6（等价于 add_three(1, 2, 3)）

params = {"a": 10, "b": 20, "c": 30}
print(add_three(**params))  # 60

# 关键字-only 参数（* 后面的参数必须用关键字传递）
def configure(host, port, *, timeout=30, retries=3):
    print(f"{host}:{port}, timeout={timeout}, retries={retries}")

configure("localhost", 8080)  # OK
configure("localhost", 8080, timeout=60)  # OK
# configure("localhost", 8080, 60)  # TypeError！timeout必须用关键字

# 返回多个值（元组解包）
def analyze(numbers):
    return {
        "sum": sum(numbers),
        "avg": sum(numbers) / len(numbers),
        "max": max(numbers),
        "min": min(numbers)
    }

result = analyze([1, 2, 3, 4, 5])
print(result)
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 可变默认参数 def f(x=[]) | 多次调用共享状态 | 用 None 做默认，函数内 if x is None: x=[] |
| *args 当成列表用 | 类型是 tuple | 需要列表时 list(args) 转换 |
| 参数顺序混乱 | 调用时传错 | 遵循：位置 → *args → 默认 → **kwargs |
| 关键字参数和位置参数混用顺序错 | SyntaxError | 位置参数必须在关键字参数前面 |

### 动手

1. 定义函数 concat(*args, sep="-")，把所有字符串用 sep 连接
2. 定义函数 build_user(name, **kwargs)，返回包含 name 和所有额外属性的字典
3. 用 * 解包调用：定义 add(a,b,c)，用列表 [10,20,30] 调用
""")

leaf_lambda = make_leaf("py-basic-lambda", "lambda 与高阶函数", "??", """### 课前

- **场景**：排序时要按字典的某个key排，列表处理时要做个简单变换。
- **目标**：掌握 lambda 匿名函数、map/filter/sorted 等高阶函数。
- **先修**：参数与返回值

### 是什么

- **一句话定义**：lambda 是一行的匿名函数，适合简单的一次性操作；高阶函数是接收函数作为参数或返回函数的函数。
- **常用高阶函数**：sorted（排序）、map（映射变换）、filter（过滤）、reduce（累积）。

### 怎么写

```python
# lambda 基本语法：lambda 参数: 表达式
square = lambda x: x ** 2
print(square(5))  # 25

# 等价于
def square2(x):
    return x ** 2

# 多参数 lambda
add = lambda a, b: a + b
print(add(3, 4))  # 7

# lambda 常用于 sorted 的 key 参数
users = [
    {"name": "Ada", "age": 28, "score": 90},
    {"name": "Bob", "age": 35, "score": 75},
    {"name": "Cara", "age": 22, "score": 88},
]

# 按年龄排序
by_age = sorted(users, key=lambda u: u["age"])
print([u["name"] for u in by_age])  # ['Cara', 'Ada', 'Bob']

# 按分数降序
by_score_desc = sorted(users, key=lambda u: u["score"], reverse=True)
print([u["name"] for u in by_score_desc])  # ['Ada', 'Cara', 'Bob']

# map：对每个元素做变换
nums = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, nums))
print(squares)  # [1, 4, 9, 16, 25]

# 等价列表推导式（更 Pythonic）
squares2 = [x ** 2 for x in nums]

# filter：筛选满足条件的元素
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)  # [2, 4]

# 等价列表推导式
evens2 = [x for x in nums if x % 2 == 0]

# reduce：累积计算（需从 functools 导入）
from functools import reduce
product = reduce(lambda a, b: a * b, nums)
print(product)  # 120（1*2*3*4*5）

# 实际应用：按多个条件排序
# 先按分数降序，分数相同按年龄升序
complex_sort = sorted(users, key=lambda u: (-u["score"], u["age"]))
print([(u["name"], u["score"]) for u in complex_sort])

# lambda 作为返回值（闭包）
def make_multiplier(n):
    return lambda x: x * n

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| lambda 里写多行语句 | SyntaxError | lambda 只能是单个表达式，复杂逻辑用 def |
| map/filter 结果直接当列表用 | 得到 map/filter 对象 | 用 list() 转换，或直接用列表推导式 |
| lambda 捕获循环变量出错 | 所有 lambda 用最后一个值 | 用默认参数 lambda x, i=i: ... 绑定 |
| 过度使用 lambda | 可读性差 | 复杂逻辑用命名函数（def），lambda 只用于简单一次性操作 |

### 动手

1. 用 sorted + lambda 把 [("a", 3), ("b", 1), ("c", 2)] 按第二个元素升序排列
2. 用 map + lambda 把 ["apple", "banana"] 全部转大写
3. 用 filter + lambda 筛选 [1,2,3,4,5,6,7,8,9,10] 中大于5的数
""")

# --- 数据结构 ---
leaf_list = make_leaf("py-basic-list", "列表 list", "?", """### 课前

- **场景**：要存一组订单ID，动态增删，按顺序遍历。
- **目标**：掌握列表创建、索引切片、增删改查、常用方法、列表推导式。
- **先修**：变量与数据类型

### 是什么

- **一句话定义**：列表是有序、可变的元素集合，用方括号表示，元素可以是任意类型。
- **核心能力**：索引/切片、增删改查、排序、反转、遍历、推导式。
- **直觉**：像一排盒子，每个盒子有编号（索引），可以随时换内容、加盒子、删盒子。

### 怎么写

```python
# 创建列表
empty = []
nums = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, None]
nested = [[1, 2], [3, 4], [5, 6]]  # 二维列表

# 索引与切片（从0开始，左闭右开）
print(nums[0])    # 1（第一个）
print(nums[-1])   # 5（最后一个）
print(nums[1:4])  # [2, 3, 4]
print(nums[:3])   # [1, 2, 3]
print(nums[2:])   # [3, 4, 5]
print(nums[::-1]) # [5, 4, 3, 2, 1]（反转）

# 增删改查
fruits = ["apple", "banana"]

# 增加
fruits.append("orange")        # 末尾添加：['apple', 'banana', 'orange']
fruits.insert(1, "grape")      # 指定位置插入：['apple', 'grape', 'banana', 'orange']
fruits.extend(["mango", "pear"])  # 扩展（合并另一个列表）

# 删除
fruits.remove("banana")  # 按值删除第一个匹配项
popped = fruits.pop()     # 删除并返回最后一个元素
popped_idx = fruits.pop(0)  # 删除并返回指定索引元素
del fruits[0]             # 删除指定索引元素
fruits.clear()            # 清空列表

# 修改
nums = [1, 2, 3]
nums[0] = 100  # 直接赋值修改
nums[1:3] = [200, 300]  # 切片赋值

# 查找
print(nums.index(200))   # 查找值的索引（找不到报错）
print(100 in nums)       # 判断是否存在（True）
print(nums.count(100))   # 统计出现次数

# 排序与反转
data = [3, 1, 4, 1, 5, 9, 2, 6]
data.sort()                # 原地升序排序
data.sort(reverse=True)    # 原地降序排序
sorted_data = sorted(data) # 返回新的排序后的列表（不改变原列表）
data.reverse()             # 原地反转

# 其他常用方法
print(len(nums))     # 长度
print(sum(nums))     # 求和（数值列表）
print(max(nums))     # 最大值
print(min(nums))     # 最小值

# 遍历
for item in nums:
    print(item)
for idx, item in enumerate(nums):
    print(f"{idx}: {item}")

# 列表拼接与重复
a = [1, 2]
b = [3, 4]
print(a + b)    # [1, 2, 3, 4]
print(a * 3)    # [1, 2, 1, 2, 1, 2]

# 列表推导式（见推导式章节）
squares = [x ** 2 for x in range(10)]
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 索引越界 nums[100] | IndexError | 索引范围 0 到 len(nums)-1 |
| 遍历列表时删除元素 | 跳过元素或索引错乱 | 遍历副本或用列表推导式过滤 |
| sort() 和 sorted() 混淆 | sort() 原地修改返回None；sorted() 返回新列表 | 需要原列表不变用 sorted() |
| 用 + 循环拼接列表 | 性能差（每次创建新列表） | 用 append/extend，或先收集再 join |
| 列表是可变对象，函数内修改影响外部 | 意外副作用 | 需要副本用 list(x) 或 x.copy() |

### 动手

1. 创建列表 [5,2,8,1,9]，排序后在末尾添加 0，再反转
2. 用 index 找到 8 的位置，用 pop 删除它
3. 写一句「列表和元组的区别是什么，什么时候用哪个」
""")

leaf_dict = make_leaf("py-basic-dict", "字典 dict", "?", """### 课前

- **场景**：要存用户信息（姓名、年龄、城市），通过键名快速查找。
- **目标**：掌握字典创建、增删改查、遍历、常用方法、字典推导式。
- **先修**：列表 list

### 是什么

- **一句话定义**：字典是键值对的无序（3.7+有序）集合，用花括号表示，通过键快速查找值。
- **核心能力**：按键存取、增删改查、遍历键/值/键值对、推导式。
- **直觉**：像一本字典，单词（键）对应解释（值），查单词比翻页快得多。

### 怎么写

```python
# 创建字典
empty = {}
user = {"name": "Ada", "age": 28, "city": "上海"}

# 访问值
print(user["name"])      # Ada（按键访问，键不存在报错）
print(user.get("age"))   # 28（get方法，键不存在返回None）
print(user.get("email", "未设置"))  # 未设置（指定默认值）

# 增加/修改
user["email"] = "ada@example.com"  # 增加新键值对
user["age"] = 29                    # 修改已有键的值
user.update({"role": "admin", "status": "active"})  # 批量更新

# 删除
del user["city"]         # 删除指定键
popped = user.pop("role")  # 删除并返回值
user.popitem()            # 删除并返回最后一个键值对（3.7+）
user.clear()              # 清空

# 查找与判断
print("name" in user)     # 判断键是否存在（True）
print(user.keys())        # 所有键：dict_keys(['name', 'age', ...])
print(user.values())      # 所有值：dict_values(['Ada', 28, ...])
print(user.items())       # 所有键值对：dict_items([('name','Ada'), ...])

# 遍历
for key in user:              # 遍历键
    print(key)
for key, value in user.items():  # 遍历键值对（最常用）
    print(f"{key}: {value}")
for value in user.values():    # 遍历值
    print(value)

# 嵌套字典（JSON-like 结构）
company = {
    "name": "数据科技",
    "employees": [
        {"name": "Ada", "role": "工程师"},
        {"name": "Bob", "role": "产品经理"}
    ],
    "address": {
        "city": "上海",
        "district": "浦东新区"
    }
}
print(company["employees"][0]["name"])  # Ada
print(company["address"]["city"])         # 上海

# 字典推导式
names = ["Ada", "Bob", "Cara"]
name_length = {name: len(name) for name in names}
print(name_length)  # {'Ada': 3, 'Bob': 3, 'Cara': 4}

# 带条件的字典推导式
filtered = {k: v for k, v in user.items() if v is not None}

# setdefault：键不存在则设置默认值并返回
counts = {}
for word in ["apple", "banana", "apple", "orange", "banana", "apple"]:
    counts[word] = counts.setdefault(word, 0) + 1
print(counts)  # {'apple': 3, 'banana': 2, 'orange': 1}

# 常用：统计频率（更简单的方式用 collections.Counter）
from collections import Counter
word_counts = Counter(["apple", "banana", "apple", "orange"])
print(word_counts)  # Counter({'apple': 2, 'banana': 1, 'orange': 1})
print(word_counts.most_common(2))  # 出现最多的2个
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 访问不存在的键 user["xxx"] | KeyError | 用 .get(key, default) 或先判断 key in dict |
| 用 for v in dict 以为遍历值 | 实际遍历的是键 | 用 .values() 取值，.items() 取键值对 |
| 字典键用可变类型（列表） | TypeError（unhashable） | 键必须是不可变类型（字符串/数字/元组） |
| 遍历字典时修改字典 | RuntimeError | 遍历列表副本或先收集要删的键 |
| 以为字典有序（旧版本） | 顺序不确定 | Python 3.7+ 保证插入顺序，之前版本不保证 |

### 动手

1. 创建字典 {"a":1, "b":2, "c":3}，把所有值乘2，添加 "d":4
2. 用字典统计 "hello world" 中每个字符出现的次数
3. 写一句「字典和列表的查找效率有什么不同」
""")

leaf_tuple_set = make_leaf("py-basic-tuple-set", "元组与集合", "?", """### 课前

- **场景**：要存一组不可变的坐标，要对列表去重，要做集合交并差运算。
- **目标**：掌握元组（不可变序列）和集合（无序不重复）的创建、操作、适用场景。
- **先修**：列表 list

### 是什么

- **元组 tuple**：有序、不可变的元素集合，用圆括号表示，相当于「只读列表」。
- **集合 set**：无序、不重复的元素集合，用花括号表示，擅长去重和集合运算。
- **适用场景**：元组用于固定不变的数据（如坐标、配置）；集合用于去重、成员判断、集合运算。

### 怎么写

```python
# ===== 元组 tuple =====
# 创建元组
point = (3, 4)
single = (1,)   # 单元素元组必须加逗号！(1) 只是整数
empty_tuple = ()
mixed_tuple = (1, "hello", 3.14, True)

# 元组解包（非常常用）
x, y = point
print(f"x={x}, y={y}")  # x=3, y=4

# 交换变量（元组解包的经典应用）
a, b = 10, 20
a, b = b, a  # 交换！
print(f"a={a}, b={b}")  # a=20, b=10

# 函数返回多个值（实际是元组）
def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([3, 1, 4, 1, 5])
print(f"最小={lo}, 最大={hi}")

# 元组的操作（和列表类似，但不能修改）
nums = (1, 2, 3, 4, 5)
print(nums[0])     # 索引
print(nums[1:4])   # 切片
print(len(nums))   # 长度
print(3 in nums)   # 成员判断
for n in nums:     # 遍历
    print(n)

# nums[0] = 100  # TypeError！元组不可变

# 元组拼接（创建新元组，不是修改）
t1 = (1, 2)
t2 = (3, 4)
print(t1 + t2)  # (1, 2, 3, 4)

# 元组作为字典的键（因为不可变、可哈希）
coordinates = {
    (31.23, 121.47): "上海",
    (39.90, 116.40): "北京"
}
print(coordinates[(31.23, 121.47)])  # 上海

# ===== 集合 set =====
# 创建集合
fruits = {"apple", "banana", "orange"}
empty_set = set()  # 注意：{} 是空字典，不是空集合！

# 从列表创建集合（自动去重）
nums_with_dup = [1, 2, 2, 3, 3, 3, 4, 5, 5]
unique_nums = set(nums_with_dup)
print(unique_nums)  # {1, 2, 3, 4, 5}

# 增删
fruits.add("grape")        # 添加元素
fruits.update({"mango", "pear"})  # 批量添加
fruits.remove("banana")    # 删除（不存在报错）
fruits.discard("xxx")      # 删除（不存在不报错）
popped = fruits.pop()      # 随机删除并返回一个元素
fruits.clear()             # 清空

# 集合运算
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(a | b)   # 并集：{1, 2, 3, 4, 5, 6, 7, 8}
print(a & b)   # 交集：{4, 5}
print(a - b)   # 差集（a有b没有）：{1, 2, 3}
print(a ^ b)   # 对称差集（不同时存在）：{1, 2, 3, 6, 7, 8}

# 集合关系
print(a.issubset({1, 2, 3, 4, 5, 6}))   # a是否是子集：True
print(a.issuperset({1, 2, 3}))            # a是否是超集：True
print(a.isdisjoint({10, 11}))             # 是否无交集：True

# 集合推导式
squares_set = {x ** 2 for x in range(10)}
print(squares_set)

# 实际应用：快速去重 + 成员判断
# 列表的 in 是 O(n)，集合的 in 是 O(1)
big_list = list(range(1000000))
big_set = set(big_list)
print(999999 in big_set)  # 极快

# 找两个列表的共同元素
list1 = [1, 2, 3, 4, 5]
list2 = [4, 5, 6, 7, 8]
common = set(list1) & set(list2)
print(common)  # {4, 5}
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 单元素元组写成 (1) | 实际是整数不是元组 | 必须加逗号：(1,) |
| 空集合写成 {} | 实际是空字典 | 空集合用 set() |
| 试图修改元组元素 | TypeError | 元组不可变，需要修改用列表 |
| 集合里放可变类型（列表/字典） | TypeError（unhashable） | 集合元素必须是不可变类型 |
| 以为集合有序 | 顺序不确定 | 集合是无序的，需要有序用列表 |
| 遍历集合时删除元素 | RuntimeError | 先收集要删的元素，遍历完再删 |

### 动手

1. 用元组解包交换 x=10, y=20 的值
2. 用集合对 [1,2,2,3,3,3,4,5,5] 去重，再转回列表
3. 用集合运算求 {1,2,3,4,5} 和 {3,4,5,6,7} 的交集和差集
""")

leaf_builtins = make_leaf("py-basic-builtins", "常用内置函数", "??", """### 课前

- **场景**：要对列表求和、找最大、排序、类型转换、遍历带索引。
- **目标**：掌握 Python 最常用的内置函数，避免重复造轮子。
- **先修**：列表/字典/元组集合

### 是什么

- **一句话定义**：内置函数是 Python 解释器自带的函数，不需要 import 即可直接使用，覆盖类型转换、数学运算、序列操作、迭代工具等。
- **学习策略**：不需要背所有，掌握最常用的 20 个左右，其余用时查文档。

### 怎么写

```python
# ===== 类型转换 =====
print(int("123"))        # 字符串转整数：123
print(float("3.14"))     # 字符串转浮点数：3.14
print(str(123))          # 整数转字符串："123"
print(bool(0))           # 转布尔：False（0/空/None为False）
print(list((1, 2, 3)))   # 元组转列表：[1, 2, 3]
print(tuple([1, 2, 3]))  # 列表转元组：(1, 2, 3)
print(set([1, 1, 2, 2])) # 列表转集合（去重）：{1, 2}
print(dict([("a", 1), ("b", 2)]))  # 键值对列表转字典

# ===== 数学运算 =====
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(sum(nums))    # 求和：31
print(max(nums))    # 最大值：9
print(min(nums))    # 最小值：1
print(abs(-5))      # 绝对值：5
print(round(3.14159, 2))  # 四舍五入保留2位：3.14
print(pow(2, 10))   # 幂运算：1024（等价于 2**10）
print(divmod(10, 3))  # 商和余数：(3, 1)

# ===== 序列操作 =====
print(len(nums))           # 长度：8
print(sorted(nums))        # 返回排序后的新列表：[1, 1, 2, 3, 4, 5, 6, 9]
print(sorted(nums, reverse=True))  # 降序
print(reversed(nums))      # 返回反转迭代器（用 list() 转换）
print(list(reversed(nums)))

# enumerate：同时获取索引和值（非常常用）
fruits = ["apple", "banana", "orange"]
for idx, fruit in enumerate(fruits):
    print(f"{idx}: {fruit}")
# 0: apple
# 1: banana
# 2: orange

# zip：同时遍历多个可迭代对象（按最短的来）
names = ["Ada", "Bob", "Cara"]
ages = [28, 35, 22]
cities = ["上海", "北京"]
for name, age, city in zip(names, ages, cities):
    print(f"{name}({age}) - {city}")
# Ada(28) - 上海
# Bob(35) - 北京
# Cara 被跳过（因为 cities 只有2个）

# zip 反操作：解压
pairs = [("a", 1), ("b", 2), ("c", 3)]
letters, numbers = zip(*pairs)
print(letters)  # ('a', 'b', 'c')
print(numbers)  # (1, 2, 3)

# ===== 判断与检查 =====
print(all([True, True, False]))  # 所有都为True才True：False
print(any([False, False, True]))  # 有一个为True就True：True
print(all(x > 0 for x in [1, 2, 3]))  # 所有数都大于0：True
print(any(x < 0 for x in [1, -2, 3]))  # 有负数：True

# ===== 输入输出 =====
# name = input("请输入名字：")  # 读取用户输入（返回字符串）
print("Hello", "world")          # 打印输出
print("a", "b", "c", sep="-")  # 分隔符：a-b-c
print("hello", end=" ")        # 结束符（默认换行）
print("world")                  # 同一行：hello world

# ===== 其他常用 =====
print(range(5))           # 范围对象：range(0, 5)（用 list() 转换）
print(list(range(2, 10, 2)))  # [2, 4, 6, 8]

print(type("hello"))      # 类型：<class 'str'>
print(isinstance("hello", str))   # 是否是某类型：True
print(isinstance(3, (int, float)))  # 是否是多个类型之一：True

print(id(nums))           # 对象的内存地址
print(hash("hello"))      # 哈希值（不可变对象才可哈希）

# eval/exec（慎用，有安全风险）
result = eval("2 + 3 * 4")  # 执行表达式字符串：14

# ===== 实际应用组合 =====
# 找出列表中最大的3个
top3 = sorted(nums, reverse=True)[:3]
print(top3)  # [9, 6, 5]

# 按字典的某个值排序
users = [{"name": "Ada", "score": 90}, {"name": "Bob", "score": 75}]
sorted_users = sorted(users, key=lambda u: u["score"], reverse=True)

# 统计满足条件的数量
count = sum(1 for x in nums if x > 3)
print(count)  # 4（4,5,9,6大于3）
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| sorted() 以为会修改原列表 | 原列表不变，返回新列表 | 需要原地排序用 .sort() |
| zip 以为会按最长的补齐 | 按最短的来，多余的被忽略 | 需要补齐用 itertools.zip_longest |
| input() 以为返回数字 | 返回字符串，需要 int() 转换 | 数字输入用 int(input(...)) |
| type() 和 isinstance() 混淆 | type 不考虑继承，isinstance 考虑 | 类型判断优先用 isinstance() |
| all([]) 返回 True 以为是 bug | 空序列的 all 是 True（vacuous truth） | 空序列需要先判断 len |
| eval() 执行用户输入 | 安全风险（代码注入） | 避免用 eval，或用 ast.literal_eval |

### 动手

1. 用 sum + 生成器表达式计算 [1,2,3,4,5] 中所有偶数的和
2. 用 enumerate 打印列表 ["a","b","c"] 的索引和值，索引从1开始
3. 用 zip 把 ["name","age"] 和 ["Ada",28] 组合成字典
""")

# ========== 组装章节 ==========
chapter_syntax = make_chapter("py-basic-syntax", "语法基础", "?", [leaf_vars, leaf_operators, leaf_strings])
chapter_control_flow = make_chapter("py-basic-control-flow", "控制流", "?", [leaf_if, leaf_loops, leaf_comprehensions])
chapter_functions = make_chapter("py-basic-functions", "函数", "?", [leaf_func_def, leaf_func_args, leaf_lambda])
chapter_data_structures = make_chapter("py-basic-data-structures", "数据结构", "?", [leaf_list, leaf_dict, leaf_tuple_set, leaf_builtins])

# ========== 领域节点 ==========
domain_content = """### 课前 · 领域导读

- **领域**：Python 基础
- **在整棵树中的角色**：Python 语言的基本功，是 pandas、可视化、生态库的前提。
- **为什么先学这块**：不会语法和数据结构，pandas 代码只能抄不能改，遇到报错看不懂。
- **与周边关系**：基础语法 → pandas 数据表 → 可视化 → 生态与加速。
- **学完本领域的阶段目标**：能独立写函数、操作列表字典、用推导式处理数据、看懂常见报错。

### 故事线（先建立全局图）

```text
语法基础 → 控制流 → 函数 → 数据结构
```

### 本领域覆盖什么

围绕「Python 基础」组织若干章节。你不必一次学完所有叶课，但应先读各**章节导读**，再按推荐顺序点绿色叶节点。

### 子章节地图

| 章节 | 一句话 |
|---|---|
| 语法基础 | 变量、数据类型、运算符、字符串——Python 的字母表。 |
| 控制流 | if 判断、for/while 循环、推导式——让程序做选择和重复。 |
| 函数 | 定义可复用代码块、参数传递、lambda——模块化的第一步。 |
| 数据结构 | 列表、字典、元组、集合、内置函数——数据怎么存怎么取。 |

### 推荐学习顺序

```text
语法基础 → 控制流 → 函数 → 数据结构
```

### 学完怎么验收

1. 能用自己的话讲清本领域解决什么问题、不解决什么
2. 每个子章节至少完成 1 片叶讲义的「动手」题
3. 能指出本领域最容易翻车的点：**可变默认参数、遍历列表时删除、字典键不存在报错。**

### 常见误区

| 误区 | 纠正 |
|---|---|
| 只看视频不写代码 | 编程必须动手，每课至少跑通示例 |
| 跳过基础直接学 pandas | 语法不熟会卡在基础报错上 |
| 背 API 而不理解 | 理解原理比背函数名更重要 |
| 遇到报错就放弃 | 报错信息是最好的老师，学会读 Traceback |

### 与整树出口的关系

整树阶段出口是：能独立用 pandas 完成清洗聚合关联，并有一条可复现基线。本领域是通向该出口的第一块拼图，没有基础语法，后面的 pandas 代码只能抄不能改。

### 练习建议（领域级）

- **时间盒**：每个子章节先留 30-45 分钟，只求跑通主路径，不追求一次记完所有边角
- **输出物**：每章结束写 3 条笔记——定义、反例、迁移到实际工作的改动点
- **对照**：学完领域后回去做练习场对应难度题做验收

### 下一动

打开第一个子章节的导读，按叶列表开课。本领域约 **13** 片叶讲义。
"""

domain_node = {
    "id": "py-basics",
    "title": "Python 基础",
    "level": "?",
    "content": domain_content,
    "children": [chapter_syntax, chapter_control_flow, chapter_functions, chapter_data_structures]
}

# 输出 JSON
output_path = r"D:\cursor\数据学习平台\kg-data\py-basics-temp.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(domain_node, f, ensure_ascii=False, indent=2)

print(f"Generated: {output_path}")
print(f"Size: {os.path.getsize(output_path)} bytes")
