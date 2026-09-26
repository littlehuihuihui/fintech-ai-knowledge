#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充Python基础核心特性：文件操作、异常处理、模块包、迭代器生成器、装饰器、上下文管理器"""

import json, re

filepath = r"D:\cursor\数据学习平台\kg-data\embed-python.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["python"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def make_leaf(node_id, title, content):
    return {"id": node_id, "title": title, "level": "??", "content": content, "children": []}

def make_chapter(node_id, title, leaves, intro):
    leaf_list = "、".join([l["title"] for l in leaves])
    content = f'''### 课前 · 章节导读

- **章节**：{title}
- **学习目标**：掌握本章核心概念和常用操作。
- **先修**：Python 语法基础、控制流、函数

### 本章叶课

{intro}

### 推荐顺序

```text
{leaf_list}
```

### 下一动

点开第 1 片绿色叶节点。本章合计约 **{len(leaves)}** 片叶讲义。
'''
    return {"id": node_id, "title": title, "level": "??", "content": content, "lessonParent": True, "children": leaves}

# ========== 1. 文件操作 ==========
file_content = '''### 课前

- **场景**：要读取CSV/文本文件、写入结果、遍历目录、处理文件路径。
- **目标**：掌握 open() 读写文件、with 语句、os/pathlib 路径操作、常用文件格式读写。
- **先修**：Python 基础语法、字符串操作

### 是什么

- **一句话定义**：文件操作是 Python 与外部存储交互的基础，通过 open() 打开文件、读写内容、关闭文件，配合 os/pathlib 管理目录和路径，是数据处理的必备技能。
- **核心能力**：文本读写、二进制读写、目录遍历、路径拼接、文件存在判断、常用格式（CSV/JSON/Excel）。

### 怎么写

```python
# ============================================================
# 例1：基本文件读取（open + read）
# ============================================================
# 方法1：open + close（不推荐，容易忘记关闭）
f = open("data.txt", "r", encoding="utf-8")
content = f.read()
f.close()

# 方法2：with 语句（推荐，自动关闭文件）
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()  # 读取全部内容
# with 块结束后文件自动关闭，即使发生异常也会关闭

# ============================================================
# 例2：逐行读取（大文件常用，避免内存溢出）
# ============================================================
with open("large_file.txt", "r", encoding="utf-8") as f:
    for line in f:  # 逐行迭代，内存友好
        print(line.strip())  # strip() 去掉换行符

# readlines() 读取所有行到列表（小文件可用，大文件耗内存）
with open("data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()  # 返回列表，每个元素是一行

# ============================================================
# 例3：文件写入（write / writelines）
# ============================================================
# "w" 模式：覆盖写入（文件不存在则创建，存在则清空重写）
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("第一行\\n")
    f.write("第二行\\n")
    f.writelines(["第三行\\n", "第四行\\n"])  # 写入列表

# "a" 模式：追加写入（在文件末尾添加，不覆盖原有内容）
with open("output.txt", "a", encoding="utf-8") as f:
    f.write("追加的一行\\n")

# "x" 模式：排他创建（文件已存在则报错，用于防止覆盖）
# with open("new_file.txt", "x", encoding="utf-8") as f:
#     f.write("新文件")

# ============================================================
# 例4：文件模式速查
# ============================================================
# "r"  只读（默认），文件不存在报错
# "w"  只写，覆盖原有内容，文件不存在则创建
# "a"  追加，在末尾写入，文件不存在则创建
# "x"  排他创建，文件已存在则报错
# "r+" 读写（可读可写，不覆盖）
# "w+" 读写（覆盖后读写）
# "a+" 读写（追加模式读写）
# 加 "b" 表示二进制模式："rb"/"wb"/"ab"（图片/视频/Excel等）

# ============================================================
# 例5：os 模块 —— 目录和文件操作
# ============================================================
import os

# 路径操作
os.getcwd()                    # 获取当前工作目录
os.listdir(".")                # 列出目录下所有文件和文件夹
os.makedirs("data/output", exist_ok=True)  # 创建多级目录，exist_ok=True避免已存在报错
os.path.exists("data.txt")     # 判断文件/目录是否存在
os.path.isfile("data.txt")     # 判断是否是文件
os.path.isdir("data")          # 判断是否是目录
os.path.getsize("data.txt")    # 获取文件大小（字节）
os.remove("temp.txt")          # 删除文件
os.rename("old.txt", "new.txt")  # 重命名文件

# 路径拼接（不要用字符串拼接，用 os.path.join）
path = os.path.join("data", "subdir", "file.txt")
# Windows: data\\subdir\\file.txt
# macOS/Linux: data/subdir/file.txt

# 遍历目录（递归）
for root, dirs, files in os.walk("data"):
    for file in files:
        full_path = os.path.join(root, file)
        print(full_path)

# ============================================================
# 例6：pathlib —— 面向对象的路径操作（Python 3.4+ 推荐）
# ============================================================
from pathlib import Path

# 路径对象
p = Path("data/subdir/file.txt")
p.exists()           # 是否存在
p.is_file()          # 是否是文件
p.is_dir()           # 是否是目录
p.name               # 文件名（含扩展名）：file.txt
p.stem               # 文件名（不含扩展名）：file
p.suffix             # 扩展名：.txt
p.parent             # 父目录：data/subdir
p.absolute()         # 绝对路径

# 路径拼接（用 / 运算符，比 os.path.join 更优雅）
p = Path("data") / "subdir" / "file.txt"

# 创建目录
Path("data/output").mkdir(parents=True, exist_ok=True)

# 遍历目录
for p in Path("data").iterdir():  # 非递归
    print(p.name)

for p in Path("data").rglob("*.csv"):  # 递归查找所有csv文件
    print(p)

# 读写文件（pathlib 直接支持）
content = Path("data.txt").read_text(encoding="utf-8")
Path("output.txt").write_text("hello", encoding="utf-8")

# ============================================================
# 例7：CSV 文件读写（标准库 csv）
# ============================================================
import csv

# 读取 CSV
with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)  # 字典读取，第一行为键
    for row in reader:
        print(row["姓名"], row["年龄"])

# 写入 CSV
with open("output.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["姓名", "年龄"])
    writer.writeheader()
    writer.writerow({"姓名": "张三", "年龄": 25})
    writer.writerows([{"姓名": "李四", "年龄": 30}, {"姓名": "王五", "年龄": 28}])

# ============================================================
# 例8：JSON 文件读写（标准库 json）
# ============================================================
import json

# 读取 JSON
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)  # 解析为 Python 字典/列表

# 写入 JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    # ensure_ascii=False：中文不转义
    # indent=2：格式化缩进，可读性好
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 忘记 close() 文件 | 文件句柄泄漏，数据可能未写入 | 永远用 with 语句，自动关闭 |
| 用字符串拼接路径 | Windows/Linux 分隔符不一致导致报错 | 用 os.path.join 或 pathlib 的 / 运算符 |
| 大文件用 read() 全部读入 | 内存溢出 | 大文件逐行迭代：for line in f |
| 写入时不指定 encoding | Windows 默认 GBK，中文乱码 | 始终指定 encoding="utf-8" |
| "w" 模式打开已有文件 | 原有内容被清空覆盖 | 需要追加用 "a"，需要防覆盖用 "x" |
| CSV 写入不加 newline="" | Windows 下出现空行 | CSV 写入必须加 newline="" |
| JSON 写入中文全是 \\uXXXX | ensure_ascii 默认 True | 设置 ensure_ascii=False |

### 动手

1. 用 with 语句读取一个文本文件，统计行数和字符数
2. 用 pathlib 遍历目录，找出所有 .csv 文件并打印路径
3. 读取一个 CSV 文件，筛选出年龄大于25的记录，写入新的 CSV 文件
4. 将一个字典数据写入 JSON 文件，要求中文正常显示、格式化缩进
'''

