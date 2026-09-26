#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""综合补充：ETL数据质量、数据库范式/主从、Python面向对象/正则/matplotlib、BI可视化原则、SQL函数"""

import json, re, os

data_dir = r"D:\cursor\数据学习平台\kg-data"

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

def load_domain(domain):
    filepath = os.path.join(data_dir, f"embed-{domain}.js")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'window\.__KG_EMBEDDED\["' + domain + r'"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
    return json.loads(match.group(1))

def save_domain(domain, data):
    new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["{domain}"]={new_json_str}\n'
    filepath = os.path.join(data_dir, f"embed-{domain}.js")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return len(new_content)

def find_node(node, node_id):
    if node.get("id") == node_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result:
            return result
    return None

# ========== ETL：数据质量 ==========
leaf_dq = make_leaf("etl-data-quality", "数据质量", "??", """### 课前

- **场景**：ETL 跑通了，但下游报表数据经常出错（空值、重复、不一致），需要建立数据质量管控。
- **目标**：掌握数据质量六大维度（完整性/准确性/一致性/及时性/唯一性/有效性）、质量校验规则、质量监控与告警。
- **先修**：ETL 基础概念

### 是什么

- **一句话定义**：数据质量是衡量数据是否满足业务使用要求的标准，通过在 ETL 各环节设置校验规则、监控指标、告警机制，确保数据从源到目标的准确可靠。
- **六大维度**：
  - **完整性（Completeness）**：数据是否缺失（空值、缺失记录）
  - **准确性（Accuracy）**：数据是否正确（与真实值/源系统一致）
  - **一致性（Consistency）**：同一数据在不同地方是否一致（跨表/跨系统）
  - **及时性（Timeliness）**：数据是否按时产出（延迟、刷新频率）
  - **唯一性（Uniqueness）**：数据是否重复（主键重复、重复记录）
  - **有效性（Validity）**：数据是否符合格式/范围/业务规则（枚举值、数值范围、日期格式）

### 怎么写

```text
# ===== 数据质量校验规则设计 =====

# 1. 完整性校验
#    - 非空校验：关键字段不能为 NULL（用户ID、订单号、金额）
#    - 记录数校验：目标表记录数与源表差异在阈值内
#    - 字段覆盖率：必填字段的非空比例 ≥ 99%

# 2. 准确性校验
#    - 数值范围：金额 > 0，年龄在 0-150
#    - 业务规则：支付金额 = 商品金额 + 运费 - 优惠
#    - 源目标对比：抽样对比源系统和目标系统的关键字段

# 3. 一致性校验
#    - 跨表一致：订单表的用户ID必须在用户表中存在（参照完整性）
#    - 跨系统一致：CRM 系统的客户数与数仓客户数一致
#    - 指标一致：同一指标在不同报表中数值相同

# 4. 及时性校验
#    - 产出时间：每日 T+1 数据必须在早上 8 点前完成
#    - 延迟监控：数据延迟超过阈值告警
#    - 刷新频率：实时数据延迟 < 5 分钟

# 5. 唯一性校验
#    - 主键唯一：订单ID不能重复
#    - 业务唯一：同一用户同一商品同一天不能有重复订单
#    - 去重率：重复记录比例 < 0.1%

# 6. 有效性校验
#    - 格式校验：手机号 11 位数字、邮箱格式、日期格式 YYYY-MM-DD
#    - 枚举校验：状态只能是（待支付/已支付/已发货/已完成/已取消）
#    - 范围校验：折扣率在 0-1 之间，利率在合理范围


# ===== ETL 中的质量门禁实现 =====

# 方式1：SQL 校验（在 ETL 流程中嵌入校验步骤）
# 校验不通过则中止任务并告警
-- 非空校验
SELECT COUNT(*) FROM orders WHERE order_id IS NULL OR user_id IS NULL;
-- 结果 > 0 则告警

-- 主键重复校验
SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1;
-- 结果 > 0 则告警

-- 数值范围校验
SELECT COUNT(*) FROM orders WHERE amount <= 0 OR amount > 1000000;

-- 参照完整性校验
SELECT COUNT(*) FROM orders o 
LEFT JOIN users u ON o.user_id = u.user_id 
WHERE u.user_id IS NULL;

# 方式2：专用数据质量工具
#   - Great Expectations（Python，开源）
#   - Apache Griffin（开源，批处理质量监控）
#   - DataWorks 数据质量（阿里云）
#   - 自研质量校验平台

# 方式3：Kettle 中的错误处理
#   - 步骤错误处理：处理失败的行流向错误日志表
#   - 转换级别：设置最大错误行数，超过则中止
#   - 作业级别：失败分支发邮件告警


# ===== 质量监控与告警 =====

# 质量看板：
#   - 每日数据质量得分（六大维度加权）
#   - 各表质量评分排名
#   - 质量问题趋势（问题数随时间变化）
#   - 未解决问题列表

# 告警机制：
#   - 严重问题（主键重复、数据大量缺失）：电话/短信告警
#   - 一般问题（少量空值、格式错误）：邮件/飞书告警
#   - 轻微问题（趋势波动）：看板展示，定期复盘

# 质量 SLA：
#   - 核心表：数据质量得分 ≥ 99 分，问题 2 小时内响应
#   - 重要表：数据质量得分 ≥ 95 分，问题 24 小时内响应
#   - 一般表：数据质量得分 ≥ 90 分，问题 72 小时内响应
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 只在最后做质量校验 | 问题发现太晚，回溯成本高 | 在 ETL 各环节（抽取后/转换后/装载后）都设置质量门禁 |
| 质量规则太松 | 问题数据流入下游 | 核心字段必须严格校验，设置合理阈值 |
| 质量规则太严 | 正常数据被误拦截 | 区分硬规则（必须通过）和软规则（告警但不拦截） |
| 只有技术校验没有业务校验 | 技术上正确但业务上错误 | 加入业务规则校验（如金额=单价×数量） |
| 质量问题没人跟进 | 问题反复出现 | 每个质量问题指定负责人，建立问题跟踪和闭环机制 |

### 动手

1. 给一张订单表设计 10 条数据质量校验规则，覆盖六大维度
2. 写 5 条 SQL 校验语句（非空/重复/范围/参照完整性/业务规则）
3. 画一个 ETL 流程中的质量门禁架构图，标注在哪些环节做什么校验
""")

