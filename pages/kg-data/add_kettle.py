#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Kettle/PDI 节点并插入到 embed-etl.js"""

import json
import re

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

def make_chapter(node_id, title, level, leaves):
    leaf_titles = "、".join([l["title"] for l in leaves])
    leaf_count = len(leaves)
    
    leaf_table_rows = []
    for i, l in enumerate(leaves, 1):
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
- **学习目标**：学完本章叶课，能独立完成 Kettle 转换/作业设计，并讲清适用边界。
- **先修**：ETL 基础概念；Kettle 核心组件与安装。

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
| 主路径 | 每叶示例可在 Spoon 中跑通 |
| 易错 | 能举本章至少 2 个反例 |
| 口述 | 不看笔记讲清「{title}」解决什么问题 |

### 下一动

点开地图中的第 1 片绿色叶节点。本章合计约 **{leaf_count}** 片叶讲义。
"""
    return {"id": node_id, "title": title, "level": level, "content": content, "lessonParent": True, "children": leaves}

# ========== 叶子节点内容 ==========

leaf_install = make_leaf("etl-kettle-install", "核心组件与安装", "?", """### 课前

- **场景**：团队要选型一款可视化 ETL 工具，听说 Kettle 开源免费，想先搭起来试试。
- **目标**：掌握 Kettle 四大核心组件、下载安装、JDK 配置、数据库驱动、Spoon 启动。
- **先修**：ETL 基础概念

### 是什么

- **一句话定义**：Kettle（Pentaho Data Integration，PDI）是开源可视化 ETL 工具，纯 Java 编写，跨平台运行，通过拖拽设计数据流程。
- **四大核心组件**：
  - **Spoon**：图形化设计工具（GUI），用来设计和编辑转换（.ktr）和作业（.kjb）
  - **Pan**：命令行工具，用于执行转换（.ktr）
  - **Kitchen**：命令行工具，用于执行作业（.kjb）
  - **Carte**：轻量级 Web 服务器，用于建立远程 ETL Server，支持集群执行
- **两大文件类型**：.ktr（转换 Transformation，数据流）、.kjb（作业 Job，工作流控制）

### 怎么写

```text
# 1. 下载
# 官方地址：https://www.hitachivantara.com/en-us/products/pentaho-platform/
#   data-integration-analytics/pentaho-community-edition.html
# 下载 pdi-ce-9.x.x-x.zip（社区版，免费）

# 2. 解压（无需安装）
# 解压到任意目录，如 D:\data-integration\

# 3. 配置 JDK
# Kettle 9.x 要求 JDK 11+，Kettle 8.x/9.1 支持 JDK 8
# 编辑 data-integration\set-pentaho-env.bat：
#   PENTAHO_JAVA_HOME = JDK 安装根目录
#   JAVA_HOME = JDK 安装根目录
#   PENTAHO_JAVA = java.exe 所在目录

# 4. 配置数据库驱动
# 将对应数据库的 JDBC 驱动 jar 复制到 data-integration\lib\
#   MySQL: mysql-connector-j-8.0.x.jar
#   Oracle: ojdbc8.jar
#   SQL Server: mssql-jdbc.jar
#   PostgreSQL: postgresql-42.x.x.jar

# 5. 启动 Spoon
# Windows: 双击 data-integration\Spoon.bat
# Linux: ./spoon.sh

# 6. 命令行执行（生产环境）
# Pan 执行转换：
#   pan.bat /rep:仓库名 /user:用户名 /pass:密码 /trans:转换名 "/param:date=2024-01-01"
# Kitchen 执行作业：
#   kitchen.bat /rep:仓库名 /user:用户名 /pass:密码 /job:作业名
```

### 核心组件对比

| 组件 | 用途 | 执行对象 | 使用场景 |
|---|---|---|---|
| Spoon | GUI 设计 | .ktr / .kjb | 开发、调试、设计 |
| Pan | 命令行执行 | .ktr（转换） | 脚本调度、自动化 |
| Kitchen | 命令行执行 | .kjb（作业） | 生产调度、定时任务 |
| Carte | Web 服务器 | 远程执行 | 集群、分布式 ETL |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| JDK 版本不匹配 | 启动报错或功能异常 | Kettle 9.x 用 JDK 11+，8.x 用 JDK 8 |
| 忘记放数据库驱动 | 连接数据库时报 ClassNotFound | 把 JDBC jar 放到 data-integration\\lib |
| 用 Spoon 跑生产任务 | 性能差、需人工值守 | 生产用 Pan/Kitchen 命令行 + 调度器 |
| 转换和作业混淆 | 转换里写流程控制，作业里写数据处理 | 转换=数据流（并行），作业=工作流（串行） |