# ========== 2. 异常处理 ==========
exception_content = '''### 课前

- **场景**：程序运行时可能遇到文件不存在、除零、索引越界、网络超时等错误，需要优雅处理而不是直接崩溃。
- **目标**：掌握 try/except/else/finally 异常处理、常见异常类型、自定义异常、异常最佳实践。
- **先修**：Python 基础语法、函数

### 是什么

- **一句话定义**：异常处理是 Python 的错误管理机制，通过 try/except 捕获运行时错误，避免程序崩溃，让程序在出错时能优雅降级或恢复，是健壮程序的必备技能。
- **核心理念**：异常不是错误，是"意料之外的情况"；好的程序应该预见异常并妥善处理。

### 怎么写

```python
# ============================================================
# 例1：基本 try/except（捕获异常）
# ============================================================
try:
    result = 10 / 0  # 会触发 ZeroDivisionError
except ZeroDivisionError:
    print("错误：不能除以零")
# 程序不会崩溃，继续执行后面的代码

# ============================================================
# 例2：获取异常信息（as e）
# ============================================================
try:
    int("abc")  # 会触发 ValueError
except ValueError as e:
    print(f"转换失败: {e}")  # e 是异常对象，包含详细信息
    print(f"异常类型: {type(e).__name__}")

# ============================================================
# 例3：多个 except 分支（不同异常不同处理）
# ============================================================
try:
    num = int(input("请输入数字: "))
    result = 100 / num
    print(f"结果: {result}")
except ValueError:
    print("输入的不是有效数字")
except ZeroDivisionError:
    print("不能输入零")
except Exception as e:  # 兜底：捕获所有其他异常
    print(f"发生未知错误: {e}")

# ============================================================
# 例4：else 子句（没有异常时执行）
# ============================================================
try:
    f = open("data.txt", "r", encoding="utf-8")
except FileNotFoundError:
    print("文件不存在")
else:
    # 只有 try 块没有异常时才执行 else
    content = f.read()
    print(f"文件内容长度: {len(content)}")
    f.close()

# ============================================================
# 例5：finally 子句（无论是否异常都执行，常用于清理）
# ============================================================
try:
    f = open("data.txt", "r", encoding="utf-8")
    content = f.read()
except FileNotFoundError:
    print("文件不存在")
else:
    print(content)
finally:
    # 无论是否发生异常，finally 都会执行
    # 常用于关闭文件、释放资源、关闭数据库连接
    if 'f' in locals() and not f.closed:
        f.close()
    print("清理完成")

# 注意：with 语句本质上就是 finally 的语法糖（自动调用 __exit__）

# ============================================================
# 例6：常见异常类型速查
# ============================================================
# SyntaxError      语法错误（代码写错了，编译时就报错）
# NameError        变量未定义
# TypeError        类型错误（如字符串和数字相加）
# ValueError       值错误（如 int("abc")）
# IndexError       索引越界（如 list[10] 但列表只有3个元素）
# KeyError         字典键不存在（如 dict["不存在的键"]）
# AttributeError   属性不存在（如 obj.nonexistent_method()）
# ZeroDivisionError 除零错误
# FileNotFoundError 文件不存在
# PermissionError  权限不足
# IOError          输入输出错误
# ImportError      导入模块失败
# ModuleNotFoundError 模块不存在
# RecursionError   递归深度超限
# StopIteration    迭代器结束
# KeyboardInterrupt 用户中断（Ctrl+C）

# ============================================================
# 例7：异常层级（捕获父类会捕获所有子类）
# ============================================================
# Exception 是大多数异常的父类
# ArithmeticError → ZeroDivisionError
# LookupError → IndexError, KeyError
# OSError → FileNotFoundError, PermissionError

# 捕获顺序：从具体到宽泛（先子类后父类）
try:
    1 / 0
except ZeroDivisionError:  # 先捕获具体的
    print("除零错误")
except ArithmeticError:    # 再捕获父类
    print("算术错误")
except Exception:          # 最后兜底
    print("其他错误")

# 错误顺序：如果先写 Exception，后面的具体异常永远不会被触发
# try:
#     1 / 0
# except Exception:  # 这里已经捕获了
#     print("兜底")
# except ZeroDivisionError:  # 永远不会执行！
#     print("除零")

# ============================================================
# 例8：主动抛出异常（raise）
# ============================================================
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")  # 主动抛出异常
    return a / b

try:
    divide(10, 0)
except ValueError as e:
    print(f"捕获到异常: {e}")

# 重新抛出异常（捕获后处理，再向上传递）
try:
    try:
        1 / 0
    except ZeroDivisionError:
        print("记录日志...")
        raise  # 重新抛出，让上层处理
except ZeroDivisionError:
    print("上层捕获")

# ============================================================
# 例9：自定义异常（继承 Exception）
# ============================================================
class BusinessError(Exception):
    """业务异常基类"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

class InsufficientBalanceError(BusinessError):
    """余额不足异常"""
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientBalanceError(
            f"余额不足：当前余额{balance}，取款{amount}",
            code="INSUFFICIENT_BALANCE"
        )
    return balance - amount

try:
    withdraw(100, 200)
except InsufficientBalanceError as e:
    print(f"错误码: {e.code}, 消息: {e}")

# ============================================================
# 例10：异常处理最佳实践
# ============================================================
# 1. 不要用裸 except（会捕获所有异常包括 KeyboardInterrupt）
# 错误：except: （捕获一切，包括 Ctrl+C）
# 正确：except Exception: 或具体异常类型

# 2. 不要吞掉异常（捕获后什么都不做）
# 错误：except: pass （隐藏了错误，调试困难）
# 正确：至少记录日志，或向上抛出

# 3. 尽量捕获具体异常，而不是宽泛的 Exception
# 错误：except Exception as e: print(e) （不知道会发生什么）
# 正确：except (FileNotFoundError, PermissionError) as e: ...

# 4. 用 finally 或 with 做资源清理
# 5. 异常信息要详细，便于调试
# 6. 不要用异常控制正常流程（异常应该是"异常"情况）

# 示例：健壮的文件读取函数
def read_file_safe(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None
    except PermissionError:
        print(f"权限不足: {filepath}")
        return None
    except UnicodeDecodeError:
        print(f"编码错误，尝试其他编码: {filepath}")
        with open(filepath, "r", encoding="gbk") as f:
            return f.read()
    except Exception as e:
        print(f"读取文件时发生未知错误: {e}")
        return None
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 裸 except: | 捕获包括 Ctrl+C 在内的一切，无法中断 | 用 except Exception 或具体异常类型 |
| except: pass | 吞掉异常，隐藏错误，调试困难 | 至少记录日志，或向上抛出 |
| 先写 Exception 后写具体异常 | 具体异常永远不会被触发 | 捕获顺序从具体到宽泛（先子类后父类） |
| 忘记 finally 清理资源 | 文件/连接泄漏 | 用 with 语句（推荐）或 finally 清理 |
| 用异常控制正常流程 | 性能差、代码难读 | 正常流程用 if/else，异常只处理意外情况 |
| 异常信息太简单 | 调试困难 | 异常消息要包含上下文（哪个文件、什么操作） |
| 捕获后不处理也不抛出 | 静默失败 | 要么处理，要么记录日志后重新抛出 |

### 动手

1. 写一个函数，读取用户输入的数字并计算100除以该数，处理 ValueError 和 ZeroDivisionError
2. 写一个健壮的文件读取函数，处理文件不存在、权限不足、编码错误三种情况
3. 自定义一个"年龄不合法"异常，在函数中验证年龄（0-150），不合法时抛出
4. 用 try/except/else/finally 完整结构写一个数据库查询的模拟代码
'''