# ========== 数据库：范式 + 主从复制 ==========
leaf_normalization = make_leaf("db-normalization", "数据库范式", "??", """### 课前

- **场景**：设计数据库表时不知道怎么拆表，导致数据冗余、更新异常、插入删除异常。
- **目标**：掌握第一范式（1NF）、第二范式（2NF）、第三范式（3NF）、BCNF 的定义和应用，理解反范式的适用场景。
- **先修**：数据库基础、主键外键

### 是什么

- **一句话定义**：数据库范式是设计关系型数据库表结构的规范，通过逐层分解表来减少数据冗余和避免更新/插入/删除异常，越高范式冗余越少但查询可能越复杂。
- **核心矛盾**：范式越高 → 冗余越少、一致性越好 → 但表越多、JOIN 越多、查询越慢。实际中通常做到 3NF，数据仓库中常用反范式。

### 范式详解

```text
# ===== 第一范式（1NF）=====
# 定义：每个字段都是原子值，不可再拆分
# 反例（不满足1NF）：
#   用户表：user_id | user_name | phones
#             1     | 张三      | 13800138000,13900139000
#   phones 字段存了多个手机号，不是原子值
# 正例（满足1NF）：
#   方案A：拆成多个字段 phone1, phone2（不推荐，数量固定）
#   方案B：新建用户电话表（推荐，一对多）
#     user_phones: user_id | phone
#                    1     | 13800138000
#                    1     | 13900139000

# ===== 第二范式（2NF）=====
# 定义：在1NF基础上，非主键字段完全依赖于整个主键（不能只依赖主键的一部分）
# 前提：有联合主键
# 反例（不满足2NF）：
#   订单商品表：order_id | product_id | product_name | quantity | price
#                主键 = (order_id, product_id)
#   product_name 只依赖 product_id，不依赖 order_id
#   → 部分依赖，不满足2NF
#   问题：同一个商品在不同订单中重复存储商品名，修改商品名要改很多行
# 正例（满足2NF）：
#   拆成两张表：
#   订单明细表：order_id | product_id | quantity | price
#   商品表：    product_id | product_name | category

# ===== 第三范式（3NF）=====
# 定义：在2NF基础上，非主键字段不传递依赖于主键
# （非主键字段只能直接依赖主键，不能依赖另一个非主键字段）
# 反例（不满足3NF）：
#   订单表：order_id | user_id | user_name | user_phone | amount
#   user_name 和 user_phone 依赖 user_id，user_id 依赖 order_id
#   → 传递依赖，不满足3NF
#   问题：用户信息在每个订单中重复，修改用户信息要改所有相关订单
# 正例（满足3NF）：
#   拆成两张表：
#   订单表：order_id | user_id | amount
#   用户表：user_id | user_name | user_phone

# ===== BCNF（巴斯-科德范式）=====
# 定义：在3NF基础上，主键的任何一部分都不能被非主键字段决定
# （消除主属性对主键的部分依赖和传递依赖）
# 通常3NF已经足够，BCNF是更严格的3NF
```

### 范式对比与选择

| 范式 | 核心要求 | 解决的问题 | 实际应用 |
|---|---|---|---|
| 1NF | 字段原子性 | 多值字段 | 所有关系型数据库都必须满足 |
| 2NF | 消除部分依赖 | 联合主键中的冗余 | 有联合主键时需要考虑 |
| 3NF | 消除传递依赖 | 非主键字段间的依赖 | 业务系统通常做到3NF |
| BCNF | 消除主属性依赖 | 更严格的冗余 | 一般不需要，特殊场景才用 |
| 4NF | 消除多值依赖 | 多对多关系 | 很少用到 |

### 反范式（数据仓库中常用）

```text
# 反范式：故意增加冗余，减少 JOIN，提升查询性能
# 适用场景：数据仓库、OLAP 系统、读多写少的场景

# 反范式常用手段：
# 1. 合并表：把经常 JOIN 的表合并成一张宽表
#    例：订单表 + 用户表 → 订单宽表（含用户信息）
#
# 2. 增加冗余列：把常用字段复制到多张表
#    例：订单表冗余 user_name，避免每次查用户表
#
# 3. 增加计算列：把经常计算的结果存为字段
#    例：订单表冗余 total_amount = quantity * price
#
# 4. 分组表：按维度预聚合
#    例：日销售汇总表、月销售汇总表

# 反范式的代价：
# - 数据冗余，存储空间增加
# - 更新异常，修改一处要同步更新多处
# - 数据一致性需要通过 ETL 保证
# 所以：业务系统（OLTP）用范式，分析系统（OLAP）用反范式
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 所有表都追求最高范式 | 表太多，查询要 JOIN 很多张，性能差 | 业务系统做到3NF即可，分析系统用反范式 |
| 一个字段存多个值 | 查询、统计、更新都困难 | 满足1NF，用关联表或JSON字段（谨慎） |
| 联合主键中部分字段决定其他字段 | 数据冗余、更新异常 | 满足2NF，拆表 |
| 非主键字段之间有依赖 | 传递依赖，更新异常 | 满足3NF，拆表 |
| 数据仓库也严格按3NF设计 | 查询慢，JOIN多 | 数据仓库用维度建模（星型/雪花），适当反范式 |

### 动手

1. 找出下面表设计中的范式问题并优化：学生选课表(学号, 姓名, 课程号, 课程名, 成绩, 学分)
2. 设计一个电商订单系统的表结构，满足3NF（订单、订单明细、用户、商品、收货地址）
3. 解释为什么数据仓库中常用反范式设计，举一个具体例子
""")