### 动手

1. 下载并安装 Kettle 社区版，配置 JDK 和 MySQL 驱动
2. 启动 Spoon，新建一个空转换，保存为 test.ktr
3. 写一句「Kettle 的转换和作业有什么区别，什么时候用哪个」
""")

leaf_transformation = make_leaf("etl-kettle-transformation", "转换 Transformation", "??", """### 课前

- **场景**：要把 MySQL 的用户表数据清洗后写入 PostgreSQL，需要设计一个数据转换流程。
- **目标**：掌握转换的核心概念（步骤、跳、并行、数据行）、常用输入输出步骤、转换设计流程。
- **先修**：Kettle 核心组件与安装

### 是什么

- **一句话定义**：转换（Transformation，.ktr）是 Kettle 中处理数据抽取、转换、装载的核心对象，由多个步骤（Step）通过跳（Hop）连接而成，所有步骤并行执行，数据行在步骤间流动。
- **核心概念**：
  - **步骤（Step）**：转换的基本单元，如表输入、过滤、表输出等
  - **跳（Hop）**：步骤间的连线，本质是行级缓存（默认 10000 行），数据从一个步骤流向另一个步骤
  - **数据行（Row）**：数据的单位，包含多个字段
  - **并行执行**：转换启动后所有步骤同时启动，各自独立线程运行
- **设计原则**：转换是数据流，关注数据从哪来、怎么处理、到哪去；不关注执行顺序（因为并行）

### 怎么写

```text
# 转换设计流程（以 MySQL → 清洗 → PostgreSQL 为例）

# 1. 新建转换
#    File → New → Transformation（或 Ctrl+N）
#    保存为 user_migration.ktr

# 2. 创建数据库连接
#    左侧主对象树 → DB 连接 → 右键新建
#    连接1：mysql_src（MySQL，源库）
#    连接2：pg_dest（PostgreSQL，目标库）
#    分别测试连接成功

# 3. 添加步骤（从左侧核心对象拖拽到画布）
#    输入 → 表输入（命名：读取用户表）
#      配置：选择 mysql_src 连接
#      SQL：SELECT id, name, age, email, created_at FROM users
#      勾选"替换SQL语句里的变量"（如果用参数）

#    转换 → 字段选择（命名：字段映射）
#      配置：重命名字段、修改类型、删除不需要的字段

#    转换 → 过滤行（命名：过滤无效数据）
#      配置：条件 name IS NOT NULL AND age > 0

#    输出 → 表输出（命名：写入目标表）
#      配置：选择 pg_dest 连接
#      目标表：users_backup
#      勾选"指定数据库字段"，映射流字段到表字段
#      设置提交记录数：1000（批量提交提升性能）

# 4. 连接步骤（创建 Hop）
#    选中第一个步骤，按住 Shift 拖到下一个步骤
#    或选中步骤，按住中键拖到目标步骤
#    顺序：表输入 → 字段选择 → 过滤行 → 表输出

# 5. 预览数据
#    右键步骤 → Preview（预览），查看该步骤输出的数据
#    确认数据正确后再运行

# 6. 运行转换
#    点击工具栏绿色三角形（或 F9）
#    查看执行结果：每个步骤显示读取/写入/输出/更新/拒绝的行数
#    绿色对勾=成功，红色叉=失败
```

### 转换的并行机制

```text
启动转换时：
  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ 表输入  │───→│ 字段选择│───→│ 过滤行  │───→│ 表输出  │
  │ (线程1) │    │ (线程2) │    │ (线程3) │    │ (线程4) │
  └─────────┘    └─────────┘    └─────────┘    └─────────┘
       ↑              ↑              ↑              ↑
  所有步骤同时启动，数据行通过跳（行集缓存）流动
  表输入生成数据 → 字段选择处理 → 过滤行筛选 → 表输出写入
  直到输入跳无数据，步骤才中止
```

### 常用输入输出步骤

| 分类 | 步骤 | 用途 |
|---|---|---|
| 输入 | 表输入 | 从数据库读取数据（最常用） |
| 输入 | 文本文件输入 | 读取 CSV/TXT 文件 |
| 输入 | Excel 输入 | 读取 Excel 文件 |
| 输入 | JSON 输入 | 读取 JSON 文件 |
| 输入 | 生成记录 | 生成测试数据 |
| 输入 | 获取系统信息 | 读取系统变量、日期等 |
| 输出 | 表输出 | 向数据库表插入数据 |
| 输出 | 插入/更新 | 根据条件插入或更新（UPSERT） |
| 输出 | 更新 | 仅更新已有记录 |
| 输出 | 删除 | 根据条件删除记录 |
| 输出 | 文本文件输出 | 输出到 CSV/TXT |
| 输出 | Excel 输出 | 输出到 Excel |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 在转换里用 Start/Success 节点 | 转换没有这些节点，只有作业有 | 流程控制用作业（Job），数据处理用转换 |
| 忘记设置字段映射 | 表输出时字段不匹配或报错 | 勾选"指定数据库字段"，手动映射 |
| 跳的方向连反 | 数据流向错误 | 箭头方向=数据流动方向，从源到目标 |
| 大表全量预览 | Spoon 卡死 | 预览时在 SQL 后加 LIMIT，或用小样本测试 |
| 步骤名重复 | 转换报错 | 每个步骤名在转换内必须唯一 |