# ========== 3. 模块与包 ==========
module_content = '''### 课前

- **场景**：代码越来越多，需要拆分到多个文件、复用别人写好的库、管理项目结构。
- **目标**：掌握 import 导入模块、自定义模块、包的结构、__init__.py、常用标准库、第三方库安装。
- **先修**：Python 基础语法、函数、文件操作

### 是什么

- **一句话定义**：模块是包含 Python 代码的 .py 文件，包是包含多个模块的目录（有 __init__.py），通过 import 语句复用代码，是 Python 代码组织和复用的核心机制。
- **核心理念**：Don't Repeat Yourself（DRY）—— 把可复用的代码抽到模块里，需要时导入。

### 怎么写

```python
# ============================================================
# 例1：import 基本用法
# ============================================================
import math  # 导入整个模块
print(math.pi)  # 通过模块名访问
print(math.sqrt(16))  # 4.0

from math import sqrt, pi  # 从模块导入特定函数/变量
print(sqrt(16))  # 直接使用，不需要 math. 前缀
print(pi)

from math import *  # 导入模块中所有公开名称（不推荐，可能命名冲突）
# 只在交互式环境或确定无冲突时使用

import math as m  # 给模块起别名
print(m.sqrt(16))  # 通过别名访问

from math import sqrt as square_root  # 给导入的函数起别名
print(square_root(16))

# ============================================================
# 例2：自定义模块（写一个 .py 文件，然后导入）
# ============================================================
# 文件：my_utils.py
# def add(a, b):
#     return a + b
# 
# def multiply(a, b):
#     return a * b
# 
# PI = 3.14159
# 
# if __name__ == "__main__":
#     # 直接运行这个文件时执行的测试代码
#     print(add(1, 2))
#     print(multiply(3, 4))

# 在另一个文件中导入：
# import my_utils
# print(my_utils.add(1, 2))  # 3
# print(my_utils.PI)  # 3.14159

# from my_utils import add, multiply
# print(add(1, 2))

# ============================================================
# 例3：if __name__ == "__main__" 的作用
# ============================================================
# 每个 Python 文件都有一个内置变量 __name__
# - 直接运行这个文件时：__name__ == "__main__"
# - 被其他文件 import 时：__name__ == 模块名（如 "my_utils"）

# 所以 if __name__ == "__main__": 块里的代码：
# - 直接运行时执行（可以用来测试）
# - 被导入时不执行（不会污染导入者的命名空间）

# 这是 Python 模块的标准写法，每个可执行脚本都应该有

# ============================================================
# 例4：包（Package）—— 包含多个模块的目录
# ============================================================
# 目录结构：
# my_package/
# ├── __init__.py       # 包的初始化文件（必须有，Python 3.3+ 可以没有但推荐有）
# ├── module_a.py       # 模块A
# ├── module_b.py       # 模块B
# └── sub_package/      # 子包
#     ├── __init__.py
#     └── module_c.py

# 导入方式：
# import my_package.module_a
# from my_package import module_a
# from my_package.module_a import some_function
# from my_package.sub_package import module_c

# ============================================================
# 例5：__init__.py 的作用
# ============================================================
# __init__.py 在包被导入时自动执行，可以用来：
# 1. 定义包级别的变量和函数
# 2. 控制 from package import * 导入哪些内容（__all__）
# 3. 预导入常用模块，简化用户导入

# 示例 __init__.py：
# __all__ = ["module_a", "module_b", "helper"]  # 控制 import * 的范围
# 
# from .module_a import important_function  # 预导入，用户可以直接 from package import important_function
# 
# VERSION = "1.0.0"  # 包级变量

# ============================================================
# 例6：相对导入（包内部模块之间互相导入）
# ============================================================
# 在 my_package/module_a.py 中：
# from . import module_b  # 导入同目录下的 module_b
# from .module_b import some_func  # 从同目录 module_b 导入函数
# from ..sub_package import module_c  # 导入上级目录的子包
# from ..sub_package.module_c import func  # 从子包导入函数

# 注意：相对导入只能在包内部使用，直接运行包含相对导入的文件会报错
# 正确做法：用 python -m my_package.module_a 运行（从包的上级目录执行）

# ============================================================
# 例7：常用标准库速查
# ============================================================
# 数据处理：
#   math        数学函数（sqrt, sin, cos, pi, e）
#   random      随机数（randint, choice, shuffle, sample）
#   statistics  统计（mean, median, stdev, variance）
#   decimal     高精度十进制计算
#   fractions   分数运算
#   itertools   迭代器工具（chain, combinations, permutations）
#   collections 高级容器（Counter, defaultdict, OrderedDict, deque）
#   functools   函数工具（reduce, partial, lru_cache, wraps）

# 文件与系统：
#   os          操作系统接口（路径、目录、环境变量）
#   sys         系统相关（argv, path, exit, stdin/stdout）
#   pathlib     面向对象路径操作
#   shutil      高级文件操作（复制、移动、删除目录）
#   glob        文件通配符匹配
#   tempfile    临时文件/目录
#   json        JSON 读写
#   csv         CSV 读写
#   pickle      Python 对象序列化
#   configparser 配置文件解析

# 时间与日期：
#   datetime    日期时间（date, time, datetime, timedelta）
#   time        时间相关（sleep, time, strftime）
#   calendar    日历相关

# 网络与并发：
#   urllib      URL 处理和 HTTP 请求
#   http        HTTP 协议
#   socket      网络编程
#   threading   多线程
#   multiprocessing 多进程
#   asyncio     异步编程
#   concurrent.futures 线程池/进程池

# 其他：
#   re          正则表达式
#   logging     日志
#   unittest    单元测试
#   doctest     文档测试
#   argparse    命令行参数解析
#   subprocess  子进程管理
#   email       邮件处理
#   hashlib     哈希算法（md5, sha1, sha256）
#   base64      Base64 编解码
#   zlib        压缩
#   copy        深拷贝/浅拷贝
#   typing      类型提示

# ============================================================
# 例8：第三方库安装（pip）
# ============================================================
# pip install package_name       # 安装
# pip install package_name==1.0  # 安装指定版本
# pip install --upgrade package_name  # 升级
# pip uninstall package_name     # 卸载
# pip list                       # 列出已安装的包
# pip freeze > requirements.txt  # 导出依赖列表
# pip install -r requirements.txt  # 从依赖列表安装

# 常用第三方库：
# 数据分析：numpy, pandas, scipy
# 可视化：matplotlib, seaborn, plotly
# 机器学习：scikit-learn, xgboost, lightgbm, tensorflow, pytorch
# 网络请求：requests, httpx
# 网页解析：beautifulsoup4, lxml
# Excel：openpyxl, xlrd, xlsxwriter
# 数据库：sqlalchemy, pymysql, psycopg2
# Web框架：flask, django, fastapi
# 命令行：click, typer
# 日期：python-dateutil, arrow
# 进度条：tqdm
# 配置：pydantic, python-dotenv

# ============================================================
# 例9：模块搜索路径（sys.path）
# ============================================================
import sys
print(sys.path)  # Python 搜索模块的路径列表
# 通常包含：
# 1. 当前脚本所在目录
# 2. PYTHONPATH 环境变量指定的目录
# 3. 标准库目录
# 4. site-packages（第三方库安装目录）

# 如果模块找不到，可以：
# 1. 把模块所在目录添加到 sys.path
# sys.path.append("/path/to/your/modules")
# 2. 设置 PYTHONPATH 环境变量
# 3. 把模块安装到 site-packages（pip install -e .）
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| from module import * | 命名冲突，不知道名称来源 | 显式导入需要的名称，或导入模块本身 |
| 文件名和标准库重名（如 json.py） | import json 导入了自己的文件 | 不要用标准库名作为文件名 |
| 循环导入（A import B，B import A） | ImportError | 重构代码，把共用部分抽到第三个模块 |
| 相对导入直接运行文件 | ValueError: attempted relative import | 用 python -m package.module 运行，或改为绝对导入 |
| 忘记 __init__.py | 目录不被识别为包（旧版Python） | 包目录下添加 __init__.py（可以为空） |
| 修改模块后不生效 | Python 缓存了旧版本 | 重新启动解释器，或用 importlib.reload() |
| pip 安装了但 import 失败 | 安装到了其他 Python 环境 | 确认 pip 和 python 是同一个环境（which python/pip） |

### 动手

1. 创建一个自定义模块 string_utils.py，包含字符串反转、统计词频、判断回文三个函数，并用 if __name__ == "__main__" 测试
2. 创建一个包 my_package，包含两个模块，在 __init__.py 中预导入常用函数
3. 用 pip 安装 requests 库，写一个简单的 GET 请求示例
4. 查看 sys.path，理解 Python 模块搜索顺序，尝试把自定义目录加入搜索路径
'''