leaf_replication = make_leaf("db-replication", "主从复制与读写分离", "???", """### 课前

- **场景**：单台数据库扛不住高并发读请求，或者需要数据备份容灾，需要搭建主从复制。
- **目标**：掌握 MySQL 主从复制原理（binlog/IO线程/SQL线程）、读写分离架构、主从延迟问题、半同步复制。
- **先修**：数据库基础、事务、索引

### 是什么

- **一句话定义**：主从复制是将主库（Master）的数据变更通过 binlog 同步到从库（Slave），实现数据备份、读写分离、高可用的技术，是 MySQL 最常用的架构扩展方式。
- **核心用途**：数据备份容灾、读写分离（读请求走从库）、高可用（主库挂了从库提升）、数据分析（从库跑查询不影响主库）。

### 主从复制原理

```text
# MySQL 主从复制的三个核心线程：

# 1. 主库：binlog dump 线程
#    主库把数据变更写入 binlog（二进制日志）
#    当有从库连接时，主库创建 binlog dump 线程，把 binlog 推送给从库

# 2. 从库：IO 线程
#    从库的 IO 线程连接主库，请求 binlog
#    接收主库推送的 binlog，写入中继日志（relay log）

# 3. 从库：SQL 线程
#    从库的 SQL 线程读取 relay log，重放其中的 SQL 语句
#    把数据变更应用到从库的数据文件中

# 数据流：
#   主库执行SQL → 写入binlog → binlog dump线程推送 → 从库IO线程接收 → 写入relay log → SQL线程重放 → 从库数据更新
```

### 主从复制配置

```sql
-- ===== 主库配置（my.cnf）=====
-- [mysqld]
-- server-id=1                    -- 主库ID，必须唯一
-- log-bin=mysql-bin              -- 开启binlog
-- binlog-format=ROW              -- binlog格式：ROW/STATEMENT/MIXED
-- binlog-do-db=your_db           -- 只同步指定库（可选，不建议）
-- expire_logs_days=7             -- binlog保留7天
-- max_binlog_size=1G             -- 单个binlog最大1G

-- 主库创建复制用户
CREATE USER 'repl'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;

-- 查看主库状态（记录 File 和 Position）
SHOW MASTER STATUS;
-- +------------------+----------+--------------+
-- | File             | Position | Binlog_Do_DB |
-- +------------------+----------+--------------+
-- | mysql-bin.000001 |     1234 | your_db      |
-- +------------------+----------+--------------+

-- ===== 从库配置（my.cnf）=====
-- [mysqld]
-- server-id=2                    -- 从库ID，不能和主库相同
-- relay-log=relay-bin            -- 中继日志
-- read_only=1                    -- 从库设为只读（普通用户不能写）
-- super_read_only=1              -- 超级用户也只读（MySQL 5.7+）

-- 从库配置主库信息
CHANGE MASTER TO
  MASTER_HOST='主库IP',
  MASTER_USER='repl',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=1234;

-- 启动从库复制
START SLAVE;

-- 查看从库状态
SHOW SLAVE STATUS\G
-- 关键指标：
--   Slave_IO_Running: Yes      -- IO线程正常
--   Slave_SQL_Running: Yes     -- SQL线程正常
--   Seconds_Behind_Master: 0   -- 主从延迟（秒），0表示同步
```

### binlog 三种格式对比

| 格式 | 记录内容 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|---|
| **STATEMENT** | 记录执行的SQL语句 | 日志小、易读 | 不确定性函数（NOW()/UUID()）会导致主从不一致 | 简单SQL、SQL语句确定的场景 |
| **ROW** | 记录每行数据的变更 | 主从一致、无不确定性问题 | 日志大（大表UPDATE/DELETE会产生大量日志） | 默认推荐，绝大多数场景 |
| **MIXED** | 混合模式，自动选择 | 兼顾两者 | 复杂场景可能判断不准 | 一般不用 |

### 读写分离架构

```text
# 读写分离：写请求走主库，读请求走从库
# 
#         应用程序
#             │
#         数据库代理（ProxySQL/MyCat/应用层路由）
#          ┌────┴────┐
#        写          读
#          │          │
#       主库      ┌───┴───┐
#       (Master) 从库1    从库2
#          │    (Slave)  (Slave)
#          └──→ binlog同步 →──┘
#
# 实现方式：
# 1. 应用层路由：代码中判断读写，选择不同数据源
# 2. 中间件代理：ProxySQL、MyCat、MaxScale（对应用透明）
# 3. 数据库驱动：MySQL Connector/J 的 ReplicationDriver
#
# 注意事项：
# - 刚写入的数据立即查询可能读不到（主从延迟）
# - 解决方案：强制走主库（关键查询）、半同步复制、等待从库同步
```

### 主从延迟问题

```text
# 主从延迟（Seconds_Behind_Master > 0）的常见原因和解决方案：

# 1. 从库性能差
#    原因：从库配置比主库低，追不上主库的写入速度
#    解决：从库配置不低于主库，或使用并行复制

# 2. 大事务
#    原因：主库执行一个大事务（如批量更新1000万行），从库重放慢
#    解决：大事务拆成小事务分批执行

# 3. 单线程复制
#    原因：MySQL 5.5 及之前 SQL 线程是单线程，串行重放
#    解决：MySQL 5.7+ 开启并行复制（slave_parallel_workers > 0）
#          MySQL 8.0 默认开启并行复制

# 4. 从库跑大查询
#    原因：从库上跑复杂查询占用资源，影响复制线程
#    解决：分析查询走专门的分析从库，或限制查询资源

# 5. 网络延迟
#    原因：主从跨机房，网络带宽不足
#    解决：主从同机房部署，或增加带宽

# 半同步复制（Semi-Sync）：
#   主库提交事务后，至少等待一个从库确认收到 binlog 才返回成功
#   保证主从数据一致性（牺牲一点性能）
#   配置：rpl_semi_sync_master_enabled=1（主库）
#         rpl_semi_sync_slave_enabled=1（从库）
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 主从 server-id 相同 | 复制异常或从库不工作 | 每个实例 server-id 必须唯一 |
| 从库不设只读 | 业务误写从库，主从数据不一致 | 从库设 read_only=1 和 super_read_only=1 |
| binlog 用 STATEMENT 格式 | 不确定性函数导致主从不一致 | 用 ROW 格式（默认推荐） |
| 读写分离后刚写就读不到 | 主从延迟导致读旧数据 | 关键查询强制走主库，或用半同步复制 |
| 从库挂了不监控 | 主库挂了无法切换，数据丢失 | 监控 Seconds_Behind_Master 和复制线程状态 |
| 大事务直接执行 | 主从延迟飙升，从库追不上 | 大事务拆成小批量分批执行 |

### 动手

1. 画一个 MySQL 主从复制的原理图，标注三个线程和数据流
2. 对比 STATEMENT 和 ROW 两种 binlog 格式，各举一个适用场景
3. 解释主从延迟的 3 个常见原因和对应的解决方案
""")

# ========== Python：面向对象 + 正则 + matplotlib ==========
leaf_oo = make_leaf("py-oop", "面向对象", "??", """### 课前

- **场景**：函数式编程写复杂项目时代码混乱、重复多，需要用面向对象组织代码。
- **目标**：掌握类与对象、属性与方法、继承、多态、封装、魔术方法，能设计合理的类结构。
- **先修**：Python 函数、数据结构

### 是什么

- **一句话定义**：面向对象编程（OOP）是一种以"对象"为核心的编程范式，将数据和操作数据的方法封装在一起，通过类定义对象的模板，通过继承和多态实现代码复用和扩展。
- **四大特性**：封装（Encapsulation）、继承（Inheritance）、多态（Polymorphism）、抽象（Abstraction）。

### 怎么写

```python
# ===== 1. 定义类和创建对象 =====
class Dog:
    # 类属性（所有对象共享）
    species = "犬科动物"
    
    # 构造方法（创建对象时自动调用）
    def __init__(self, name, age):
        # 实例属性（每个对象独有）
        self.name = name
        self.age = age
    
    # 实例方法
    def bark(self):
        print(f"{self.name} 在汪汪叫！")
    
    def get_info(self):
        return f"名字：{self.name}，年龄：{self.age}，物种：{self.species}"

# 创建对象
dog1 = Dog("旺财", 3)
dog2 = Dog("大黄", 5)

# 访问属性和方法
print(dog1.name)           # 旺财
dog1.bark()                 # 旺财 在汪汪叫！
print(dog2.get_info())      # 名字：大黄，年龄：5，物种：犬科动物

# ===== 2. 封装（私有属性和方法）=====
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance       # 单下划线：约定为私有（但仍可外部访问）
        self.__password = "123456"   # 双下划线：名称修饰，外部不能直接访问
    
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            print(f"存入 {amount}，余额 {self._balance}")
        else:
            print("存款金额必须大于0")
    
    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            print(f"取出 {amount}，余额 {self._balance}")
        else:
            print("取款金额无效或余额不足")
    
    def get_balance(self):
        return self._balance

account = BankAccount("张三", 1000)
account.deposit(500)       # 存入 500，余额 1500
account.withdraw(200)      # 取出 200，余额 1300
print(account.get_balance())  # 1300
# account.__password  # 报错，不能直接访问
# account._BankAccount__password  # 可以通过名称修饰访问（不推荐）

# ===== 3. 继承 =====
class Animal:
    def __init__(self, name):
        self.name = name
    
    def eat(self):
        print(f"{self.name} 在吃东西")
    
    def sleep(self):
        print(f"{self.name} 在睡觉")

class Cat(Animal):  # 继承 Animal
    def __init__(self, name, color):
        super().__init__(name)  # 调用父类构造方法
        self.color = color
    
    def meow(self):
        print(f"{self.name} 在喵喵叫")
    
    # 重写父类方法
    def eat(self):
        print(f"{self.name}（{self.color}）在吃鱼")

cat = Cat("咪咪", "橘色")
cat.eat()       # 咪咪（橘色）在吃鱼（重写后的方法）
cat.sleep()     # 咪咪 在睡觉（继承的方法）
cat.meow()      # 咪咪 在喵喵叫（子类自己的方法）

# 多继承
class A:
    def method_a(self):
        print("A 的方法")

class B:
    def method_b(self):
        print("B 的方法")

class C(A, B):  # 同时继承 A 和 B
    pass

c = C()
c.method_a()  # A 的方法
c.method_b()  # B 的方法

# ===== 4. 多态 =====
class Shape:
    def area(self):
        pass  # 抽象方法，子类必须实现

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

# 多态：不同对象调用同名方法，产生不同结果
shapes = [Circle(5), Rectangle(3, 4), Circle(2)]
for shape in shapes:
    print(f"面积：{shape.area()}")
# 面积：78.5
# 面积：12
# 面积：12.56

# ===== 5. 常用魔术方法 =====
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):  # print() 时调用
        return f"Point({self.x}, {self.y})"
    
    def __repr__(self):  # 交互式环境显示
        return f"Point(x={self.x}, y={self.y})"
    
    def __eq__(self, other):  # == 比较
        return self.x == other.x and self.y == other.y
    
    def __add__(self, other):  # + 运算
        return Point(self.x + other.x, self.y + other.y)
    
    def __len__(self):  # len() 调用
        return 2  # 二维点

p1 = Point(1, 2)
p2 = Point(3, 4)
print(p1)              # Point(1, 2)
print(p1 == Point(1, 2))  # True
print(p1 + p2)         # Point(4, 6)
print(len(p1))         # 2
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 方法忘记写 self | 调用时报参数错误 | 所有实例方法第一个参数必须是 self |
| 子类构造方法不调用 super().__init__() | 父类属性未初始化 | 子类 __init__ 中先调用 super().__init__() |
| 用双下划线属性以为绝对安全 | 仍可通过名称修饰访问 | 双下划线只是名称修饰，不是真正的私有，靠约定 |
| 多继承时方法冲突 | 不知道调用哪个父类的方法 | 理解 MRO（方法解析顺序），用 super() 按 MRO 调用 |
| 类属性和实例属性混淆 | 修改类属性影响所有对象 | 可变类属性（列表/字典）修改会影响所有对象，注意 |
| 过度使用面向对象 | 简单任务也写一堆类，代码复杂 | 简单脚本用函数式，复杂项目用面向对象，按需选择 |

### 动手

1. 设计一个学生管理系统的类结构：Person 类（name/age）→ Student 类（继承Person，加 student_id/grades）→ Course 类，实现学生选课和成绩查询
2. 给上面的类添加 __str__ 方法和相等比较（学号相同则相等）
3. 写一句「什么时候用面向对象，什么时候用函数式编程」
""")