### 动手

1. 设计一个转换：从 MySQL 的 test 表读取数据，过滤 age>=18，写入另一个表
2. 用预览功能检查每个步骤的输出数据
3. 运行转换，查看各步骤的读写行数统计
""")

leaf_job = make_leaf("etl-kettle-job", "作业 Job", "??", """### 课前

- **场景**：每天凌晨要依次执行：清空临时表 → 跑数据转换 → 发送成功邮件 → 失败时告警，需要编排整个工作流。
- **目标**：掌握作业的核心概念（作业项、作业跳、串行/并行、结果传递）、常用作业项、作业设计流程。
- **先修**：转换 Transformation

### 是什么

- **一句话定义**：作业（Job，.kjb）是 Kettle 中用于组织和控制转换及其他任务执行顺序的工作流，由作业项（Job Entry）通过作业跳（Job Hop）连接，默认串行执行，支持条件分支和并行。
- **核心概念**：
  - **作业项（Job Entry）**：作业的基本单元，如 Start、Transformation、Job、Mail、Shell 等
  - **作业跳（Job Hop）**：作业项间的连接线，根据上一步执行结果决定下一步（绿色=成功，红色=失败，蓝色=无条件）
  - **串行执行**：默认按顺序执行，一个完成后才执行下一个
  - **并行执行**：可设置某个作业项的后续项并行执行
  - **结果对象**：作业项间传递的数据，包含数据行、文件名、行数统计、退出状态等
- **与转换的区别**：转换=数据流（并行，处理数据），作业=工作流（串行，控制流程）

### 怎么写

```text
# 作业设计流程（以每日 ETL 任务为例）

# 1. 新建作业
#    File → New → Job
#    保存为 daily_etl.kjb

# 2. 添加作业项（从左侧核心对象拖拽）
#    通用 → Start（作业起点，必须有且只有一个）
#    通用 → Transformation（执行转换）
#      配置：选择 user_migration.ktr
#      可传递参数：/param:date=${DATE}
#    通用 → Transformation（执行第二个转换）
#      配置：选择 agg_report.ktr
#    邮件 → 发送邮件（成功通知）
#      配置：SMTP 服务器、发件人、收件人、主题、正文
#    通用 → Success（作业成功结束）
#    通用 → Abort（作业中止，用于失败分支）

# 3. 连接作业项（创建作业跳）
#    Start → 转换1 → 转换2 → 发送邮件 → Success（绿色线，成功后执行）
#    转换1 → Abort（红色线，失败后执行）
#    转换2 → Abort（红色线，失败后执行）

# 4. 配置作业跳的颜色（执行条件）
#    绿色连接线：上一步成功后执行（默认）
#    红色连接线：上一步失败后执行
#    蓝色连接线：无论成功失败都执行
#    右键连接线 → 选择"Unconditional"/"Follow when result is true"/"Follow when result is false"

# 5. 设置并行执行（可选）
#    右键某个作业项 → 勾选"Run Next Entries in Parallel"
#    则该作业项的所有后续项会并行执行

# 6. 运行作业
#    点击运行按钮，查看执行日志
#    每个作业项显示执行状态（成功/失败/跳过）

# 7. 生产调度
#    用 Kitchen 命令行执行：
#    kitchen.bat /rep:仓库名 /user:admin /pass:xxx /job:daily_etl
#    配合 Windows 任务计划程序或 Linux crontab 实现定时执行
```

### 作业执行路径

```text
                    ┌──────────┐
                    │  Start   │
                    └────┬─────┘
                         │ 成功（绿色）
                    ┌────▼─────┐
                    │ 转换1    │───失败（红色）──→ Abort（中止）
                    └────┬─────┘
                         │ 成功
                    ┌────▼─────┐
                    │ 转换2    │───失败（红色）──→ Abort
                    └────┬─────┘
                         │ 成功
                    ┌────▼─────┐
                    │ 发送邮件  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ Success  │
                    └──────────┘
```