# ========== 4. 迭代器与生成器 ==========
iterator_content = '''### 课前

- **场景**：要处理大数据集（内存装不下）、惰性计算（用的时候才算）、自定义可迭代对象、简化迭代逻辑。
- **目标**：掌握迭代器协议、生成器函数(yield)、生成器表达式、itertools 常用工具。
- **先修**：Python 基础语法、循环、函数

### 是什么

- **一句话定义**：迭代器是实现了 __iter__ 和 __next__ 方法的对象，可以逐个返回元素；生成器是用 yield 关键字定义的特殊迭代器，能惰性生成值，是处理大数据和简化迭代的强大工具。
- **核心优势**：惰性计算（不一次性生成所有值，节省内存）、状态保持（每次调用从上次位置继续）、代码简洁。

### 怎么写

```python
# ============================================================
# 例1：可迭代对象 vs 迭代器
# ============================================================
# 可迭代对象（Iterable）：可以被 for 循环遍历的对象
# 实现了 __iter__ 方法，返回一个迭代器
# 例如：list, tuple, str, dict, set, range, file

my_list = [1, 2, 3]
for item in my_list:  # for 循环自动调用 iter() 获取迭代器
    print(item)

# 手动使用迭代器：
it = iter(my_list)  # 调用 __iter__，返回迭代器
print(next(it))  # 1，调用 __next__
print(next(it))  # 2
print(next(it))  # 3
# print(next(it))  # StopIteration（迭代结束，抛出异常）

# ============================================================
# 例2：自定义迭代器（实现 __iter__ 和 __next__）
# ============================================================
class Countdown:
    """从 n 倒数到 1 的迭代器"""
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self  # 返回自身作为迭代器
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration  # 迭代结束
        value = self.current
        self.current -= 1
        return value

# 使用
for i in Countdown(5):
    print(i)  # 5, 4, 3, 2, 1

# 手动：
cd = Countdown(3)
print(next(cd))  # 3
print(next(cd))  # 2
print(next(cd))  # 1
# print(next(cd))  # StopIteration

# ============================================================
# 例3：生成器函数（yield）—— 最简单的迭代器
# ============================================================
def countdown_gen(start):
    """用 yield 实现的倒数生成器"""
    current = start
    while current > 0:
        yield current  # 暂停执行，返回值；下次调用从这里继续
        current -= 1

# 使用（和迭代器一样）
for i in countdown_gen(5):
    print(i)  # 5, 4, 3, 2, 1

# 生成器的执行过程：
gen = countdown_gen(3)
print(next(gen))  # 3（执行到 yield 3，暂停）
print(next(gen))  # 2（从 yield 后继续，current=2，yield 2，暂停）
print(next(gen))  # 1
# print(next(gen))  # StopIteration（函数执行完毕）

# ============================================================
# 例4：生成器 vs 普通函数的区别
# ============================================================
# 普通函数：调用后执行完毕，返回一个值
def normal_func():
    return 1
    return 2  # 永远不会执行

# 生成器函数：调用后返回生成器对象，每次 next() 执行到下一个 yield
def generator_func():
    yield 1
    yield 2  # 第二次 next() 执行到这里
    yield 3

gen = generator_func()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3

# 生成器可以有无限多个值（普通函数做不到）
def infinite_counter():
    n = 0
    while True:
        yield n
        n += 1

# counter = infinite_counter()
# print(next(counter))  # 0
# print(next(counter))  # 1
# ... 永远不会结束，按需取值

# ============================================================
# 例5：生成器的内存优势（处理大数据）
# ============================================================
# 普通方式：生成所有数据到列表，占用大量内存
def read_all_lines(filepath):
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip())
    return lines  # 大文件可能内存溢出

# 生成器方式：逐行生成，内存友好
def read_lines_gen(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()  # 每次只生成一行

# 使用时内存占用极小：
# for line in read_lines_gen("huge_file.txt"):
#     process(line)

# 另一个例子：斐波那契数列
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# fib = fibonacci()
# for _ in range(10):
#     print(next(fib))  # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

# ============================================================
# 例6：生成器表达式（类似列表推导式，但用圆括号）
# ============================================================
# 列表推导式：一次性生成所有元素，占用内存
squares_list = [x**2 for x in range(1000000)]  # 100万个数字，占用内存

# 生成器表达式：惰性生成，几乎不占内存
squares_gen = (x**2 for x in range(1000000))  # 生成器对象，不立即计算

# 使用时才计算：
for square in squares_gen:
    if square > 100:
        break
    print(square)

# 生成器表达式可以直接作为函数参数（不需要额外括号）
sum(x**2 for x in range(100))  # 平方和
max(x**2 for x in range(100))  # 最大值

# ============================================================
# 例7：yield from（委托生成器，Python 3.3+）
# ============================================================
def nested_gen():
    """嵌套生成器"""
    yield from [1, 2, 3]  # 等价于 for x in [1,2,3]: yield x
    yield from (x**2 for x in range(3))  # 可以委托另一个生成器
    yield from "ab"  # 字符串也是可迭代的

for item in nested_gen():
    print(item)  # 1, 2, 3, 0, 1, 4, 'a', 'b'

# yield from 的主要用途：递归生成器、协程（高级用法）

# ============================================================
# 例8：itertools 常用工具（标准库，迭代器工具集）
# ============================================================
import itertools

# count：无限计数
for i in itertools.count(10, 2):  # 从10开始，步长2
    if i > 20:
        break
    print(i)  # 10, 12, 14, 16, 18, 20

# cycle：无限循环
# for item in itertools.cycle(["A", "B", "C"]):
#     print(item)  # A, B, C, A, B, C, ... 无限

# repeat：重复 n 次
for item in itertools.repeat("hello", 3):
    print(item)  # hello, hello, hello

# chain：连接多个可迭代对象
for item in itertools.chain([1, 2], ["a", "b"], (3, 4)):
    print(item)  # 1, 2, a, b, 3, 4

# combinations：组合（不考虑顺序，不重复）
for combo in itertools.combinations([1, 2, 3], 2):
    print(combo)  # (1,2), (1,3), (2,3)

# permutations：排列（考虑顺序）
for perm in itertools.permutations([1, 2, 3], 2):
    print(perm)  # (1,2), (1,3), (2,1), (2,3), (3,1), (3,2)

# product：笛卡尔积
for p in itertools.product([1, 2], ["a", "b"]):
    print(p)  # (1,a), (1,b), (2,a), (2,b)

# islice：切片迭代器（类似 list 切片，但不复制）
gen = (x for x in range(100))
for item in itertools.islice(gen, 5, 10):  # 取第5到第10个
    print(item)  # 5, 6, 7, 8, 9

# groupby：分组（需要先排序）
data = [("A", 1), ("A", 2), ("B", 3), ("B", 4)]
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")  # A: [('A',1),('A',2)], B: [('B',3),('B',4)]

# ============================================================
# 例9：生成器的 send/throw/close（高级，协程基础）
# ============================================================
def echo_gen():
    """可以接收外部值的生成器"""
    while True:
        received = yield  # 暂停，等待外部 send 值
        print(f"收到: {received}")

gen = echo_gen()
next(gen)  # 启动生成器，执行到第一个 yield
gen.send("hello")  # 收到: hello
gen.send("world")  # 收到: world
gen.close()  # 关闭生成器

# 这是协程（coroutine）的基础，asyncio 就是基于这个机制
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 生成器只能迭代一次 | 第二次 for 循环没有输出 | 生成器是一次性的，需要重新创建生成器对象 |
| 对生成器用 len()/索引 | TypeError: object of type 'generator' has no len() | 生成器不支持 len 和索引，需要时转 list（但会消耗内存） |
| 生成器表达式用方括号 | 变成列表推导式，占用内存 | 生成器表达式用圆括号 ()，列表用方括号 [] |
| 忘记 next() 启动带 send 的生成器 | TypeError: can't send non-None value | 第一次必须用 next(gen) 或 gen.send(None) 启动 |
| 自定义迭代器 __iter__ 返回非迭代器 | TypeError: iter() returned non-iterator | __iter__ 必须返回实现了 __next__ 的对象（通常返回 self） |
| 生成器中 return 有值 | 值被忽略（Python 3.3+ 可以通过 StopIteration.value 获取） | 生成器用 yield 返回值，return 只用于结束生成器 |
| itertools.groupby 不排序 | 分组结果不对 | groupby 只合并连续的相同键，使用前必须先排序 |

### 动手

1. 写一个生成器函数，生成斐波那契数列的前 n 项
2. 用生成器表达式计算 1 到 100 万的平方和（注意内存占用）
3. 自定义一个迭代器类，实现 range(start, stop, step) 的功能
4. 用 itertools.combinations 找出列表中所有两两组合
5. （进阶）写一个可以接收外部值的生成器，实现简单的累加器
'''