leaf_regex = make_leaf("py-regex", "正则表达式", "??", """### 课前

- **场景**：需要从文本中提取手机号、邮箱、验证输入格式、批量替换字符串，普通字符串方法不够用。
- **目标**：掌握 Python re 模块的常用方法、正则语法（元字符/量词/分组/断言）、常见正则模式。
- **先修**：Python 字符串操作

### 是什么

- **一句话定义**：正则表达式（Regular Expression，regex）是一种用特殊语法描述字符串模式的工具，可以高效地完成字符串的匹配、提取、替换、分割，是文本处理的利器。
- Python 模块：`re`（标准库，无需安装）。

### 怎么写

```python
import re

# ===== 1. 常用方法 =====

# match：从字符串开头匹配（只匹配开头）
result = re.match(r"hello", "hello world")
print(result.group())  # hello
result = re.match(r"world", "hello world")
print(result)  # None（开头不是world）

# search：搜索整个字符串，找到第一个匹配
result = re.search(r"world", "hello world")
print(result.group())  # world

# findall：找到所有匹配，返回列表
text = "电话：13800138000，备用：13900139000"
phones = re.findall(r"1\d{10}", text)
print(phones)  # ['13800138000', '13900139000']

# finditer：找到所有匹配，返回迭代器（节省内存）
for match in re.finditer(r"1\d{10}", text):
    print(f"找到：{match.group()}，位置：{match.start()}-{match.end()}")

# sub：替换
text = "我的邮箱是 test@example.com"
new_text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", 
                  "***@***.com", text)
print(new_text)  # 我的邮箱是 ***@***.com

# split：按正则分割
text = "a,b;c d\te"
parts = re.split(r"[,;\s]+", text)
print(parts)  # ['a', 'b', 'c', 'd', 'e']

# compile：预编译正则（多次使用时性能更好）
pattern = re.compile(r"1\d{10}")
result = pattern.findall(text)  # 等价于 re.findall(pattern, text)

# ===== 2. 基础语法 =====

# 元字符
# .   匹配任意字符（除换行符）
# ^   匹配字符串开头
# $   匹配字符串结尾
# *   匹配前一个字符 0 次或多次
# +   匹配前一个字符 1 次或多次
# ?   匹配前一个字符 0 次或 1 次
# {n} 匹配前一个字符恰好 n 次
# {n,m} 匹配前一个字符 n 到 m 次
# []  字符集，匹配其中任意一个
# |   或，匹配左边或右边
# ()  分组，提取匹配内容

# 字符类
# \d  数字 [0-9]
# \D  非数字
# \w  单词字符 [a-zA-Z0-9_]
# \W  非单词字符
# \s  空白字符（空格、制表符、换行等）
# \S  非空白字符
# \b  单词边界

# ===== 3. 分组与提取 =====
text = "2024-01-15"
match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
if match:
    print(match.group(0))  # 2024-01-15（整个匹配）
    print(match.group(1))  # 2024（第一个分组）
    print(match.group(2))  # 01（第二个分组）
    print(match.group(3))  # 15（第三个分组）
    print(match.groups())  # ('2024', '01', '15')（所有分组）

# 命名分组
match = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", text)
print(match.group("year"))   # 2024
print(match.groupdict())      # {'year': '2024', 'month': '01', 'day': '15'}

# ===== 4. 常用正则模式 =====

# 手机号
phone_pattern = r"1[3-9]\d{9}"
# 邮箱
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# 身份证号（18位）
id_pattern = r"[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]"
# URL
url_pattern = r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[^\s]*)?"
# IP地址
ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
# 中文字符
chinese_pattern = r"[\u4e00-\u9fa5]+"
# 日期 YYYY-MM-DD
date_pattern = r"\d{4}-\d{2}-\d{2}"

# ===== 5. 实际应用示例 =====

# 验证手机号格式
def is_valid_phone(phone):
    return bool(re.match(r"^1[3-9]\d{9}$", phone))

print(is_valid_phone("13800138000"))  # True
print(is_valid_phone("12345"))          # False

# 提取文本中所有邮箱
text = "联系我们：sales@company.com 或 support@company.com，也可访问官网"
emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
print(emails)  # ['sales@company.com', 'support@company.com']

# 敏感信息脱敏
text = "手机号：13800138000，身份证：110101199001011234"
# 手机号中间4位脱敏
text = re.sub(r"(1\d{2})\d{4}(\d{4})", r"\1****\2", text)
# 身份证中间10位脱敏
text = re.sub(r"(\d{4})\d{10}(\d{4})", r"\1**********\2", text)
print(text)  # 手机号：138****8000，身份证：1101**********1234
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 正则字符串不用 raw string（r""） | 反斜杠转义混乱，\d 变成 d | 正则都用 r"" 原始字符串 |
| 用 match 而不是 search | 不在开头的匹配不到 | match 只匹配开头，search 搜索整个字符串 |
| . 以为能匹配换行 | 跨行文本匹配不到 | 用 re.DOTALL 标志，或用 [\s\S] 代替 . |
| 量词默认贪婪匹配 | 匹配到最长的而不是期望的 | 量词后加 ? 变成非贪婪：*?、+?、?? |
| 分组太多记不住编号 | group(3) 不知道是哪个 | 用命名分组 (?P<name>...)，用 group("name") 提取 |
| 正则写得太复杂 | 难以维护和调试 | 复杂正则拆成多个简单正则，或用注释模式 re.VERBOSE |
| 不预编译多次使用的正则 | 性能差 | 多次使用的正则用 re.compile() 预编译 |

### 动手

1. 写一个函数验证邮箱格式是否正确（用正则）
2. 从一段文本中提取所有手机号和邮箱
3. 写一个正则把文本中的日期格式从 YYYY/MM/DD 替换为 YYYY-MM-DD
""")