### 常用作业项分类

| 分类 | 作业项 | 用途 |
|---|---|---|
| 通用 | Start | 作业起点（必须有） |
| 通用 | Success | 作业成功结束 |
| 通用 | Abort | 作业中止（失败） |
| 通用 | Transformation | 执行转换（.ktr） |
| 通用 | Job | 嵌套执行另一个作业（.kjb） |
| 通用 | Dummy | 占位/空操作 |
| 通用 | Wait for SQL | 等待 SQL 条件满足 |
| 脚本 | Shell | 执行 Shell 脚本 |
| 脚本 | SQL | 执行 SQL 语句 |
| 脚本 | JavaScript | 执行 JS 脚本（高级流程控制） |
| 脚本 | Python | 执行 Python 脚本 |
| 邮件 | 发送邮件 | 发送通知邮件 |
| 文件管理 | 创建目录 | 创建文件夹 |
| 文件管理 | 删除文件 | 删除文件 |
| 文件管理 | 移动文件 | 移动/重命名文件 |
| 文件管理 | 复制文件 | 复制文件 |
| 条件 | 检查文件是否存在 | 判断文件是否存在 |
| 条件 | 检查数据库表是否存在 | 判断表是否存在 |
| 文件传输 | FTP 上传/下载 | FTP 文件传输 |
| 文件传输 | SFTP | SFTP 安全文件传输 |
| 大数据 | Hadoop 操作 | HDFS/Hive/HBase 操作 |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 作业里没有 Start 节点 | 作业无法启动 | 每个作业必须有且只有一个 Start |
| 转换和作业的文件搞混 | 执行报错 | .ktr 用 Pan/Transformation 执行，.kjb 用 Kitchen/Job 执行 |
| 作业跳的颜色设置错 | 失败时不告警，成功时走失败分支 | 绿色=成功执行，红色=失败执行，蓝色=无条件 |
| 在作业里写数据处理逻辑 | 性能差、难维护 | 数据处理放转换，作业只负责编排和控制 |
| 忘记配置失败分支 | 转换失败后作业继续跑后续步骤 | 每个关键转换都应配置失败分支（发邮件/Abort） |

### 动手

1. 设计一个作业：Start → 执行 user_migration.ktr → 成功发邮件 → Success，失败 Abort
2. 配置作业跳的颜色：成功走绿色线，失败走红色线
3. 用 Kitchen 命令行执行这个作业，查看执行日志
""")

leaf_steps = make_leaf("etl-kettle-steps", "常用步骤分类", "??", """### 课前

- **场景**：设计转换时需要各种数据处理步骤，不知道 Kettle 提供了哪些步骤、各自怎么用。
- **目标**：掌握 Kettle 转换中常用步骤的分类、用途和关键配置，能根据需求选择合适的步骤。
- **先修**：转换 Transformation

### 是什么

- **一句话定义**：Kettle 转换提供了 200+ 个步骤（Step），按功能分为输入、输出、转换、脚本、查询、连接、流程、作业、映射、批量、大数据等类别，覆盖数据处理的各种场景。
- **学习策略**：不需要背所有步骤，掌握最常用的 20-30 个，其余用时在左侧核心对象里搜索。

### 常用步骤分类详解

#### 1. 输入类（Input）—— 数据来源

| 步骤 | 用途 | 关键配置 |
|---|---|---|
| 表输入 | 从数据库读取数据 | 数据库连接 + SQL 语句，支持变量替换 |
| 文本文件输入 | 读取 CSV/TXT | 文件路径、分隔符、编码、字段定义 |
| Excel 输入 | 读取 Excel | 工作表、起始行、字段映射 |
| JSON 输入 | 读取 JSON | JSON Path 提取字段 |
| XML 输入 | 读取 XML | XPath 路径 |
| 生成记录 | 生成测试数据 | 行数、常量字段 |
| 获取系统信息 | 读取系统变量 | 选择系统信息类型（日期、环境变量等） |
| 从结果获取记录 | 从作业结果获取数据 | 配合作业中的"复制记录到结果" |

#### 2. 输出类（Output）—— 数据目的地

| 步骤 | 用途 | 关键配置 |
|---|---|---|
| 表输出 | 向数据库插入 | 连接 + 目标表 + 字段映射 + 批量提交 |
| 插入/更新 | UPSERT | 查询关键字段，不存在插入，存在更新 |
| 更新 | 仅更新 | 根据指定字段更新已有记录 |
| 删除 | 仅删除 | 根据指定字段删除记录 |
| 同步 | 增删改三合一 | 根据字段判断执行插入/更新/删除 |
| 文本文件输出 | 输出 CSV/TXT | 路径、分隔符、编码、是否含表头 |
| Excel 输出 | 输出 Excel | 文件名、工作表、字段 |
| 复制记录到结果 | 传递给作业 | 供后续作业项使用 |