# ========== 5. 装饰器 ==========
decorator_content = '''### 课前

- **场景**：要给多个函数添加相同的功能（计时、日志、权限检查、缓存），不想重复代码。
- **目标**：掌握装饰器语法、带参数的装饰器、多个装饰器叠加、functools.wraps、常用内置装饰器。
- **先修**：Python 函数（一等公民）、闭包、*args/**kwargs

### 是什么

- **一句话定义**：装饰器是接收一个函数作为参数、返回一个新函数的函数，在不修改原函数代码的情况下增强其功能，是 Python 中"开放封闭原则"的典型实现，代码复用的利器。
- **核心理念**：函数是一等公民（可以作为参数传递、作为返回值、赋值给变量），装饰器利用这一点实现"包装"。

### 怎么写

```python
# ============================================================
# 例1：函数是一等公民（装饰器的基础）
# ============================================================
# 函数可以赋值给变量
def greet(name):
    return f"Hello, {name}!"

say_hello = greet  # 不调用，只是引用
print(say_hello("Alice"))  # Hello, Alice!

# 函数可以作为参数传递
def call_func(func, arg):
    return func(arg)

print(call_func(greet, "Bob"))  # Hello, Bob!

# 函数可以作为返回值
def get_greeter(language):
    if language == "en":
        def greet_en(name):
            return f"Hello, {name}!"
        return greet_en
    elif language == "zh":
        def greet_zh(name):
            return f"你好，{name}！"
        return greet_zh

greeter = get_greeter("zh")
print(greeter("张三"))  # 你好，张三！

# ============================================================
# 例2：闭包（Closure）—— 装饰器的核心机制
# ============================================================
def outer(x):
    def inner(y):
        return x + y  # inner 引用了 outer 的变量 x
    return inner

add5 = outer(5)  # x=5 被"记住"了
print(add5(3))   # 8（5+3）
print(add5(10))  # 15（5+10）

# 闭包的特点：内部函数记住了外部函数的变量环境，即使外部函数已经执行完毕

# ============================================================
# 例3：最简单的装饰器
# ============================================================
def my_decorator(func):
    def wrapper():
        print("函数执行前")
        func()  # 调用原函数
        print("函数执行后")
    return wrapper

@my_decorator  # 语法糖，等价于 say_hello = my_decorator(say_hello)
def say_hello():
    print("Hello!")

say_hello()
# 输出：
# 函数执行前
# Hello!
# 函数执行后

# 等价写法（不用 @ 语法糖）：
# def say_hello():
#     print("Hello!")
# say_hello = my_decorator(say_hello)

# ============================================================
# 例4：装饰带参数的函数（用 *args, **kwargs 通用接收）
# ============================================================
def log_decorator(func):
    def wrapper(*args, **kwargs):  # 通用参数接收
        print(f"调用函数: {func.__name__}, 参数: {args}, {kwargs}")
        result = func(*args, **kwargs)  # 传递参数给原函数
        print(f"函数返回: {result}")
        return result  # 返回原函数的返回值
    return wrapper

@log_decorator
def add(a, b):
    return a + b

@log_decorator
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(add(3, 5))
# 调用函数: add, 参数: (3, 5), {}
# 函数返回: 8
# 8

print(greet("Alice", greeting="Hi"))
# 调用函数: greet, 参数: ('Alice',), {'greeting': 'Hi'}
# 函数返回: Hi, Alice!
# Hi, Alice!

# ============================================================
# 例5：functools.wraps —— 保留原函数元信息
# ============================================================
import functools

def decorator_without_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def decorator_with_wraps(func):
    @functools.wraps(func)  # 把原函数的元信息复制到 wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator_without_wraps
def func1():
    """这是 func1 的文档字符串"""
    pass

@decorator_with_wraps
def func2():
    """这是 func2 的文档字符串"""
    pass

print(func1.__name__)  # wrapper（丢失了原函数名！）
print(func1.__doc__)   # None（丢失了文档字符串！）

print(func2.__name__)  # func2（保留了原函数名）
print(func2.__doc__)   # 这是 func2 的文档字符串（保留了文档）

# 最佳实践：所有装饰器都应该用 @functools.wraps(func)

# ============================================================
# 例6：带参数的装饰器（三层嵌套）
# ============================================================
def repeat(times):  # 第一层：接收装饰器参数
    def decorator(func):  # 第二层：接收函数
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # 第三层：实际包装
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)  # 带参数的装饰器
def say_hi(name):
    print(f"Hi, {name}!")

say_hi("Alice")
# Hi, Alice!
# Hi, Alice!
# Hi, Alice!

# 等价于：say_hi = repeat(3)(say_hi)

# ============================================================
# 例7：多个装饰器叠加（执行顺序）
# ============================================================
def decorator_a(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("A 之前")
        result = func(*args, **kwargs)
        print("A 之后")
        return result
    return wrapper

def decorator_b(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("B 之前")
        result = func(*args, **kwargs)
        print("B 之后")
        return result
    return wrapper

@decorator_a
@decorator_b
def my_func():
    print("原函数")

my_func()
# 输出顺序：
# A 之前
# B 之前
# 原函数
# B 之后
# A 之后

# 执行顺序：装饰器从下往上应用（先 B 后 A），执行时从上往下（先 A 后 B）
# 等价于：my_func = decorator_a(decorator_b(my_func))

# ============================================================
# 例8：常用装饰器示例 —— 计时装饰器
# ============================================================
import time

def timer(func):
    """统计函数执行时间的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.4f}秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    print("完成")

slow_function()
# 完成
# slow_function 执行时间: 1.0012秒

# ============================================================
# 例9：常用装饰器示例 —— 缓存装饰器
# ============================================================
def memoize(func):
    """缓存函数结果的装饰器（适合纯函数，相同输入返回相同输出）"""
    cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fibonacci(n):
    """计算斐波那契数列第 n 项（递归，无缓存会非常慢）"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # 有缓存，瞬间完成
# 无缓存的话，fibonacci(100) 可能需要几百年...

# Python 内置了更强大的缓存装饰器：
@functools.lru_cache(maxsize=128)  # LRU 缓存，最多保留128个
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# ============================================================
# 例10：常用装饰器示例 —— 重试装饰器
# ============================================================
def retry(max_attempts=3, delay=1):
    """失败自动重试的装饰器（网络请求常用）"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise  # 最后一次失败，抛出异常
                    print(f"第 {attempt} 次失败: {e}，{delay}秒后重试...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def unstable_api_call():
    """模拟不稳定的 API 调用"""
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络超时")
    return "成功"

# ============================================================
# 例11：内置装饰器 —— @property, @staticmethod, @classmethod
# ============================================================
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property  # 把方法变成属性，可以像属性一样访问
    def radius(self):
        return self._radius
    
    @radius.setter  # 属性的 setter，允许赋值时验证
    def radius(self, value):
        if value <= 0:
            raise ValueError("半径必须大于0")
        self._radius = value
    
    @property
    def area(self):  # 只读属性（没有 setter）
        return 3.14159 * self._radius ** 2
    
    @staticmethod  # 静态方法，不需要 self，不访问实例
    def is_valid_radius(radius):
        return radius > 0
    
    @classmethod  # 类方法，第一个参数是 cls（类本身）
    def from_diameter(cls, diameter):
        return cls(diameter / 2)  # 调用类创建实例

c = Circle(5)
print(c.radius)  # 5（像属性一样访问，不需要括号）
print(c.area)    # 78.53975
c.radius = 10    # 调用 setter
print(Circle.is_valid_radius(5))  # True（静态方法）
c2 = Circle.from_diameter(20)     # 类方法创建实例
print(c2.radius)  # 10.0

# ============================================================
# 例12：装饰器的实际应用场景
# ============================================================
# 1. 日志记录：记录函数调用、参数、返回值
# 2. 性能计时：统计函数执行时间
# 3. 缓存：memoize / lru_cache
# 4. 权限验证：检查用户是否有权限调用
# 5. 输入验证：验证参数合法性
# 6. 重试机制：网络请求失败自动重试
# 7. 事务管理：数据库事务自动提交/回滚
# 8. 路由注册：Web 框架中的 @app.route
# 9. 序列化：自动将返回值转为 JSON
# 10. 限流：限制函数调用频率
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 忘记 functools.wraps | 函数名变成 wrapper，文档丢失 | 所有装饰器都加 @functools.wraps(func) |
| 装饰器不返回值 | 原函数返回值丢失 | wrapper 必须 return func(*args, **kwargs) 的结果 |
| 带参数的装饰器少一层嵌套 | TypeError: ... takes 0 positional arguments | 带参数的装饰器必须三层嵌套（参数→函数→包装） |
| 装饰器执行顺序搞反 | 输出顺序不符合预期 | 装饰器从下往上应用，执行时从上往下 |
| 缓存装饰器用于非纯函数 | 返回错误的缓存结果 | 只有相同输入返回相同输出的纯函数才能用缓存 |
| @property 方法加括号 | TypeError: 'int' object is not callable | property 像属性一样访问，不加括号 |
| 装饰器修改了原函数 | 副作用，难以调试 | 装饰器应该只增强，不修改原函数的行为 |

### 动手

1. 写一个计时装饰器，统计函数执行时间，并用 functools.wraps 保留元信息
2. 写一个带参数的装饰器 @log(level="INFO")，可以指定日志级别
3. 写一个缓存装饰器，用于斐波那契数列计算，对比有缓存和无缓存的性能差异
4. 写一个权限检查装饰器 @requires_role("admin")，模拟用户角色验证
5. 用 @property 实现一个 Temperature 类，支持摄氏度和华氏度的相互转换
'''