leaf_matplotlib = make_leaf("py-matplotlib", "matplotlib 可视化", "??", """### 课前

- **场景**：数据分析结果需要用图表展示，matplotlib 是 Python 最基础的绘图库。
- **目标**：掌握 matplotlib 的基本用法（折线图/柱状图/散点图/饼图/直方图）、子图布局、样式美化、中文显示。
- **先修**：Python 基础、numpy/pandas

### 是什么

- **一句话定义**：matplotlib 是 Python 最基础、最流行的 2D 绘图库，提供了类似 MATLAB 的绘图接口，可以绘制折线图、柱状图、散点图、饼图、直方图等各种统计图表，是数据可视化的基础工具。
- 常用子模块：`matplotlib.pyplot`（简写为 plt）。

### 怎么写

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ===== 中文显示配置（必须，否则中文乱码）=====
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False  # 负号正常显示

# ===== 1. 折线图 =====
months = ["1月", "2月", "3月", "4月", "5月", "6月"]
sales = [120, 150, 135, 180, 165, 200]
profit = [30, 45, 35, 55, 50, 65]

plt.figure(figsize=(10, 6))  # 设置画布大小
plt.plot(months, sales, marker="o", linewidth=2, label="销售额")
plt.plot(months, profit, marker="s", linewidth=2, label="利润")
plt.title("上半年销售趋势", fontsize=16)
plt.xlabel("月份", fontsize=12)
plt.ylabel("金额（万元）", fontsize=12)
plt.legend(fontsize=12)  # 显示图例
plt.grid(True, alpha=0.3)  # 网格线
plt.tight_layout()  # 自动调整布局
plt.show()

# ===== 2. 柱状图 =====
categories = ["电子产品", "服装", "食品", "家居", "图书"]
sales_2023 = [450, 320, 280, 200, 150]
sales_2024 = [520, 350, 310, 230, 170]

x = np.arange(len(categories))
width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, sales_2023, width, label="2023年", color="#4A90D9")
plt.bar(x + width/2, sales_2024, width, label="2024年", color="#E74C3C")
plt.xticks(x, categories)
plt.title("各品类销售额对比", fontsize=16)
plt.ylabel("销售额（万元）", fontsize=12)
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# ===== 3. 散点图 =====
np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5
sizes = np.random.randint(50, 200, 100)
colors = np.random.rand(100)

plt.figure(figsize=(10, 6))
scatter = plt.scatter(x, y, s=sizes, c=colors, cmap="viridis", alpha=0.7)
plt.colorbar(scatter, label="数值")
plt.title("散点图示例", fontsize=16)
plt.xlabel("X 轴", fontsize=12)
plt.ylabel("Y 轴", fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ===== 4. 饼图 =====
labels = ["电子产品", "服装", "食品", "家居", "图书"]
sizes = [35, 25, 20, 12, 8]
colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
explode = (0.1, 0, 0, 0, 0)  # 突出显示第一块

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct="%1.1f%%", shadow=True, startangle=90)
plt.title("销售品类占比", fontsize=16)
plt.axis("equal")  # 保证饼图是圆形
plt.tight_layout()
plt.show()

# ===== 5. 直方图 =====
data = np.random.randn(1000)  # 1000个正态分布随机数

plt.figure(figsize=(10, 6))
plt.hist(data, bins=30, color="#4A90D9", edgecolor="white", alpha=0.8)
plt.title("数据分布直方图", fontsize=16)
plt.xlabel("数值", fontsize=12)
plt.ylabel("频数", fontsize=12)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# ===== 6. 子图布局 =====
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("多子图组合", fontsize=18)

# 子图1：折线图
axes[0, 0].plot(months, sales, marker="o")
axes[0, 0].set_title("销售趋势")
axes[0, 0].grid(True, alpha=0.3)

# 子图2：柱状图
axes[0, 1].bar(categories, sales_2023, color="#4A90D9")
axes[0, 1].set_title("品类销售")
axes[0, 1].tick_params(axis="x", rotation=45)

# 子图3：散点图
axes[1, 0].scatter(x, y, alpha=0.6)
axes[1, 0].set_title("散点图")
axes[1, 0].grid(True, alpha=0.3)

# 子图4：饼图
axes[1, 1].pie(sizes, labels=labels, autopct="%1.0f%%")
axes[1, 1].set_title("占比")

plt.tight_layout()
plt.show()

# ===== 7. 保存图片 =====
plt.figure(figsize=(10, 6))
plt.plot(months, sales, marker="o")
plt.title("销售趋势")
plt.savefig("sales_trend.png", dpi=300, bbox_inches="tight")
# dpi=300：高清分辨率
# bbox_inches="tight"：自动裁剪空白边缘
plt.close()
```

### 常用图表选择

| 图表类型 | 适用场景 | 函数 |
|---|---|---|
| 折线图 | 时间趋势、变化 | plt.plot() |
| 柱状图 | 类别对比、排名 | plt.bar() |
| 条形图 | 类别名称长、横向对比 | plt.barh() |
| 散点图 | 相关性、分布 | plt.scatter() |
| 饼图 | 占比构成（类别少） | plt.pie() |
| 直方图 | 数据分布 | plt.hist() |
| 箱线图 | 数据分布、异常值 | plt.boxplot() |
| 热力图 | 矩阵数据、密度 | plt.imshow() |
| 面积图 | 累计趋势 | plt.stackplot() |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 不配置中文字体 | 中文显示为方框 | plt.rcParams["font.sans-serif"] 设置中文字体 |
| 负号显示为方框 | 坐标轴负号乱码 | plt.rcParams["axes.unicode_minus"] = False |
| 不调用 plt.show() | 图表不显示 | 脚本中必须调用 plt.show() 才会显示 |
| 多个图共用一个 figure | 图表叠加在一起 | 每个图用 plt.figure() 新建，或用 plt.subplot 子图 |
| 保存图片前调用 plt.show() | 保存的图片是空白 | 先 savefig 再 show，或 savefig 后 close |
| 饼图类别太多 | 看不清、颜色难区分 | 超过5个类别用柱状图，或合并小类别 |
| 不设置 figsize | 图表太小或比例不对 | plt.figure(figsize=(宽, 高)) 设置合适大小 |

### 动手

1. 用 matplotlib 画一个包含 4 个子图的组合图（折线图+柱状图+散点图+饼图）
2. 画一个双 Y 轴折线图（左轴销售额，右轴增长率）
3. 把画好的图表保存为 300dpi 的 PNG 图片
""")