#### 3. 转换类（Transform）—— 数据清洗和处理

| 步骤 | 用途 | 说明 |
|---|---|---|
| 字段选择 | 选择/重命名/删除字段，修改类型 | 最常用的字段管理步骤 |
| 计算器 | 新建计算字段 | 加减乘除、字符串函数、日期函数、逻辑运算 |
| 值映射 | 字段值映射替换 | 如 1→男、0→女，支持默认值 |
| 增加常量 | 添加固定值字段 | 给每行添加一个常量字段 |
| 增加序列 | 添加自增序列 | 生成 1,2,3... 序号 |
| 字符串操作 | 字符串处理 | 去空格、大小写、截取、替换、长度 |
| 替换字符串 | 正则/普通替换 | 支持正则表达式 |
| 去重 | 去除重复行 | 按指定字段去重 |
| 排序 | 按字段排序 | 升序/降序，多字段 |
| 过滤行 | 按条件过滤 | 条件表达式，满足条件的行通过 |
| 分组聚合 | 分组统计 | SUM/COUNT/AVG/MIN/MAX |
| 拆分字段 | 按分隔符拆分 | 一个字段拆成多个字段 |
| 合并记录 | 比较两个流的差异 | 标记 identical/changed/new/deleted |
| 行转列/列转行 | 行列转换 | 透视/反透视 |

#### 4. 脚本类（Scripting）—— 自定义逻辑

| 步骤 | 用途 | 说明 |
|---|---|---|
| JavaScript 脚本 | 写 JS 代码 | 最灵活，可写复杂逻辑，访问每行字段 |
| Java 代码 | 写 Java 代码 | 性能更好，适合复杂计算 |
| 执行 SQL 脚本 | 执行任意 SQL | DDL/DML，如建表、清空表 |
| 用户自定义 Java 表达式 | 简单 Java 表达式 | 轻量级计算 |

#### 5. 查询类（Lookup）—— 关联查询

| 步骤 | 用途 | 说明 |
|---|---|---|
| 数据库查询 | 关联数据库表 | 按指定字段到数据库查询，类似 LEFT JOIN |
| 流查询 Stream Lookup | 两个流关联 | 一个流做查找表，另一个按 key 查找，性能好 |
| 合并连接 Merge Join | 两个已排序流 JOIN | INNER/LEFT/RIGHT/FULL JOIN，要求按连接键排序 |
| HTTP 客户端 | 调用 HTTP API | GET/POST 请求，获取返回数据 |

#### 6. 流程类（Flow）—— 控制数据流向

| 步骤 | 用途 | 说明 |
|---|---|---|
| 空操作 Dummy | 什么都不做 | 调试、占位、错误处理终点 |
| 中止 Abort | 满足条件中止转换 | 数据质量校验，遇到错误行中止 |
| 写日志 | 输出数据到日志 | 调试用，打印字段值 |
| 发送邮件 | 转换中发邮件 | 满足条件时发通知 |

#### 7. 作业类（Job）—— 与作业交互

| 步骤 | 用途 |
|---|---|
| 复制记录到结果 | 把数据行传到作业结果 |
| 从结果获取记录 | 从作业结果获取数据行 |
| 设置变量 | 设置环境变量/命名参数 |
| 获取变量 | 获取变量值到字段 |
| 执行作业 | 转换中嵌套执行作业 |
| 执行转换 | 转换中嵌套执行转换 |

### 步骤选择决策树