# ========== 6. 上下文管理器 ==========
context_content = '''### 课前

- **场景**：要确保资源（文件、数据库连接、锁）在使用后正确释放，不管是否发生异常。
- **目标**：掌握 with 语句、上下文管理器协议（__enter__/__exit__）、contextlib 工具、自定义上下文管理器。
- **先修**：Python 基础语法、异常处理（try/finally）、装饰器

### 是什么

- **一句话定义**：上下文管理器是实现了 __enter__ 和 __exit__ 方法的对象，配合 with 语句使用，确保资源在进入时获取、退出时自动释放（即使发生异常），是 Python 资源管理的标准方式。
- **核心理念**：Don't Repeat Yourself —— 把"获取资源→使用→释放资源"的模式抽象出来，避免到处写 try/finally。

### 怎么写

```python
# ============================================================
# 例1：with 语句的基本用法（文件操作）
# ============================================================
# 传统方式（try/finally）：
f = open("data.txt", "r", encoding="utf-8")
try:
    content = f.read()
    print(content)
finally:
    f.close()  # 无论是否异常，都关闭文件

# with 方式（推荐，更简洁）：
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
# with 块结束后，文件自动关闭（即使发生异常）

# ============================================================
# 例2：上下文管理器协议（__enter__ / __exit__）
# ============================================================
class MyContext:
    def __enter__(self):
        """进入 with 块时调用，返回值赋给 as 后的变量"""
        print("进入上下文")
        return "上下文资源"  # 这个值会赋给 as 后的变量
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 块时调用，无论是否异常都会执行
        exc_type: 异常类型（无异常则为 None）
        exc_val: 异常值（无异常则为 None）
        exc_tb: 异常追踪栈（无异常则为 None）
        返回 True 表示抑制异常，返回 False/None 表示传播异常
        """
        print("退出上下文")
        if exc_type:
            print(f"发生异常: {exc_type.__name__}: {exc_val}")
        return False  # 不抑制异常，让异常继续传播

# 使用：
with MyContext() as resource:
    print(f"使用资源: {resource}")
    # 输出：
    # 进入上下文
    # 使用资源: 上下文资源
    # 退出上下文

# 发生异常时：
with MyContext():
    print("执行中...")
    raise ValueError("测试异常")
    print("这行不会执行")
# 输出：
# 进入上下文
# 执行中...
# 退出上下文
# 发生异常: ValueError: 测试异常
# 然后异常继续抛出（因为 __exit__ 返回 False）

# ============================================================
# 例3：__exit__ 抑制异常（返回 True）
# ============================================================
class SuppressError:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ValueError:
            print(f"抑制了 ValueError: {exc_val}")
            return True  # 返回 True，异常被抑制，不会继续抛出
        return False  # 其他异常正常传播

with SuppressError():
    raise ValueError("这个异常会被抑制")
print("程序继续执行")  # 这行会执行，因为异常被抑制了

# with SuppressError():
#     raise TypeError("这个异常不会被抑制")  # 会正常抛出

# ============================================================
# 例4：自定义上下文管理器 —— 数据库连接
# ============================================================
class DatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None
    
    def __enter__(self):
        print(f"连接数据库: {self.db_url}")
        # self.conn = create_connection(self.db_url)  # 实际连接
        self.conn = f"连接对象({self.db_url})"
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("关闭数据库连接")
        # if self.conn:
        #     self.conn.close()
        self.conn = None
        return False

with DatabaseConnection("mysql://localhost/mydb") as conn:
    print(f"执行查询: {conn}")
    # 模拟查询
# 输出：
# 连接数据库: mysql://localhost/mydb
# 执行查询: 连接对象(mysql://localhost/mydb)
# 关闭数据库连接

# ============================================================
# 例5：自定义上下文管理器 —— 计时器
# ============================================================
import time

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self  # 返回自身，可以访问 elapsed 属性
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.elapsed = self.end - self.start
        print(f"执行时间: {self.elapsed:.4f}秒")
        return False

with Timer() as t:
    time.sleep(1)
    # 可以在 with 块内访问 t.start
print(f"块结束后也能访问: {t.elapsed:.4f}秒")

# ============================================================
# 例6：contextlib.contextmanager —— 用生成器写上下文管理器（更简洁）
# ============================================================
from contextlib import contextmanager

@contextmanager
def my_context():
    # __enter__ 部分：yield 之前的代码
    print("进入上下文")
    resource = "资源对象"
    try:
        yield resource  # yield 的值赋给 as 后的变量
        # __exit__ 部分（正常退出）：yield 之后的代码
        print("正常退出上下文")
    except Exception as e:
        # __exit__ 部分（异常退出）
        print(f"异常退出: {e}")
        # 不重新抛出 = 抑制异常
        # raise = 传播异常
        raise  # 重新抛出异常
    finally:
        # 无论是否异常都执行（清理资源）
        print("清理资源")

with my_context() as res:
    print(f"使用: {res}")
# 输出：
# 进入上下文
# 使用: 资源对象
# 正常退出上下文
# 清理资源

# ============================================================
# 例7：contextmanager 实际例子 —— 临时修改工作目录
# ============================================================
import os

@contextmanager
def change_dir(path):
    """临时切换工作目录，退出后自动恢复"""
    original_dir = os.getcwd()
    os.chdir(path)
    try:
        yield  # 不需要返回值
    finally:
        os.chdir(original_dir)  # 恢复原目录

print(f"当前目录: {os.getcwd()}")
with change_dir("/tmp"):
    print(f"临时目录: {os.getcwd()}")
print(f"恢复后: {os.getcwd()}")

# ============================================================
# 例8：contextmanager 实际例子 —— 事务管理
# ============================================================
@contextmanager
def transaction(db):
    """数据库事务上下文管理器，成功自动提交，失败自动回滚"""
    print("开始事务")
    try:
        yield db  # 返回数据库连接
        print("提交事务")
        # db.commit()
    except Exception as e:
        print(f"回滚事务: {e}")
        # db.rollback()
        raise  # 重新抛出异常

# 使用：
# with transaction(db) as conn:
#     conn.execute("INSERT ...")
#     conn.execute("UPDATE ...")
#     # 如果中途异常，自动回滚；全部成功，自动提交

# ============================================================
# 例9：contextlib 其他工具
# ============================================================
from contextlib import suppress, closing, redirect_stdout
import io

# suppress：抑制指定异常（上下文管理器版本的 try/except: pass）
with suppress(FileNotFoundError):
    os.remove("不存在的文件.txt")  # 不会报错
print("继续执行")

# closing：把有 close() 方法但没有实现上下文管理器的对象包装成上下文管理器
# from urllib.request import urlopen
# with closing(urlopen("https://example.com")) as response:
#     html = response.read()
# # 自动调用 response.close()

# redirect_stdout：重定向标准输出
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("这些输出会被捕获")
    print("不会显示在屏幕上")
print(f"捕获的内容: {buffer.getvalue()}")

# ============================================================
# 例10：多个上下文管理器同时使用
# ============================================================
# 方式1：嵌套 with（不推荐，缩进太深）
# with open("file1.txt") as f1:
#     with open("file2.txt") as f2:
#         with open("file3.txt") as f3:
#             ...

# 方式2：一个 with 语句多个上下文（Python 3.10+ 推荐，用括号）
# with (
#     open("file1.txt") as f1,
#     open("file2.txt") as f2,
#     open("file3.txt") as f3,
# ):
#     ...

# 方式3：contextlib.ExitStack（动态数量的上下文管理器）
from contextlib import ExitStack

filenames = ["file1.txt", "file2.txt", "file3.txt"]
with ExitStack() as stack:
    files = [stack.enter_context(open(fname)) for fname in filenames]
    # 所有文件都会在退出时自动关闭
    # for f in files:
    #     print(f.read())

# ============================================================
# 例11：上下文管理器的实际应用场景
# ============================================================
# 1. 文件操作：open() 内置支持
# 2. 数据库连接/事务：连接自动关闭，事务自动提交/回滚
# 3. 锁：threading.Lock() 支持 with，自动获取和释放
# 4. 网络连接：socket、HTTP 连接
# 5. 临时文件：tempfile 支持 with，自动删除
# 6. 临时修改环境：切换目录、修改环境变量、重定向输出
# 7. 性能计时：统计代码块执行时间
# 8. 资源池：从连接池获取连接，用完自动归还
# 9. 测试：临时修改配置，测试后自动恢复
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| __exit__ 忘记返回值 | 默认返回 None（False），异常正常传播 | 需要抑制异常时显式 return True |
| contextmanager 没有 try/finally | 异常时资源不释放 | yield 必须放在 try 块中，finally 做清理 |
| contextmanager 中 yield 后有代码但异常时不执行 | 资源泄漏 | 清理代码放 finally 块，不要放 yield 后 |
| with 块内修改 as 变量指向新对象 | 原资源不被释放 | as 变量不要重新赋值，需要时用不同变量名 |
| 自定义 __enter__ 不返回值 | as 变量为 None | __enter__ 必须 return 资源对象 |
| 用 with 处理不支持的对象 | AttributeError: __enter__ | 确认对象实现了上下文管理器协议，或用 closing() 包装 |
| 多个 with 嵌套太深 | 代码可读性差 | 用一个 with 多个上下文（Python 3.10+）或 ExitStack |

### 动手

1. 用类实现一个上下文管理器，统计代码块执行时间，支持在块内和块后访问耗时
2. 用 @contextmanager 实现一个临时修改环境变量的上下文管理器，退出后自动恢复
3. 实现一个数据库事务上下文管理器，成功自动提交，失败自动回滚
4. 用 contextlib.suppress 重写一段 try/except: pass 的代码
5. （进阶）用 ExitStack 同时管理动态数量的文件，全部读取后自动关闭
'''