# ========== BI：可视化原则 ==========
leaf_viz_principles = make_leaf("bi-viz-principles", "可视化设计原则", "??", """### 课前

- **场景**：做出来的报表不好看、业务方看不懂、重点不突出，需要掌握可视化设计原则。
- **目标**：掌握数据可视化的核心原则（数据墨水比、图表选择、配色、布局、叙事），避免常见可视化错误。
- **先修**：BI 基础、常用图表

### 是什么

- **一句话定义**：可视化设计原则是指导数据图表设计的规范和最佳实践，目标是让数据清晰、准确、高效地传达信息，避免误导和视觉干扰，核心是"让数据说话"。
- **经典理论**：Edward Tufte 的《定量信息的视觉显示》提出的数据墨水比、图表垃圾、Lie Factor 等概念。

### 核心原则

```text
# ===== 原则1：数据墨水比最大化 =====
# 数据墨水：图表中用于展示数据的墨水（柱子、折线、数据点）
# 非数据墨水：装饰性元素（3D效果、阴影、网格线、背景色）
# 目标：在不影响理解的前提下，最大化数据墨水比例

# 应该去掉的"图表垃圾"：
# - 3D 效果（除非真的需要展示三维数据）
# - 过度的阴影和渐变
# - 不必要的网格线（或用浅色细线）
# - 花哨的背景图案
# - 重复的数据标签（柱子上已经标了数字，Y轴就不需要那么密）

# 反例：3D 饼图、带阴影的柱状图、深色背景+亮色网格
# 正例：简洁的平面图表、浅色细网格、白色背景
```

```text
# ===== 原则2：选择正确的图表类型 =====
# 图表类型取决于你想展示什么关系：

# 比较（Comparison）：
#   - 类别对比 → 柱状图/条形图
#   - 时间趋势 → 折线图
#   - 排名 → 条形图（横向，按值排序）
#   - 部分与整体 → 饼图（类别少）/ 堆叠柱状图

# 分布（Distribution）：
#   - 单变量分布 → 直方图/箱线图
#   - 双变量关系 → 散点图
#   - 多变量分布 → 热力图/平行坐标

# 构成（Composition）：
#   - 静态占比 → 饼图/环形图
#   - 随时间变化的构成 → 堆叠面积图/堆叠柱状图

# 关系（Relationship）：
#   - 两个变量相关性 → 散点图
#   - 三个变量 → 气泡图（大小表示第三维）
#   - 流程/流向 → 桑基图/漏斗图

# 常见错误：
# - 用饼图展示超过5个类别 → 改用条形图
# - 用折线图展示类别对比（没有时间顺序）→ 改用柱状图
# - 用3D柱状图 → 改用2D，3D会扭曲数值感知
# - 用双轴图不说明 → 必须明确标注左右轴分别是什么
```

```text
# ===== 原则3：配色要专业、有意义 =====
# 配色原则：
# 1. 同一类别在不同图表中颜色一致
# 2. 顺序数据用渐变色（从浅到深表示从小到大）
# 3. 分类数据用区分度高的颜色（不要用相近色）
# 4. 突出重点用强调色，其他用中性色（灰色）
# 5. 考虑色盲友好（红绿色盲是最常见的，避免红绿对比）
# 6. 不要用彩虹色（rainbow），颜色顺序没有数值含义

# 常用配色方案：
# - 商务蓝：#1f77b4, #ff7f0e, #2ca02c, #d62728, #9467bd
# - Tableau 10 色：专业、区分度高
# - 单色渐变：#deebf7 → #08519c（蓝色系，适合顺序数据）
# - 发散色：#d73027（红）→ #ffffbf（黄）→ #1a9850（绿）（适合正负值）

# 强调技巧：
#   所有柱子灰色，只有要强调的柱子用红色/蓝色
#   所有折线灰色，只有要强调的折线用亮色加粗
```

```text
# ===== 原则4：布局要有层次、有重点 =====
# 布局原则：
# 1. 核心 KPI 放最上方、最显眼的位置
# 2. 相关图表放在一起，形成逻辑分组
# 3. 从概览到明细，从上到下、从左到右
# 4. 适当留白，不要太拥挤
# 5. 对齐：图表边缘对齐，大小一致
# 6. 标题清晰：每个图表有明确的标题，说明展示什么

# 经典仪表盘布局：
#   ┌─────────────────────────────────────┐
#   │  KPI卡片1  │  KPI卡片2  │  KPI卡片3  │  ← 核心指标
#   ├─────────────────────────────────────┤
#   │  趋势折线图（宽）     │  品类柱状图  │  ← 主要分析
#   ├─────────────────────────────────────┤
#   │  区域地图  │  渠道饼图  │  明细表格  │  ← 细分维度
#   └─────────────────────────────────────┘
```

```text
# ===== 原则5：用数据讲故事（Data Storytelling）=====
# 好的可视化不只是展示数据，而是讲述一个故事：
# 1. 背景：当前业务状况是什么？
# 2. 发现：数据揭示了什么问题/机会？
# 3. 洞察：为什么会这样？根本原因是什么？
# 4. 建议：应该采取什么行动？

# 叙事技巧：
# - 用标题传达洞察，而不是描述图表类型
#   差标题："2024年各月销售额"
#   好标题："2024年销售额稳步增长，Q4突破历史新高"
# - 用注释标注关键数据点（异常值、转折点、目标达成）
# - 用颜色引导视线（重点数据用强调色）
# - 按逻辑顺序排列图表（先整体后局部，先原因后结果）
```

### 常见可视化错误

| 错误 | 问题 | 纠正 |
|---|---|---|
| Y轴不从0开始 | 夸大差异，误导读者 | 柱状图Y轴必须从0开始；折线图可以截断但要标注 |
| 饼图类别太多 | 看不清，颜色难区分 | 超过5个类别用条形图，小类别合并为"其他" |
| 3D图表 | 扭曲数值，难以比较 | 用2D图表，3D只在真正三维数据时用 |
| 双Y轴不标注 | 读者不知道左右轴是什么 | 明确标注左右轴的含义和单位 |
| 颜色没有意义 | 随机配色，无法传达信息 | 用颜色编码数据维度（类别/顺序/强调） |
| 数据标签过多 | 图表拥挤，看不清 | 只标注关键数据点，或用鼠标悬停显示 |
| 图表没有标题 | 读者不知道在看什么 | 每个图表有清晰标题，最好传达洞察 |
| 截断Y轴不标注 | 误导，以为差异很大 | 截断Y轴必须明确标注（如用//符号或文字说明） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 为了好看加很多装饰 | 数据被淹没，重点不突出 | 遵循数据墨水比，去掉不必要的装饰 |
| 所有图表用一样的颜色 | 无法区分类别，也没有重点 | 分类用不同颜色，重点用强调色 |
| 仪表盘塞太多图表 | 拥挤，找不到重点 | 一个仪表盘5-8个图表足够，核心KPI放大 |
| 标题只写图表类型 | 没有洞察，业务方不关心 | 标题写结论和洞察，如"销售额同比增长20%" |
| 不考虑色盲用户 | 红绿对比色盲用户分不清 | 用色盲友好配色，或加形状/纹理区分 |
| 图表比例不对 | 圆形变椭圆，柱状图比例失调 | 用合适的figsize，饼图用axis("equal") |

### 动手

1. 找一个你觉得不好看的图表，用可视化原则分析它的问题并给出改进方案
2. 设计一个销售仪表盘的布局（KPI卡片+趋势图+品类对比+区域分布），标注每个区域放什么
3. 写一句「数据墨水比」的含义，并举一个增加数据墨水比的例子
""")