```text
需要做什么？
├── 数据从哪来？→ 输入类
│   ├── 数据库 → 表输入
│   ├── CSV/TXT → 文本文件输入
│   └── Excel → Excel 输入
├── 数据怎么处理？→ 转换类
│   ├── 字段增删改 → 字段选择/增加常量/计算器
│   ├── 过滤 → 过滤行
│   ├── 清洗 → 字符串操作/值映射/去重/排序
│   └── 聚合 → 分组聚合
├── 数据关联？→ 查询类
│   ├── 关联数据库 → 数据库查询
│   ├── 关联另一个流 → 流查询/合并连接
│   └── 复杂逻辑 → JavaScript 脚本
└── 数据到哪去？→ 输出类
    ├── 插入 → 表输出
    ├── 插入或更新 → 插入/更新
    ├── 文件 → 文本文件输出/Excel 输出
    └── 传给作业 → 复制记录到结果
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用数据库查询做大数据关联 | 性能差（每行查一次库） | 用流查询（内存哈希）或合并连接 |
| 合并连接前未排序 | 结果错误或丢失数据 | Merge Join 要求两个流都按连接键排序 |
| JavaScript 脚本里写循环 | 性能差 | 能用内置步骤就不用脚本，脚本只做复杂逻辑 |
| 过滤行条件写错 | 数据被错误过滤 | 仔细检查条件表达式，用预览验证 |
| 字段选择后字段丢失 | 后续步骤找不到字段 | 字段选择里确认需要的字段都勾选了 |

### 动手

1. 设计一个转换：表输入 → 过滤行（amount>100）→ 字符串操作（name 去空格转大写）→ 表输出
2. 用分组聚合步骤统计每个用户的订单数和总金额
3. 写一句「什么时候用数据库查询，什么时候用流查询」
""")

leaf_practice = make_leaf("etl-kettle-practice", "实战入门与调优", "???", """### 课前

- **场景**：已经学会了 Kettle 基础，要做一个真实的数据迁移项目，需要考虑参数化、性能优化、错误处理、生产部署。
- **目标**：掌握 Kettle 实战技巧：参数化、变量、性能优化、错误处理、命令行调度、资源库。
- **先修**：转换、作业、常用步骤分类

### 是什么

- **一句话定义**：Kettle 实战入门涵盖从开发到生产的全流程技巧，包括参数化复用、性能优化、错误处理、调度部署、资源库管理，让转换/作业从"能跑"变成"生产可用"。
- **核心能力**：参数化、变量传递、性能调优、错误处理、日志监控、命令行执行、资源库。

### 怎么写

```text
# ===== 1. 参数化与变量 =====

# 命名参数（在转换/作业设置中定义）
# 转换设置 → 命名参数标签 → 添加参数名和默认值
#   date = 2024-01-01
#   table_name = users

# 在 SQL 中引用参数（表输入步骤）
# SELECT * FROM ${table_name} WHERE created_at >= '${date}'
# 注意：必须勾选"替换SQL语句里的变量"

# 在路径中引用参数
# 文本文件输出路径：/data/output/${date}_users.csv

# 命令行传递参数
# pan.bat /trans:user_migration "/param:date=2024-01-15" "/param:table_name=orders"

# 设置变量步骤（在转换中动态设置变量）
# 作业 → 设置变量：变量名=batch_date，变量值=字段值
# 后续转换可以用 ${batch_date} 引用

# 获取变量步骤（把变量值读到字段）
# 作业 → 获取变量：变量名=date，输出字段=batch_date


# ===== 2. 性能优化 =====

# (1) 增加步骤副本数（多线程并行）
# 右键步骤 → "Change number of copies to start" → 输入线程数
# 适合：CPU 密集型步骤（如 JavaScript、复杂计算）
# 不适合：数据库写入（可能导致锁冲突）

# (2) 行集大小调整
# 转换设置 → 杂项 → "大小 of row set"（默认 10000）
# 大数据量可调大（如 50000），减少线程切换开销
# 小数据量可调小，减少内存占用

# (3) 批量提交
# 表输出步骤 → "提交记录数量"（默认 1000，可设 5000-10000）
# 减少事务提交次数，大幅提升写入性能

# (4) 使用唯一连接（单事务）
# 转换设置 → 杂项 → 勾选"使用唯一连接"
# 所有步骤共用一个数据库连接和事务
# 适合：多个步骤写同一个库，需要事务一致性
# 注意：会降低并行度

# (5) 数据库连接池
# 数据库连接 → 选项 → 勾选"使用连接池"
# 适合：大量小转换/作业频繁创建连接

# (6) 分区表/分片
# 大表按分区键分片，并行写入多个分区
# 表输出步骤支持分区模式

# (7) 索引策略
# 大批量插入前可先禁用索引，插入后重建
# 用"执行 SQL 脚本"步骤：ALTER TABLE xxx DISABLE KEYS;


# ===== 3. 错误处理 =====

# (1) 步骤错误处理（错误行导向）
# 右键步骤 → "定义错误处理" → 配置：
#   启用错误处理：勾选
#   目标步骤：选择错误处理步骤（如文本文件输出）
#   错误描述字段名：error_desc
#   错误代码字段名：error_code
#   错误列字段名：error_column
# 效果：处理失败的行不会导致转换中止，而是流向错误处理步骤

# (2) 转换级别错误处理
# 转换设置 → 杂项 → "错误处理"
# 可设置最大错误行数，超过则中止

# (3) 作业级别错误处理
# 用红色作业跳（失败分支）处理转换失败
# 失败后：发邮件告警 → 写日志 → Abort 或 重试

# (4) 重试机制
# 作业项配置 → "高级" → 设置重试次数和间隔
# 适合：网络不稳定、数据库连接偶尔失败的场景