# ========== 组装新节点 ==========
# 文件与异常子章节
file_exception_chapter = make_chapter(
    "python-base-file-exception",
    "文件与异常",
    [
        make_leaf("python-base-file-io", "文件操作与路径", file_content),
        make_leaf("python-base-exception", "异常处理", exception_content),
    ],
    "| 叶课 | 内容 |\n|---|---|\n| 文件操作与路径 | open读写、os/pathlib、CSV/JSON |\n| 异常处理 | try/except/finally、自定义异常、最佳实践 |"
)

# 模块与包（独立叶子）
module_leaf = make_leaf("python-base-modules", "模块与包", module_content)

# 进阶特性子章节
advanced_chapter = make_chapter(
    "python-base-advanced",
    "进阶特性",
    [
        make_leaf("python-base-iterator", "迭代器与生成器", iterator_content),
        make_leaf("python-base-decorator", "装饰器", decorator_content),
        make_leaf("python-base-context", "上下文管理器", context_content),
    ],
    "| 叶课 | 内容 |\n|---|---|\n| 迭代器与生成器 | 迭代器协议、yield、生成器表达式、itertools |\n| 装饰器 | 装饰器语法、带参数装饰器、functools.wraps、内置装饰器 |\n| 上下文管理器 | with语句、__enter__/__exit__、contextmanager、资源管理 |"
)

# 找到Python基础章节并添加新节点
def find_node_by_title(node, title):
    if node.get("title") == title:
        return node
    for child in node.get("children", []):
        result = find_node_by_title(child, title)
        if result:
            return result
    return None

python_base = find_node_by_title(data, "Python 基础")
print(f"Python基础章节原有 {len(python_base['children'])} 子节点")

# 添加新节点（在面向对象和正则表达式之前）
new_children = []
for child in python_base["children"]:
    if child["title"] == "面向对象":
        new_children.append(file_exception_chapter)
        new_children.append(module_leaf)
        new_children.append(advanced_chapter)
    new_children.append(child)

python_base["children"] = new_children
print(f"Python基础章节现有 {len(python_base['children'])} 子节点")

# 保存
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["python"]={new_json_str}\n'

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-python.js size: {len(new_content)} bytes")
print("Python基础核心特性补充完成！新增6篇：")
print("  1. 文件操作与路径")
print("  2. 异常处理")
print("  3. 模块与包")
print("  4. 迭代器与生成器")
print("  5. 装饰器")
print("  6. 上下文管理器")