# ========== SQL：DISTINCT + 字符串函数 ==========
leaf_distinct = make_leaf("sql-distinct", "DISTINCT 去重", "?", """### 课前

- **场景**：查询结果有重复行，需要去重；或者需要统计不重复的数量。
- **目标**：掌握 DISTINCT 的用法、多列去重、DISTINCT 与 GROUP BY 的区别、COUNT(DISTINCT)。
- **先修**：SELECT 基础

### 是什么

- **一句话定义**：DISTINCT 用于去除查询结果中的重复行，只保留唯一值，常用于查看有哪些不同的取值、统计不重复数量。

### 怎么写

```sql
-- 样例表：orders
-- order_id | user_id | product | amount | order_date
-- 1        | 101     | 手机    | 3000   | 2024-01-15
-- 2        | 102     | 电脑    | 5000   | 2024-01-16
-- 3        | 101     | 耳机    | 200    | 2024-01-17
-- 4        | 103     | 手机    | 3000   | 2024-01-18
-- 5        | 102     | 手机    | 3000   | 2024-01-19

-- 1. 单列去重：查看有哪些不同的产品
SELECT DISTINCT product FROM orders;
-- 结果：手机、电脑、耳机（去掉重复的"手机"）

-- 2. 多列去重：查看有哪些不同的 (用户, 产品) 组合
SELECT DISTINCT user_id, product FROM orders;
-- 结果：
-- 101 | 手机
-- 102 | 电脑
-- 101 | 耳机
-- 103 | 手机
-- 102 | 手机
-- 注意：是两列的组合去重，不是每列单独去重

-- 3. COUNT(DISTINCT)：统计不重复的数量
SELECT COUNT(DISTINCT user_id) AS unique_users FROM orders;
-- 结果：3（用户101、102、103，共3个不同用户）

SELECT COUNT(DISTINCT product) AS unique_products FROM orders;
-- 结果：3（手机、电脑、耳机）

-- 多列不重复计数（部分数据库支持，如 MySQL 不支持直接 COUNT(DISTINCT a,b)）
-- MySQL 写法：
SELECT COUNT(*) FROM (SELECT DISTINCT user_id, product FROM orders) t;
-- PostgreSQL 支持：
SELECT COUNT(DISTINCT (user_id, product)) FROM orders;

-- 4. DISTINCT 与 GROUP BY 的区别
-- 效果相同：
SELECT DISTINCT product FROM orders;
SELECT product FROM orders GROUP BY product;
-- 两者都返回不重复的 product 列表

-- 但 GROUP BY 可以配合聚合函数：
SELECT product, COUNT(*) AS order_count, SUM(amount) AS total_amount
FROM orders
GROUP BY product;
-- 结果：
-- 手机 | 3 | 9000
-- 电脑 | 1 | 5000
-- 耳机 | 1 | 200

-- 5. DISTINCT 在聚合函数中的使用
SELECT 
  COUNT(*) AS total_orders,
  COUNT(DISTINCT user_id) AS unique_users,
  COUNT(DISTINCT product) AS unique_products,
  AVG(DISTINCT amount) AS avg_distinct_amount  -- 对不重复的金额求平均（少用）
FROM orders;

-- 6. DISTINCT 对 NULL 的处理
-- DISTINCT 认为所有 NULL 是相同的，只保留一个
SELECT DISTINCT nullable_column FROM table;
-- 如果有多个 NULL，结果只显示一个 NULL

-- 7. 性能注意
-- DISTINCT 需要排序或哈希去重，大数据量时性能开销大
-- 优化：
-- - 尽量在 WHERE 中先过滤，减少需要去重的数据量
-- - 对去重列建索引
-- - 大数据量去重可以考虑用 GROUP BY（某些数据库优化器处理不同）
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 以为 DISTINCT 作用于紧跟的一列 | SELECT DISTINCT a, b 以为只对 a 去重 | DISTINCT 作用于所有列，是组合去重 |
| 用 DISTINCT 代替 GROUP BY 做统计 | 无法计算聚合值 | 需要聚合统计用 GROUP BY，只去重用 DISTINCT |
| COUNT(DISTINCT) 多列在 MySQL 报错 | 语法错误 | MySQL 用子查询：SELECT COUNT(*) FROM (SELECT DISTINCT a,b FROM t) t |
| 大表直接 DISTINCT 全表 | 查询慢 | 先 WHERE 过滤，对去重列建索引 |
| DISTINCT 和 ORDER BY 非选择列 | 某些数据库报错 | ORDER BY 的列必须在 SELECT 列表中（或用聚合） |

### 动手

1. 用 DISTINCT 查询订单表中有哪些不同的产品和用户
2. 用 COUNT(DISTINCT) 统计订单表中的不重复用户数和不重复产品数
3. 对比 DISTINCT 和 GROUP BY 的查询结果，说明什么时候用哪个
""")