# ===== 4. 日志与监控 =====

# 日志级别（运行转换/作业时选择）
#   Error: 只显示错误
#   Warning: 错误和警告
#   Basic: 基本信息（默认，生产推荐）
#   Detailed: 详细信息
#   Debug: 调试信息（开发用，性能差）
#   Rowlevel: 每行数据（极详细，仅小样本调试）

# 日志输出
# 命令行执行时重定向到文件：
#   kitchen.bat /job:daily_etl > /logs/daily_etl_$(date +%Y%m%d).log 2>&1

# 执行结果统计
# 每个步骤显示：读取、写入、输出、输入、更新、拒绝、错误行数
# 转换结束显示：总耗时、总读取行数、总写入行数、错误数


# ===== 5. 资源库（Repository）=====

# 三种资源库类型：
# (1) 数据库资源库：所有元数据存在关系数据库中，适合团队协作
# (2) 文件资源库：元数据存在文件目录，适合个人开发
# (3) Pentaho 资源库：企业版插件

# 创建数据库资源库：
#   1. 新建一个空数据库（如 kettle_repo）
#   2. Spoon → 右上角"Connect" → "New Repository" → "Database Repository"
#   3. 配置数据库连接，测试连接
#   4. 点击"创建或升级"，自动创建资源库表
#   5. 用 admin/admin 登录（首次登录后修改密码）

# 资源库优势：
#   - 团队协作：多人共享转换/作业
#   - 版本管理：可查看历史版本
#   - 权限控制：用户/角色权限管理
#   - 统一调度：配合 Carte 集群调度


# ===== 6. 生产部署 checklist =====

# □ 转换/作业已参数化（不硬编码日期、表名、路径）
# □ 数据库连接使用资源库或 JNDI（不硬编码密码）
# □ 错误处理已配置（错误行记录、失败告警）
# □ 日志级别设置为 Basic（生产环境不用 Debug）
# □ 性能优化：批量提交、步骤副本数、行集大小
# □ 调度配置：Kitchen/Pan 命令行 + crontab/任务计划
# □ 监控告警：失败发邮件、执行时长监控
# □ 备份：资源库定期备份、转换/作业文件版本管理
```

### 性能优化优先级

| 优先级 | 优化手段 | 效果 | 风险 |
|---|---|---|---|
| 1 | 批量提交（表输出） | 写入性能提升 5-10 倍 | 低 |
| 2 | 增加步骤副本数 | CPU 密集步骤提升 N 倍 | 中（需确认步骤可并行） |
| 3 | 行集大小调大 | 减少线程切换，提升 10-30% | 低（内存占用增加） |
| 4 | 使用唯一连接 | 事务一致性，减少连接开销 | 中（并行度降低） |
| 5 | 禁用索引后重建 | 大批量插入提升 2-5 倍 | 中（插入期间查询慢） |
| 6 | 数据库分区/分片 | 大表写入并行化 | 高（架构改动大） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| SQL 中用了变量但没勾选"替换变量" | 变量不替换，SQL 报错 | 表输入步骤必须勾选"替换SQL语句里的变量" |
| 生产环境用 Debug 日志级别 | 性能极差，日志爆炸 | 生产用 Basic，开发才用 Debug |
| 表输出不设批量提交 | 每条提交一次，性能极差 | 设置提交记录数 1000+ |
| 错误行不处理直接中止 | 一条脏数据导致整个转换失败 | 配置错误处理，错误行单独记录 |
| 硬编码数据库密码 | 安全风险，环境迁移麻烦 | 用资源库或 JNDI，密码不写在文件里 |
| 用 Spoon 跑生产任务 | 需人工值守，性能差 | 生产用 Kitchen/Pan 命令行 + 调度器 |

### 动手

1. 给 user_migration.ktr 添加参数 date，在 SQL 中用 ${date} 过滤，命令行传参执行
2. 配置表输出的批量提交为 5000，给计算步骤增加 2 个副本，对比性能
3. 给转换配置错误处理：处理失败的行写入错误日志文件，转换不中止
4. 写一句「Kettle 和 DataX/Airbyte 相比，各自的适用场景是什么」
""")

# ========== 组装章节 ==========
chapter_core = make_chapter("etl-kettle-core", "核心组件与安装", "?", [leaf_install])
chapter_trans = make_chapter("etl-kettle-trans", "转换与作业", "??", [leaf_transformation, leaf_job])
chapter_steps = make_chapter("etl-kettle-steps-ch", "常用步骤与实战", "??", [leaf_steps, leaf_practice])

# ========== Kettle 领域节点（在工具选型下） ==========
kettle_content = """### 课前 · 节点导读

- **节点**：Kettle / PDI（Pentaho Data Integration）
- **定位**：开源可视化 ETL 工具，纯 Java 编写，跨平台，拖拽式设计数据流程
- **适用场景**：数据迁移、数据同步、ETL 作业编排、小到中等数据量的批处理
- **优势**：开源免费、可视化拖拽、组件丰富、社区活跃、支持集群
- **劣势**：大数据量性能不如专门的分布式工具、学习曲线较陡、企业版需付费

### Kettle 是什么

Kettle（现在叫 PDI，Pentaho Data Integration）是一款流行的开源 ETL 工具，2006 年被 Pentaho 收购，2015 年被 Hitachi Vantara 收购。它允许用户通过图形化界面设计数据抽取、转换、装载流程，支持多种数据源和目标，是数据仓库建设和数据迁移的常用工具。

### 核心组件

| 组件 | 用途 | 执行对象 |
|---|---|---|
| Spoon | GUI 设计工具 | .ktr / .kjb |
| Pan | 命令行执行 | .ktr（转换） |
| Kitchen | 命令行执行 | .kjb（作业） |
| Carte | Web 服务器/集群 | 远程执行 |

### 两大核心概念

- **转换（Transformation，.ktr）**：数据流，所有步骤并行执行，处理数据的抽取/转换/装载
- **作业（Job，.kjb）**：工作流，默认串行执行，控制转换和其他任务的执行顺序、条件分支、错误处理

### 子章节地图

| 章节 | 一句话 |
|---|---|
| 核心组件与安装 | 下载安装、JDK 配置、四大组件、Spoon 启动 |
| 转换与作业 | 转换设计（步骤/跳/并行）、作业编排（作业项/作业跳/调度） |
| 常用步骤与实战 | 200+ 步骤分类、参数化、性能优化、错误处理、生产部署 |

### 推荐学习顺序

```text
核心组件与安装 → 转换与作业 → 常用步骤与实战
```

### 与其他工具的对比

| 工具 | 类型 | 可视化 | 大数据 | 适用场景 |
|---|---|---|---|---|
| Kettle/PDI | 传统 ETL | 强 | 一般 | 数据迁移、中小数据量批处理 |
| DataX | 数据同步 | 弱（JSON配置） | 较好 | 异构数据源批量同步 |
| Airbyte | 数据集成 | 强 | 较好 | 连接器丰富的 ELT |
| Flink CDC | 实时同步 | 弱 | 强 | 实时变更数据捕获 |
| Airflow | 任务编排 | 中 | 强 | DAG 调度、工作流编排 |
| dbt | 数据转换 | 中 | 强 | 仓内 SQL 转换、建模 |

### 下一动

打开第一个子章节，开始学习 Kettle。本节点约 **5** 片叶讲义。
"""

kettle_node = {
    "id": "etl-tool-kettle",
    "title": "Kettle / PDI",
    "level": "???",
    "content": kettle_content,
    "children": [chapter_core, chapter_trans, chapter_steps]
}

# ========== 插入到 embed-etl.js ==========
with open(r"D:\cursor\数据学习平台\kg-data\embed-etl.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["etl"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
if not match:
    print("ERROR: Cannot find JSON in embed-etl.js")
    exit(1)

data = json.loads(match.group(1))
print(f"Original ETL tree loaded")

# 找到工具选型 → 选型地图节点
def find_node(node, target_id):
    if node.get("id") == target_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, target_id)
        if result:
            return result
    return None

selection_map = find_node(data, "etl-tool-map")
if not selection_map:
    print("ERROR: Cannot find 选型地图 node")
    # 尝试找工具选型
    tool_selection = find_node(data, "工具选型")
    if tool_selection:
        print(f"Found 工具选型, children: {[c['title'] for c in tool_selection.get('children', [])]}")
    exit(1)

print(f"Found 选型地图, current children: {[c['title'] for c in selection_map.get('children', [])]}")

# 检查是否已存在 Kettle
existing = [c for c in selection_map["children"] if "Kettle" in c.get("title", "")]
if existing:
    print("Kettle already exists, replacing...")
    selection_map["children"] = [c for c in selection_map["children"] if "Kettle" not in c.get("title", "")]

# 插入 Kettle 节点（放在最后）
selection_map["children"].append(kettle_node)
print(f"New children: {[c['title'] for c in selection_map['children']]}")

# 序列化
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["etl"]={new_json_str}\n'

with open(r"D:\cursor\数据学习平台\kg-data\embed-etl.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-etl.js size: {len(new_content)} bytes")
print("Kettle/PDI 节点已成功插入 ETL 知识图谱")