leaf_string_funcs = make_leaf("sql-string-funcs", "字符串函数", "?", """### 课前

- **场景**：需要拼接字符串、截取子串、替换、大小写转换、计算长度、去除空格等字符串操作。
- **目标**：掌握 SQL 常用字符串函数（CONCAT/SUBSTRING/REPLACE/UPPER/LENGTH/TRIM 等），注意不同数据库的语法差异。
- **先修**：SELECT 基础

### 是什么

- **一句话定义**：SQL 字符串函数用于对文本类型的数据进行各种操作，包括拼接、截取、替换、转换、查找、格式化等，是数据清洗和处理的常用工具。

### 常用字符串函数

```sql
-- 样例数据
-- 'Hello World'
-- '  你好，世界  '
-- '2024-01-15'

-- ===== 1. 字符串拼接 =====
-- MySQL / PostgreSQL / SQL Server：
SELECT CONCAT('Hello', ' ', 'World');  -- 'Hello World'
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;

-- 拼接时处理 NULL（CONCAT 遇到 NULL 会返回 NULL）：
SELECT CONCAT(IFNULL(first_name, ''), ' ', IFNULL(last_name, '')) FROM users;
-- 或用 CONCAT_WS（指定分隔符，自动跳过 NULL）：
SELECT CONCAT_WS(' ', first_name, last_name) FROM users;

-- Oracle 用 || 拼接：
-- SELECT first_name || ' ' || last_name FROM users;

-- ===== 2. 字符串长度 =====
-- MySQL：CHAR_LENGTH（字符数）、LENGTH（字节数）
SELECT CHAR_LENGTH('Hello');  -- 5
SELECT CHAR_LENGTH('你好');    -- 2（字符数）
SELECT LENGTH('你好');         -- 6（UTF-8下每个中文3字节）

-- PostgreSQL：LENGTH（字符数）、OCTET_LENGTH（字节数）
-- SQL Server：LEN（字符数）、DATALENGTH（字节数）
-- Oracle：LENGTH（字符数）

-- ===== 3. 大小写转换 =====
SELECT UPPER('hello');   -- 'HELLO'
SELECT LOWER('HELLO');   -- 'hello'
SELECT INITCAP('hello world');  -- 'Hello World'（PostgreSQL/Oracle，每个单词首字母大写）

-- ===== 4. 去除空格 =====
SELECT TRIM('  hello  ');    -- 'hello'（去首尾空格）
SELECT LTRIM('  hello');     -- 'hello'（去左边空格）
SELECT RTRIM('hello  ');     -- 'hello'（去右边空格）

-- 去除指定字符：
SELECT TRIM(LEADING '0' FROM '000123');  -- '123'（去前导0）
SELECT TRIM(TRAILING '-' FROM 'hello--'); -- 'hello'
SELECT TRIM(BOTH 'x' FROM 'xxhelloxx');   -- 'hello'

-- ===== 5. 截取子串 =====
-- SUBSTRING(string, start, length)
-- 注意：SQL 中字符串索引从 1 开始（不是 0！）
SELECT SUBSTRING('Hello World', 1, 5);   -- 'Hello'（从第1个字符开始，取5个）
SELECT SUBSTRING('Hello World', 7);       -- 'World'（从第7个字符开始到结尾）
SELECT SUBSTRING('Hello World', -5);      -- 'World'（负数从末尾数，MySQL支持）

-- 左截取/右截取：
SELECT LEFT('Hello World', 5);   -- 'Hello'
SELECT RIGHT('Hello World', 5);  -- 'World'

-- ===== 6. 查找子串位置 =====
-- INSTR / POSITION / CHARINDEX
SELECT INSTR('Hello World', 'World');   -- 7（MySQL，找到返回位置，没找到返回0）
SELECT POSITION('World' IN 'Hello World');  -- 7（PostgreSQL/SQL标准）
SELECT CHARINDEX('World', 'Hello World');  -- 7（SQL Server）

-- 从指定位置开始查找：
SELECT INSTR('Hello World Hello', 'Hello', 7);  -- 13（MySQL，从第7个字符开始找）

-- ===== 7. 替换 =====
SELECT REPLACE('Hello World', 'World', 'SQL');  -- 'Hello SQL'
SELECT REPLACE('2024-01-15', '-', '/');          -- '2024/01/15'

-- 正则替换（MySQL 8.0+ / PostgreSQL）：
SELECT REGEXP_REPLACE('电话：13800138000', '[0-9]', '*');  -- '电话：***********'

-- ===== 8. 填充 =====
-- LPAD / RPAD：左填充/右填充到指定长度
SELECT LPAD('123', 6, '0');   -- '000123'（左边补0到6位）
SELECT RPAD('abc', 6, '-');   -- 'abc---'（右边补-到6位）

-- 应用：编号格式化
SELECT LPAD(order_id, 8, '0') AS formatted_id FROM orders;
-- 1 → '00000001'

-- ===== 9. 反转 =====
SELECT REVERSE('Hello');  -- 'olleH'

-- ===== 10. 字符串分割（按分隔符）=====
-- MySQL：SUBSTRING_INDEX
SELECT SUBSTRING_INDEX('a,b,c,d', ',', 2);   -- 'a,b'（取前2个元素）
SELECT SUBSTRING_INDEX('a,b,c,d', ',', -1);  -- 'd'（取最后1个元素）

-- PostgreSQL：SPLIT_PART
SELECT SPLIT_PART('a,b,c,d', ',', 2);  -- 'b'（取第2个元素）

-- ===== 11. 类型转换 =====
-- 字符串转数字/日期，数字/日期转字符串
SELECT CAST('123' AS SIGNED);          -- 123（字符串转整数）
SELECT CAST(123 AS CHAR);               -- '123'（数字转字符串）
SELECT CAST('2024-01-15' AS DATE);     -- 日期类型
SELECT CAST('2024-01-15 10:30:00' AS DATETIME);  -- 日期时间

-- MySQL 简写：
SELECT CONVERT('123', SIGNED);  -- 123
SELECT DATE('2024-01-15 10:30:00');  -- '2024-01-15'（提取日期部分）

-- ===== 12. 实际应用示例 =====

-- 姓名拼接：
SELECT CONCAT(last_name, first_name) AS full_name FROM employees;

-- 手机号脱敏：
SELECT CONCAT(LEFT(phone, 3), '****', RIGHT(phone, 4)) AS masked_phone FROM users;
-- 13800138000 → 138****8000

-- 邮箱提取域名：
SELECT SUBSTRING_INDEX(email, '@', -1) AS domain FROM users;
-- test@example.com → example.com

-- 日期格式化（字符串）：
SELECT DATE_FORMAT(NOW(), '%Y年%m月%d日');  -- '2024年01月15日'（MySQL）
SELECT TO_CHAR(NOW(), 'YYYY年MM月DD日');     -- PostgreSQL/Oracle

-- 去除字符串中的所有空格：
SELECT REPLACE('Hello World', ' ', '');  -- 'HelloWorld'
```

### 不同数据库语法差异

| 功能 | MySQL | PostgreSQL | SQL Server | Oracle |
|---|---|---|---|---|
| 拼接 | CONCAT() | CONCAT() / \|\| | CONCAT() / + | \|\| |
| 字符长度 | CHAR_LENGTH() | LENGTH() | LEN() | LENGTH() |
| 字节长度 | LENGTH() | OCTET_LENGTH() | DATALENGTH() | LENGTHB() |
| 截取 | SUBSTRING() | SUBSTRING() | SUBSTRING() | SUBSTR() |
| 查找位置 | INSTR() | POSITION() | CHARINDEX() | INSTR() |
| 分割 | SUBSTRING_INDEX() | SPLIT_PART() | 无内置 | SUBSTR()+INSTR() |
| 正则替换 | REGEXP_REPLACE() | REGEXP_REPLACE() | 无内置（用CLR） | REGEXP_REPLACE() |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 字符串索引用 0 开始 | 截取结果错位 | SQL 中字符串索引从 1 开始，SUBSTRING(s, 1, 3) 取前3个 |
| 用 LENGTH 计算中文字符数 | 结果偏大（按字节算） | 中文用 CHAR_LENGTH（MySQL）或 LENGTH（PostgreSQL） |
| CONCAT 遇到 NULL 返回 NULL | 拼接结果变成 NULL | 用 IFNULL/COALESCE 处理 NULL，或用 CONCAT_WS |
| 不同数据库函数名搞混 | 语法错误 | 注意 MySQL/PostgreSQL/SQL Server/Oracle 的函数差异 |
| 替换时大小写不匹配 | 替换不到 | REPLACE 默认大小写敏感，需要时先统一大小写 |
| LPAD/RPAD 长度小于原字符串 | 字符串被截断 | LPAD/RPAD 的长度参数是最终长度，小于原长会截断 |

### 动手

1. 写一个 SQL 把用户表中的手机号中间4位替换为 ****（如 138****8000）
2. 从邮箱地址中提取 @ 前面的用户名和 @ 后面的域名
3. 把日期字段格式化为 "YYYY年MM月DD日" 的字符串格式
""")

# ========== 执行所有补充 ==========
print("=" * 60)
print("开始综合补充")
print("=" * 60)

# --- ETL ---
etl_data = load_domain("etl")
etl_root = etl_data["children"]
if not any(c.get("id") == "etl-data-quality" for c in etl_root):
    etl_root.append(leaf_dq)
    print("✓ ETL: 数据质量已添加")
size = save_domain("etl", etl_data)
print(f"  embed-etl.js size: {size}")

# --- 数据库 ---
db_data = load_domain("database")
db_root = db_data["children"]
if not any(c.get("id") == "db-normalization" for c in db_root):
    db_root.append(leaf_normalization)
    print("✓ 数据库: 范式已添加")
if not any(c.get("id") == "db-replication" for c in db_root):
    db_root.append(leaf_replication)
    print("✓ 数据库: 主从复制已添加")
size = save_domain("database", db_data)
print(f"  embed-database.js size: {size}")

# --- Python ---
py_data = load_domain("python")
py_root = py_data["children"]
# 找到 Python 基础节点，添加面向对象和正则
py_basics = find_node(py_data, "py-basics")
if py_basics:
    if not any(c.get("id") == "py-oop" for c in py_basics["children"]):
        py_basics["children"].append(leaf_oo)
        print("✓ Python: 面向对象已添加到 Python 基础")
    if not any(c.get("id") == "py-regex" for c in py_basics["children"]):
        py_basics["children"].append(leaf_regex)
        print("✓ Python: 正则表达式已添加到 Python 基础")
# matplotlib 加到根节点
if not any(c.get("id") == "py-matplotlib" for c in py_root):
    py_root.append(leaf_matplotlib)
    print("✓ Python: matplotlib 已添加")
size = save_domain("python", py_data)
print(f"  embed-python.js size: {size}")

# --- BI ---
bi_data = load_domain("bi")
bi_root = bi_data["children"]
if not any(c.get("id") == "bi-viz-principles" for c in bi_root):
    bi_root.append(leaf_viz_principles)
    print("✓ BI: 可视化设计原则已添加")
size = save_domain("bi", bi_data)
print(f"  embed-bi.js size: {size}")

# --- SQL ---
sql_data = load_domain("sql")
sql_root = sql_data["children"]
# 找到基础查询节点，添加 DISTINCT 和字符串函数
# 先找一个合适的位置，直接加到根节点
if not any(c.get("id") == "sql-distinct" for c in sql_root):
    sql_root.append(leaf_distinct)
    print("✓ SQL: DISTINCT 去重已添加")
if not any(c.get("id") == "sql-string-funcs" for c in sql_root):
    sql_root.append(leaf_string_funcs)
    print("✓ SQL: 字符串函数已添加")
size = save_domain("sql", sql_data)
print(f"  embed-sql.js size: {size}")

print("\n" + "=" * 60)
print("综合补充完成！")
print("=" * 60)
