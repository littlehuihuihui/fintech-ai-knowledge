#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完善SQL窗口函数4个子节点，增加更多例子"""

import json, re

filepath = r"D:\cursor\数据学习平台\kg-data\embed-sql.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["sql"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def find_node(node, node_id):
    if node.get("id") == node_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result:
            return result
    return None

# ========== 1. 排名函数（大幅扩充例子） ==========
rank_content = '''### 课前

- **场景**：要给每个区域的销售额排名、取 Top N、给用户分位数分组、连续登录天数、去重取最新记录。
- **目标**：掌握 ROW_NUMBER、RANK、DENSE_RANK、NTILE 四个排名函数的区别和适用场景，能应对各种排名类业务需求。
- **先修**：窗口函数基础（OVER 语法）

### 是什么

- **一句话定义**：排名函数为分区内的每一行分配一个排名序号，不同函数处理并列值的方式不同，是数据分析中最常用的窗口函数。
- **四个函数对比**：
  - **ROW_NUMBER()**：唯一序号，即使值相同也强行排序（1,2,3,4...）
  - **RANK()**：并列排名，跳过后续序号（1,1,3,4...）
  - **DENSE_RANK()**：并列排名，不跳过序号（1,1,2,3...）
  - **NTILE(n)**：将分区内行平均分成 n 组，返回组号（1,2,3...n）

### 怎么写

```sql
-- ============================================================
-- 样例数据：员工销售额表
-- ============================================================
-- emp_id | dept   | sales | hire_date
-- 1      | 销售部 | 100   | 2023-01-15
-- 2      | 销售部 | 100   | 2023-03-20
-- 3      | 销售部 | 80    | 2023-02-10
-- 4      | 销售部 | 60    | 2023-06-01
-- 5      | 技术部 | 90    | 2023-04-05
-- 6      | 技术部 | 90    | 2023-05-12
-- 7      | 技术部 | 70    | 2023-01-20

-- ============================================================
-- 例1：ROW_NUMBER() —— 唯一序号（强行排序，无并列）
-- ============================================================
SELECT 
  emp_id, dept, sales,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY sales DESC) AS rn
FROM employees;
-- 销售部：100→1, 100→2, 80→3, 60→4（两个100强行排1和2）
-- 技术部：90→1, 90→2, 70→3

-- ============================================================
-- 例2：RANK() —— 并列排名，跳过后续序号
-- ============================================================
SELECT 
  emp_id, dept, sales,
  RANK() OVER (PARTITION BY dept ORDER BY sales DESC) AS rk
FROM employees;
-- 销售部：100→1, 100→1, 80→3, 60→4（两个并列第1，下一个直接第3）
-- 技术部：90→1, 90→1, 70→3

-- ============================================================
-- 例3：DENSE_RANK() —— 并列排名，不跳过序号（连续）
-- ============================================================
SELECT 
  emp_id, dept, sales,
  DENSE_RANK() OVER (PARTITION BY dept ORDER BY sales DESC) AS dr
FROM employees;
-- 销售部：100→1, 100→1, 80→2, 60→3（两个并列第1，下一个第2，连续）
-- 技术部：90→1, 90→1, 70→2

-- ============================================================
-- 例4：NTILE(n) —— 平均分成 n 组（分位数）
-- ============================================================
SELECT 
  emp_id, dept, sales,
  NTILE(2) OVER (PARTITION BY dept ORDER BY sales DESC) AS tile2,
  NTILE(4) OVER (ORDER BY sales DESC) AS tile4_all
FROM employees;
-- 销售部4人分2组：前2名→1，后2名→2
-- 全部7人分4组：尽量平均（2,2,2,1人），前几组多1个

-- ============================================================
-- 例5：取每个部门销售额 Top 2（最常用场景）
-- ============================================================
WITH ranked AS (
  SELECT 
    emp_id, dept, sales,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY sales DESC) AS rn
  FROM employees
)
SELECT * FROM ranked WHERE rn <= 2;
-- 每个部门取前2名（用 ROW_NUMBER 保证正好取2个，不会因为并列多取）

-- ============================================================
-- 例6：取前 10% 的员工（NTILE 分位数应用）
-- ============================================================
WITH tiled AS (
  SELECT 
    emp_id, dept, sales,
    NTILE(10) OVER (ORDER BY sales DESC) AS tile
  FROM employees
)
SELECT * FROM tiled WHERE tile = 1;
-- tile=1 就是前 10%（高绩效员工）

-- ============================================================
-- 例7：去重取最新记录（ROW_NUMBER 经典用法）
-- 场景：用户表有多次更新记录，取每个用户最新的一条
-- ============================================================
-- 样例：user_log 表
-- user_id | name  | updated_at
-- 1       | 张三  | 2024-01-01
-- 1       | 张三  | 2024-03-15  ← 最新
-- 2       | 李四  | 2024-02-10
-- 2       | 李四  | 2024-04-01  ← 最新

WITH dedup AS (
  SELECT 
    user_id, name, updated_at,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn
  FROM user_log
)
SELECT user_id, name, updated_at FROM dedup WHERE rn = 1;
-- 每个用户只保留最新一条记录（数据仓库拉链表去重常用）

-- ============================================================
-- 例8：连续登录天数（ROW_NUMBER 偏移法，经典面试题）
-- 场景：计算每个用户的连续登录天数
-- ============================================================
-- 样例：login 表（user_id, login_date）
-- 1 | 2024-01-01
-- 1 | 2024-01-02
-- 1 | 2024-01-03   ← 连续3天
-- 1 | 2024-01-05   ← 断了一天
-- 1 | 2024-01-06   ← 连续2天

WITH login_rn AS (
  SELECT 
    user_id, login_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
  FROM login
),
login_group AS (
  SELECT 
    user_id, login_date, rn,
    DATE_SUB(login_date, INTERVAL rn DAY) AS grp_date
    -- 连续日期减去行号会得到相同的日期（分组标识）
  FROM login_rn
)
SELECT 
  user_id,
  MIN(login_date) AS start_date,
  MAX(login_date) AS end_date,
  COUNT(*) AS consecutive_days
FROM login_group
GROUP BY user_id, grp_date
ORDER BY user_id, start_date;
-- 结果：
-- user 1: 2024-01-01 ~ 2024-01-03, 3天
-- user 1: 2024-01-05 ~ 2024-01-06, 2天

-- ============================================================
-- 例9：每个分数段的人数（DENSE_RANK 做分数段）
-- ============================================================
SELECT 
  emp_id, dept, sales,
  DENSE_RANK() OVER (ORDER BY 
    CASE 
      WHEN sales >= 100 THEN 'S'
      WHEN sales >= 80 THEN 'A'
      WHEN sales >= 60 THEN 'B'
      ELSE 'C'
    END DESC
  ) AS grade_rank
FROM employees;
-- 按销售额等级排名，同等级同排名

-- ============================================================
-- 例10：排名变化（环比排名升降，需要 LAG 配合）
-- ============================================================
-- 样例：月度销售排名
-- month | emp_id | sales
-- 01    | 1      | 100
-- 01    | 2      | 90
-- 02    | 1      | 80
-- 02    | 2      | 95

WITH monthly_rank AS (
  SELECT 
    month, emp_id, sales,
    RANK() OVER (PARTITION BY month ORDER BY sales DESC) AS rk
  FROM monthly_sales
)
SELECT 
  month, emp_id, sales, rk,
  LAG(rk) OVER (PARTITION BY emp_id ORDER BY month) AS prev_rk,
  LAG(rk) OVER (PARTITION BY emp_id ORDER BY month) - rk AS rank_change
FROM monthly_rank;
-- rank_change > 0：排名上升；< 0：排名下降；= 0：持平
```

### 四个函数对比表

| 函数 | 并列处理 | 序号特点 | 适用场景 |
|---|---|---|---|
| ROW_NUMBER | 强行排序，无并列 | 连续唯一 | Top N（正好取N个）、去重取第一条、连续登录 |
| RANK | 并列同排名，跳过后续 | 不连续（1,1,3） | 考试排名、竞赛排名（并列名次） |
| DENSE_RANK | 并列同排名，不跳过 | 连续（1,1,2） | 产品等级、分数段（名次连续） |
| NTILE(n) | 平均分组 | 组号1~n | 分位数、四分位、Top N%、用户分层 |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用 RANK() 取 Top N | 并列时可能多取（如 Top2 取出3条） | 正好取 N 条用 ROW_NUMBER()，需要包含并列用 RANK() + 子查询 |
| 忘记 PARTITION BY | 全局排名，不是分组排名 | 需要每个组内排名必须加 PARTITION BY |
| ORDER BY 方向搞反 | 排名顺序反了 | 降序排名用 DESC（高的排前面），升序用 ASC |
| NTILE 分组不均匀以为是 bug | NTILE 尽量平均，不能整除时前几组多1个 | 正常行为，前 (总数%n) 组多1个 |
| 排名函数里加 DISTINCT | 语法错误或结果意外 | 排名函数不支持 DISTINCT，先去重再排名 |
| WHERE 中直接用排名结果 | 语法错误（窗口函数在WHERE后执行） | 用 CTE/子查询包裹，外层过滤 |
| 连续登录用 RANK 而不是 ROW_NUMBER | 同一天多次登录会导致行号跳变 | 连续登录必须先去重同一天，再用 ROW_NUMBER |

### 动手

1. 用 ROW_NUMBER() 给每个区域的订单按金额降序排名，取每个区域 Top 3
2. 对比 RANK() 和 DENSE_RANK() 的结果，解释什么时候用哪个
3. 用 NTILE(4) 把用户按消费金额分成4组，统计每组的人数和平均消费
4. 实现"每个用户取最新一条记录"的去重逻辑（ROW_NUMBER 经典用法）
5. （进阶）实现连续登录天数计算（ROW_NUMBER 偏移法）
'''

# ========== 2. 聚合窗口（增加更多例子） ==========
agg_content = '''### 课前

- **场景**：要计算累计销售额、移动平均、每行占分区总计的比例、同环比、留存、分组占比，用 GROUP BY 会丢失明细行。
- **目标**：掌握 SUM/AVG/COUNT/MIN/MAX 配合 OVER 子句实现窗口聚合，包括累计、移动平均、占比、各种业务场景。
- **先修**：窗口函数基础、GROUP BY

### 是什么

- **一句话定义**：聚合窗口函数将聚合函数（SUM/AVG/COUNT 等）应用于窗口内的行集合，为每一行返回一个聚合值，同时保留明细行，解决了 GROUP BY 只能返回聚合行的限制。
- **核心能力**：累计求和（running total）、移动平均（moving average）、占比（ratio to total）、分区内统计、同环比基础。

### 怎么写

```sql
-- ============================================================
-- 样例：每日销售额表
-- ============================================================
-- date       | month | region | sales
-- 2024-01-01 | 01    | 华东   | 100
-- 2024-01-02 | 01    | 华东   | 150
-- 2024-01-03 | 01    | 华东   | 120
-- 2024-01-04 | 01    | 华东   | 200
-- 2024-01-05 | 01    | 华东   | 180

-- ============================================================
-- 例1：累计求和（Running Total）—— 从第一行到当前行的累计
-- ============================================================
SELECT 
  date, sales,
  SUM(sales) OVER (ORDER BY date) AS running_total
FROM daily_sales;
-- 结果：
-- 01-01 | 100 | 100
-- 01-02 | 150 | 250
-- 01-03 | 120 | 370
-- 01-04 | 200 | 570
-- 01-05 | 180 | 750

-- ============================================================
-- 例2：分区内累计 —— 每个月/每个区域内重新累计
-- ============================================================
SELECT 
  date, month, region, sales,
  SUM(sales) OVER (PARTITION BY month ORDER BY date) AS month_running,
  SUM(sales) OVER (PARTITION BY region ORDER BY date) AS region_running
FROM daily_sales;
-- 每个月从1号开始重新累计；每个区域独立累计

-- ============================================================
-- 例3：移动平均（Moving Average）—— 前 N 行到当前行的平均
-- ============================================================
SELECT 
  date, sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma3,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7
FROM daily_sales;
-- 3日移动平均（含当天和前2天）
-- 01-01 | 100 | 100（只有1天）
-- 01-02 | 150 | 125（2天平均）
-- 01-03 | 120 | 123.33（3天平均：(100+150+120)/3）
-- 01-04 | 200 | 156.67（(150+120+200)/3）
-- 01-05 | 180 | 166.67（(120+200+180)/3）

-- ============================================================
-- 例4：中心移动平均 —— 前后各 N 行（平滑曲线常用）
-- ============================================================
SELECT 
  date, sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS centered_ma3
FROM daily_sales;
-- 中心3日平均（前1天+当天+后1天）
-- 01-02 | 150 | (100+150+120)/3 = 123.33

-- ============================================================
-- 例5：占比（Ratio to Total）—— 每行占分区总计的百分比
-- ============================================================
SELECT 
  date, sales,
  SUM(sales) OVER () AS total,
  ROUND(sales * 100.0 / NULLIF(SUM(sales) OVER (), 0), 2) AS pct
FROM daily_sales;
-- 总计 750，每行占比：
-- 01-01 | 100 | 750 | 13.33%
-- 01-02 | 150 | 750 | 20.00%

-- ============================================================
-- 例6：分区内占比 —— 每个区域内的占比（双层占比）
-- ============================================================
SELECT 
  region, date, sales,
  SUM(sales) OVER (PARTITION BY region) AS region_total,
  ROUND(sales * 100.0 / NULLIF(SUM(sales) OVER (PARTITION BY region), 0), 2) AS region_pct,
  SUM(sales) OVER () AS grand_total,
  ROUND(sales * 100.0 / NULLIF(SUM(sales) OVER (), 0), 2) AS grand_pct
FROM daily_sales;
-- 同时计算"占区域比例"和"占全局比例"

-- ============================================================
-- 例7：计数窗口 —— 分区内总行数、累计行数
-- ============================================================
SELECT 
  date, sales,
  COUNT(*) OVER (PARTITION BY month) AS month_days,
  COUNT(*) OVER (ORDER BY date) AS running_count
FROM daily_sales;
-- month_days：当月有多少天（每行都显示）
-- running_count：到当天为止累计多少天

-- ============================================================
-- 例8：窗口内最大/最小值 —— 到当前行为止的历史最高/最低
-- ============================================================
SELECT 
  date, sales,
  MAX(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS max_so_far,
  MIN(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS min_so_far,
  -- 创新高标记
  CASE WHEN sales = MAX(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) 
       THEN '创新高' ELSE '' END AS is_new_high
FROM daily_sales;
-- max_so_far：到当天为止的历史最高销售额
-- is_new_high：当天是否创了历史新高（股票分析常用）

-- ============================================================
-- 例9：综合应用 —— 每日销售额占当月累计的比例
-- ============================================================
SELECT 
  date, month, sales,
  SUM(sales) OVER (PARTITION BY month ORDER BY date) AS month_running,
  SUM(sales) OVER (PARTITION BY month) AS month_total,
  ROUND(SUM(sales) OVER (PARTITION BY month ORDER BY date) * 100.0 
        / NULLIF(SUM(sales) OVER (PARTITION BY month), 0), 2) AS pct_of_month
FROM daily_sales;
-- 可以看"到月中为止完成了当月目标的百分之多少"

-- ============================================================
-- 例10：分组排名占比 —— 每个区域内的销售额排名及占比
-- ============================================================
SELECT 
  region, date, sales,
  ROW_NUMBER() OVER (PARTITION BY region ORDER BY sales DESC) AS rn,
  SUM(sales) OVER (PARTITION BY region) AS region_total,
  ROUND(sales * 100.0 / NULLIF(SUM(sales) OVER (PARTITION BY region), 0), 2) AS pct
FROM daily_sales
ORDER BY region, rn;

-- ============================================================
-- 例11：累计占比（帕累托分析基础）—— 累计销售额占总销售额比例
-- ============================================================
SELECT 
  date, sales,
  SUM(sales) OVER (ORDER BY date) AS running_total,
  SUM(sales) OVER () AS grand_total,
  ROUND(SUM(sales) OVER (ORDER BY date) * 100.0 
        / NULLIF(SUM(sales) OVER (), 0), 2) AS running_pct
FROM daily_sales
ORDER BY date;
-- 可以看到"前N天贡献了总销售额的百分之多少"（帕累托/80-20分析）

-- ============================================================
-- 例12：标准差窗口 —— 计算移动标准差（波动分析）
-- ============================================================
SELECT 
  date, sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7,
  STDDEV(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS std7
FROM daily_sales;
-- 7日移动平均 + 7日移动标准差（股票波动率分析常用）
```

### 窗口帧（Window Frame）详解

```sql
-- 聚合窗口函数的关键：窗口帧定义（ROWS/RANGE BETWEEN ... AND ...）

-- 语法：
-- AGG_FUNC(col) OVER (
--   [PARTITION BY col]
--   [ORDER BY col]
--   [ROWS BETWEEN frame_start AND frame_end]
-- )

-- frame_start / frame_end 可选值：
--   UNBOUNDED PRECEDING：分区第一行
--   n PRECEDING：当前行前 n 行
--   CURRENT ROW：当前行
--   n FOLLOWING：当前行后 n 行
--   UNBOUNDED FOLLOWING：分区最后一行

-- 常用组合：
-- ROWS UNBOUNDED PRECEDING：从第一行到当前行（累计）
-- ROWS BETWEEN n PRECEDING AND CURRENT ROW：前 n 行到当前行（移动平均）
-- ROWS BETWEEN n PRECEDING AND n FOLLOWING：前后各n行（中心移动平均）
-- ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING：整个分区（总计）
-- 不写 ROWS 子句时：
--   有 ORDER BY：默认 RANGE UNBOUNDED PRECEDING（累计）
--   无 ORDER BY：默认整个分区（总计）
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 累计求和忘记 ORDER BY | 返回整个分区总计，不是累计 | 累计必须加 ORDER BY，否则窗口帧是整个分区 |
| 移动平均用 RANGE 而不是 ROWS | 相同值的行会被合并，结果不对 | 移动平均必须用 ROWS BETWEEN，RANGE 只对数值类型有特殊含义 |
| 占比计算除零 | 显示 NULL 或 Infinity | 用 NULLIF 处理：sales / NULLIF(SUM() OVER(), 0) |
| 窗口聚合和 GROUP BY 混用 | 结果不符合预期 | 窗口函数在 GROUP BY 之后执行，理解执行顺序 |
| 以为窗口聚合会改变行数 | 行数不变，每行多一个聚合值 | 窗口函数不改变行数，这是和 GROUP BY 的本质区别 |
| 有 ORDER BY 时以为窗口是整个分区 | 实际是累计（到当前行） | 需要整个分区必须写 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING |
| 移动平均开头几天数据少以为是 bug | 正常行为，前几天窗口内行数不足 | 可以用 CASE WHEN 判断行数足够才显示，或接受前几天不准 |

### 动手

1. 计算每日销售额的累计值和7日移动平均
2. 计算每个产品销售额占总销售额的百分比，以及占所属类别的百分比
3. 计算每个月的累计销售额，以及当月累计占全年的比例
4. 计算"到当天为止是否创历史新高"的标记（MAX 窗口应用）
5. 计算7日移动平均和移动标准差（波动分析）
'''

# ========== 3. 偏移函数（增加更多例子） ==========
lag_content = '''### 课前

- **场景**：要计算同比环比（和上一期比）、获取上一行/下一行的值、取分区内第一个/最后一个值、相邻行差值、留存分析。
- **目标**：掌握 LAG、LEAD、FIRST_VALUE、LAST_VALUE 四个偏移函数的用法，能应对各种时间对比和相邻行分析。
- **先修**：窗口函数基础、聚合窗口

### 是什么

- **一句话定义**：偏移函数允许在不进行自连接的情况下，访问当前行之前或之后的行的值，以及分区内的首行/末行值，是计算同比环比、相邻行对比的核心函数。
- **四个函数**：
  - **LAG(col, n, default)**：获取当前行之前第 n 行的值（往前看）
  - **LEAD(col, n, default)**：获取当前行之后第 n 行的值（往后看）
  - **FIRST_VALUE(col)**：获取窗口帧内第一行的值
  - **LAST_VALUE(col)**：获取窗口帧内最后一行的值

### 怎么写

```sql
-- ============================================================
-- 样例：月度销售额表
-- ============================================================
-- year | month | sales
-- 2023 | 01    | 80
-- 2023 | 02    | 90
-- ...
-- 2024 | 01    | 100
-- 2024 | 02    | 120
-- 2024 | 03    | 150
-- 2024 | 04    | 140
-- 2024 | 05    | 180
-- 2024 | 06    | 200

-- ============================================================
-- 例1：LAG() —— 获取上一行的值（环比基础）
-- ============================================================
SELECT 
  year, month, sales,
  LAG(sales) OVER (ORDER BY year, month) AS prev_month_sales,
  LAG(sales, 1) OVER (ORDER BY year, month) AS prev1,  -- 上1行（默认）
  LAG(sales, 2, 0) OVER (ORDER BY year, month) AS prev2  -- 上2行，默认值0
FROM monthly_sales;
-- 结果：
-- 2024-01 | 100 | 90(2023-12) | 90 | 0
-- 2024-02 | 120 | 100 | 100 | 80(2023-11)
-- 2024-03 | 150 | 120 | 120 | 100

-- ============================================================
-- 例2：环比增长率（最常用场景）
-- ============================================================
SELECT 
  year, month, sales,
  LAG(sales) OVER (ORDER BY year, month) AS prev_sales,
  ROUND((sales - LAG(sales) OVER (ORDER BY year, month)) * 100.0 
        / NULLIF(LAG(sales) OVER (ORDER BY year, month), 0), 2) AS mom_pct,
  -- 环比增长量（绝对值）
  sales - LAG(sales) OVER (ORDER BY year, month) AS mom_diff
FROM monthly_sales;
-- 02月环比：(120-100)/100 = 20%
-- 03月环比：(150-120)/120 = 25%

-- ============================================================
-- 例3：LEAD() —— 获取下一行的值
-- ============================================================
SELECT 
  year, month, sales,
  LEAD(sales) OVER (ORDER BY year, month) AS next_month_sales,
  LEAD(sales, 2) OVER (ORDER BY year, month) AS next2
FROM monthly_sales;
-- 2024-01 | 100 | 120 | 150
-- 2024-02 | 120 | 150 | 140
-- ...
-- 2024-06 | 200 | NULL | NULL（最后一行没有下一行）

-- ============================================================
-- 例4：同比增长率（LAG 偏移 12 行 = 去年同月）
-- ============================================================
SELECT 
  year, month, sales,
  LAG(sales, 12) OVER (ORDER BY year, month) AS last_year_sales,
  ROUND((sales - LAG(sales, 12) OVER (ORDER BY year, month)) * 100.0 
        / NULLIF(LAG(sales, 12) OVER (ORDER BY year, month), 0), 2) AS yoy_pct
FROM monthly_sales;
-- LAG(sales, 12) = 往前12行 = 去年同月
-- 2024-01 同比：(100-80)/80 = 25%（假设2023-01是80）

-- ============================================================
-- 例5：季度同比（LAG 偏移 4 行）
-- ============================================================
-- 样例：季度销售额
-- year | quarter | sales
-- 2023 | Q1      | 250
-- 2023 | Q2      | 280
-- 2024 | Q1      | 300
-- 2024 | Q2      | 350

SELECT 
  year, quarter, sales,
  LAG(sales, 4) OVER (ORDER BY year, quarter) AS last_year_q,
  ROUND((sales - LAG(sales, 4) OVER (ORDER BY year, quarter)) * 100.0 
        / NULLIF(LAG(sales, 4) OVER (ORDER BY year, quarter), 0), 2) AS yoy_pct
FROM quarterly_sales;
-- 季度数据同比用 LAG(col, 4)（往前4个季度=去年同季度）

-- ============================================================
-- 例6：FIRST_VALUE() —— 获取分区内第一行的值
-- ============================================================
SELECT 
  year, month, sales,
  FIRST_VALUE(sales) OVER (ORDER BY year, month) AS first_sales,
  FIRST_VALUE(sales) OVER (PARTITION BY year ORDER BY month) AS year_first,
  -- 相对于首月的增长倍数
  ROUND(sales * 1.0 / NULLIF(FIRST_VALUE(sales) OVER (PARTITION BY year ORDER BY month), 0), 2) AS vs_first
FROM monthly_sales;
-- 每行都显示第一个月的销售额
-- vs_first：当月销售额是首月的多少倍

-- ============================================================
-- 例7：LAST_VALUE() —— 获取窗口帧内最后一行的值（注意窗口帧！）
-- ============================================================
-- 注意：LAST_VALUE 默认窗口帧是 RANGE UNBOUNDED PRECEDING（到当前行）
-- 所以直接用 LAST_VALUE 会返回当前行自己！必须指定窗口帧到分区末尾
SELECT 
  year, month, sales,
  LAST_VALUE(sales) OVER (ORDER BY year, month) AS wrong_last,  -- 错误：返回当前行
  LAST_VALUE(sales) OVER (ORDER BY year, month 
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS correct_last
FROM monthly_sales;
-- correct_last 每行都返回最后一个月（2024-06）的销售额 200

-- ============================================================
-- 例8：相邻行差值（差分）—— 每月比上月增长了多少
-- ============================================================
SELECT 
  year, month, sales,
  sales - LAG(sales) OVER (ORDER BY year, month) AS diff,
  sales - LAG(sales, 1, sales) OVER (ORDER BY year, month) AS diff_safe
FROM monthly_sales;
-- 每月比上月增长了多少（绝对值）
-- diff_safe：第一行用默认值 sales，差值为0（避免NULL）

-- ============================================================
-- 例9：连续增长/下降天数（LAG 判断方向）
-- ============================================================
-- 场景：统计销售额连续增长了多少天
WITH direction AS (
  SELECT 
    date, sales,
    CASE 
      WHEN sales > LAG(sales) OVER (ORDER BY date) THEN '增长'
      WHEN sales < LAG(sales) OVER (ORDER BY date) THEN '下降'
      ELSE '持平'
    END AS trend
  FROM daily_sales
)
SELECT date, sales, trend FROM direction;
-- 可以进一步用窗口函数统计连续增长天数（配合 ROW_NUMBER 偏移法）

-- ============================================================
-- 例10：留存分析（LAG 判断用户是否连续活跃）
-- ============================================================
-- 场景：判断用户次日是否留存（今天活跃了，明天是否也活跃）
-- 样例：user_active（user_id, active_date）
-- 1 | 2024-01-01
-- 1 | 2024-01-02  ← 次日留存
-- 1 | 2024-01-04  ← 断了一天

WITH next_active AS (
  SELECT 
    user_id, active_date,
    LEAD(active_date) OVER (PARTITION BY user_id ORDER BY active_date) AS next_date
  FROM user_active
)
SELECT 
  user_id, active_date, next_date,
  CASE WHEN DATEDIFF(next_date, active_date) = 1 THEN '次日留存' 
       WHEN next_date IS NULL THEN '流失'
       ELSE '间隔活跃' END AS retention_status
FROM next_active;
-- 次日留存率 = 次日留存数 / 总活跃数

-- ============================================================
-- 例11：相对于最高月的比例（MAX 窗口 + FIRST_VALUE 配合）
-- ============================================================
SELECT 
  year, month, sales,
  MAX(sales) OVER () AS max_sales,
  ROUND(sales * 100.0 / NULLIF(MAX(sales) OVER (), 0), 2) AS pct_of_max,
  -- 最高月是哪个月
  FIRST_VALUE(month) OVER (ORDER BY sales DESC) AS best_month
FROM monthly_sales;
```

### 函数参数详解

| 函数 | 参数 | 说明 |
|---|---|---|
| LAG(col, n, default) | col：要获取的列；n：往前几行（默认1）；default：超出边界时的默认值（默认NULL） | 往前看 |
| LEAD(col, n, default) | 同上，n 是往后几行 | 往后看 |
| FIRST_VALUE(col) | col：要获取的列 | 窗口帧第一行 |
| LAST_VALUE(col) | col：要获取的列 | 窗口帧最后一行（注意窗口帧设置） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| LAST_VALUE() 直接用不设窗口帧 | 返回当前行自己（不是最后一行） | 必须加 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING |
| 同比用 LAG(sales, 1) 而不是 LAG(sales, 12) | 变成环比不是同比 | 月度数据同比用 LAG(col, 12)，季度用 LAG(col, 4) |
| LAG/LEAD 忘记 ORDER BY | 结果不确定 | 偏移函数必须有明确的 ORDER BY 定义行的顺序 |
| 环比除零（上月为0） | 报错或 Infinity | 用 NULLIF(prev, 0) 处理除零 |
| 用自连接代替 LAG/LEAD | 性能差、代码复杂 | 优先用窗口函数，数据库优化器能高效处理 |
| FIRST_VALUE 以为是全局第一行 | 受 PARTITION BY 限制 | 加了 PARTITION BY 就是分区内第一行，不加才是全局 |
| 同比数据有缺失月份 | LAG(12) 对不上去年同月 | 必须确保数据连续（每月都有），缺失月份要补0 |
| 留存分析用 LAG 而不是 LEAD | 方向反了 | 判断"明天是否来"用 LEAD（往后看），判断"昨天是否来"用 LAG |

### 动手

1. 计算月度销售额的环比增长率和环比增长量（绝对值）
2. 假设有两年数据，用 LAG(sales, 12) 计算同比增长率
3. 用 FIRST_VALUE 和 LAST_VALUE 计算每月销售额相对于首月和末月的比例
4. 计算相邻行差值（差分），分析销售额波动
5. （进阶）实现次日留存分析（LEAD 判断下一天是否活跃）
'''

# ========== 4. 窗口定义（增加更多例子） ==========
def_content = '''### 课前

- **场景**：要精确控制窗口函数计算哪些行、按什么顺序、窗口帧的范围，需要理解 OVER 子句的完整语法，以及窗口函数的执行顺序和高级用法。
- **目标**：掌握 PARTITION BY、ORDER BY、ROWS/RANGE 窗口帧、窗口命名（WINDOW 子句）的完整用法，能写出复杂的窗口函数查询。
- **先修**：排名函数、聚合窗口、偏移函数

### 是什么

- **一句话定义**：窗口定义（OVER 子句）是窗口函数的核心，通过 PARTITION BY 分区、ORDER BY 排序、ROWS/RANGE 定义窗口帧，精确控制窗口函数对哪些行、按什么顺序、在什么范围内进行计算。
- **完整语法**：
```sql
window_function (expression) OVER (
  [PARTITION BY partition_expression]
  [ORDER BY sort_expression [ASC | DESC] [NULLS {FIRST | LAST}]]
  [ROWS | RANGE BETWEEN frame_start AND frame_end]
)
```

### 怎么写

```sql
-- ============================================================
-- 样例：员工表
-- ============================================================
-- emp_id | dept   | emp_name | salary | hire_date  | bonus
-- 1      | 销售部 | 张三     | 15000  | 2023-01-15 | 2000
-- 2      | 销售部 | 李四     | 12000  | 2023-03-20 | NULL
-- 3      | 技术部 | 王五     | 18000  | 2023-02-10 | 3000
-- 4      | 技术部 | 赵六     | 16000  | 2023-06-01 | 1500

-- ============================================================
-- 例1：PARTITION BY —— 分区（分组）
-- ============================================================
SELECT 
  dept, emp_name, salary,
  AVG(salary) OVER (PARTITION BY dept) AS dept_avg_salary,
  AVG(salary) OVER () AS company_avg_salary
FROM employees;
-- PARTITION BY dept：每个部门内的平均工资
-- 无 PARTITION BY：全公司平均工资
-- 注意：PARTITION BY 不改变行数（每行都有结果），这是和 GROUP BY 的本质区别

-- ============================================================
-- 例2：ORDER BY —— 排序（影响排名、累计、窗口帧）
-- ============================================================
SELECT 
  dept, emp_name, salary,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_in_dept,
  SUM(salary) OVER (PARTITION BY dept ORDER BY salary DESC) AS running_sum
FROM employees;
-- ORDER BY salary DESC：工资从高到低排名和累计

-- ============================================================
-- 例3：多字段排序（并列时的 tie-breaker）
-- ============================================================
SELECT 
  dept, emp_name, salary, hire_date,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, hire_date ASC) AS rn
FROM employees;
-- 工资相同的按入职时间早的排前面（资历老的优先）
-- 多字段排序是处理并列值的常用手段

-- ============================================================
-- 例4：NULLS FIRST / LAST —— 空值排序位置
-- ============================================================
SELECT 
  emp_name, bonus,
  ROW_NUMBER() OVER (ORDER BY bonus DESC NULLS LAST) AS rn_last,
  ROW_NUMBER() OVER (ORDER BY bonus DESC NULLS FIRST) AS rn_first
FROM employees;
-- NULLS LAST：空值排最后（默认升序时空值排最后，降序时空值排最前）
-- NULLS FIRST：空值排最前
-- 注意：MySQL 不支持 NULLS FIRST/LAST 语法，用 CASE WHEN 模拟：
-- ORDER BY CASE WHEN bonus IS NULL THEN 1 ELSE 0 END, bonus DESC

-- ============================================================
-- 例5：ROWS 窗口帧 —— 物理行数（精确控制哪些行）
-- ============================================================
SELECT 
  month, sales,
  -- 从分区第一行到当前行（累计）
  SUM(sales) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS running_total,
  -- 前2行到当前行（3日移动平均）
  AVG(sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma3,
  -- 当前行到后2行（前瞻平均）
  AVG(sales) OVER (ORDER BY month ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING) AS forward3,
  -- 前1行到后1行（中心移动平均）
  AVG(sales) OVER (ORDER BY month ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS centered3,
  -- 整个分区（总计）
  SUM(sales) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS total
FROM monthly_sales;

-- ============================================================
-- 例6：RANGE 窗口帧 —— 逻辑范围（基于 ORDER BY 的值）
-- ============================================================
-- RANGE 是按值的范围，不是物理行数；相同 ORDER BY 值的行会被视为同一组
SELECT 
  dept, emp_name, salary,
  -- RANGE UNBOUNDED PRECEDING：到当前行（含相同值的行）
  SUM(salary) OVER (PARTITION BY dept ORDER BY salary RANGE UNBOUNDED PRECEDING) AS range_sum,
  -- ROWS UNBOUNDED PRECEDING：到当前行（物理行）
  SUM(salary) OVER (PARTITION BY dept ORDER BY salary ROWS UNBOUNDED PRECEDING) AS rows_sum
FROM employees;
-- 区别：如果有两人工资相同，RANGE 会把两人都算进去，ROWS 只算到当前物理行
-- RANGE 还支持按值范围：RANGE BETWEEN 1000 PRECEDING AND 1000 FOLLOWING
-- （工资在当前行±1000范围内的行，仅数值类型支持）

-- ============================================================
-- 例7：WINDOW 子句 —— 命名窗口（复用窗口定义，减少重复代码）
-- ============================================================
SELECT 
  month, sales,
  SUM(sales) OVER w AS running_total,
  AVG(sales) OVER w AS running_avg,
  COUNT(*) OVER w AS running_count,
  MAX(sales) OVER w AS running_max
FROM monthly_sales
WINDOW w AS (ORDER BY month ROWS UNBOUNDED PRECEDING);
-- 等价于每个函数都写一遍 OVER (ORDER BY month ROWS UNBOUNDED PRECEDING)
-- 代码更简洁，修改窗口定义只需要改一处

-- ============================================================
-- 例8：多个命名窗口（不同用途的窗口分别命名）
-- ============================================================
SELECT 
  dept, month, sales,
  SUM(sales) OVER monthly AS month_running,
  SUM(sales) OVER dept_total AS dept_total,
  AVG(sales) OVER ma3 AS moving_avg3
FROM sales
WINDOW 
  monthly AS (PARTITION BY dept ORDER BY month ROWS UNBOUNDED PRECEDING),
  dept_total AS (PARTITION BY dept),
  ma3 AS (PARTITION BY dept ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW);

-- ============================================================
-- 例9：窗口函数的执行顺序（非常重要！）
-- ============================================================
-- SQL 执行顺序：FROM → WHERE → GROUP BY → HAVING → WINDOW → SELECT → DISTINCT → ORDER BY → LIMIT
-- 窗口函数在 GROUP BY/HAVING 之后、SELECT 之前执行
-- 所以：
--   1. 窗口函数可以看到 GROUP BY 后的聚合结果
--   2. WHERE 看不到窗口函数的结果（要过滤必须用子查询/CTE）
--   3. SELECT 中的别名不能在窗口函数中直接引用（窗口函数在SELECT前执行）

-- 错误：WHERE 中直接用窗口函数
-- SELECT * FROM t WHERE ROW_NUMBER() OVER (...) = 1  -- 语法错误！

-- 正确：用子查询/CTE
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
  FROM employees
)
SELECT * FROM ranked WHERE rn = 1;

-- ============================================================
-- 例10：窗口函数不能嵌套（必须分层计算）
-- ============================================================
-- 错误：窗口函数嵌套
-- SELECT ROW_NUMBER() OVER (ORDER BY SUM(sales) OVER (...)) FROM t  -- 语法错误！

-- 正确：用 CTE 分层计算
WITH layer1 AS (
  SELECT 
    dept, emp_name, salary,
    SUM(salary) OVER (PARTITION BY dept) AS dept_total
  FROM employees
),
layer2 AS (
  SELECT 
    dept, emp_name, salary, dept_total,
    ROW_NUMBER() OVER (ORDER BY dept_total DESC) AS dept_rank
  FROM layer1
)
SELECT * FROM layer2;
-- 第一层计算部门总计，第二层按部门总计排名

-- ============================================================
-- 例11：PARTITION BY 多字段（多级分区）
-- ============================================================
SELECT 
  region, dept, emp_name, salary,
  AVG(salary) OVER (PARTITION BY region, dept) AS region_dept_avg,
  AVG(salary) OVER (PARTITION BY region) AS region_avg,
  AVG(salary) OVER () AS company_avg
FROM employees;
-- 可以同时计算"区域+部门平均"、"区域平均"、"全公司平均"
-- PARTITION BY 支持多个字段，用逗号分隔

-- ============================================================
-- 例12：窗口函数 + GROUP BY 配合（先聚合再窗口）
-- ============================================================
-- 场景：先按天聚合销售额，再计算累计和移动平均
SELECT 
  date,
  SUM(sales) AS daily_sales,
  SUM(SUM(sales)) OVER (ORDER BY date) AS running_total,
  AVG(SUM(sales)) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7
FROM orders
GROUP BY date
ORDER BY date;
-- 注意：窗口函数中的 SUM(sales) 实际是 SUM(SUM(sales))
-- 内层 SUM(sales) 是 GROUP BY 的聚合，外层 SUM() 是窗口函数
-- 这是窗口函数和 GROUP BY 配合的常见写法
```

### 窗口帧速查表

| 窗口帧定义 | 含义 | 常用场景 |
|---|---|---|
| （不写，无ORDER BY） | 整个分区 | 总计、占比 |
| （不写，有ORDER BY） | RANGE UNBOUNDED PRECEDING（累计） | 累计求和、排名 |
| ROWS UNBOUNDED PRECEDING | 第一行到当前行 | 累计（物理行） |
| ROWS BETWEEN n PRECEDING AND CURRENT ROW | 前n行到当前行 | 移动平均 |
| ROWS BETWEEN CURRENT ROW AND n FOLLOWING | 当前行到后n行 | 前瞻平均 |
| ROWS BETWEEN n PRECEDING AND n FOLLOWING | 前后各n行 | 中心移动平均 |
| ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING | 整个分区 | 总计（有ORDER BY时必须写） |
| RANGE BETWEEN n PRECEDING AND n FOLLOWING | 值在±n范围内 | 按值范围聚合（仅数值类型） |

### ROWS vs RANGE 对比

| 维度 | ROWS | RANGE |
|---|---|---|
| 定义方式 | 物理行数 | ORDER BY 值的逻辑范围 |
| 相同值处理 | 每行独立 | 相同值的行合并为一组 |
| 适用类型 | 所有类型 | 数值/日期/字符串（可排序类型） |
| 常用场景 | 移动平均、精确行数控制 | 累计、按值范围 |
| 性能 | 略好 | 略差（需处理相同值） |
| 支持±n范围 | 是（物理行） | 是（值范围，仅数值类型） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| WHERE 中直接用窗口函数 | 语法错误 | 用子查询/CTE 包裹，外层过滤 |
| 有 ORDER BY 时以为窗口是整个分区 | 实际是累计（到当前行） | 需要整个分区必须写 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING |
| ROWS 和 RANGE 混淆 | 相同值时结果不同 | 移动平均必须用 ROWS，累计可用 RANGE |
| PARTITION BY 和 GROUP BY 混淆 | 行数改变 vs 行数不变 | PARTITION BY 不改变行数（每行都有结果），GROUP BY 会聚合行 |
| 窗口函数嵌套 | 语法错误或结果不对 | 窗口函数不能嵌套，需要用子查询分层计算 |
| 忘记窗口函数在 GROUP BY 之后执行 | 引用了未聚合的列 | 理解执行顺序，窗口函数看到的是 GROUP BY 后的结果 |
| SELECT 别名在窗口函数中使用 | 报错（窗口函数在SELECT前执行） | 窗口函数中不能引用SELECT别名，必须写完整表达式 |
| MySQL 用 NULLS FIRST/LAST | 语法错误（MySQL不支持） | 用 CASE WHEN 模拟：ORDER BY CASE WHEN col IS NULL THEN 1 ELSE 0 END |

### 动手

1. 用 WINDOW 子句定义一个命名窗口，被 SUM/AVG/COUNT 三个函数复用
2. 计算 7 日中心移动平均（前3天+当天+后3天），注意用 ROWS BETWEEN
3. 用 CTE + ROW_NUMBER 实现：每个部门取工资最高的员工（去重取第一条）
4. 实现"先按天聚合，再计算累计和移动平均"的查询（GROUP BY + 窗口函数配合）
5. （进阶）实现窗口函数分层计算：第一层计算部门总计，第二层按部门总计排名
'''

# 更新4个节点
nodes_to_update = {
    "SQL.聚合分析.窗口函数.排名函数": rank_content,
    "SQL.聚合分析.窗口函数.聚合窗口": agg_content,
    "SQL.聚合分析.窗口函数.偏移函数": lag_content,
    "SQL.聚合分析.窗口函数.窗口定义": def_content,
}

for nid, new_content in nodes_to_update.items():
    node = find_node(data, nid)
    old_len = len(node["content"])
    node["content"] = new_content
    print(f"更新 {node['title']}: {old_len} → {len(new_content)} 字符")

# 序列化
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["sql"]={new_json_str}\n'

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-sql.js size: {len(new_content)} bytes")
print("SQL 窗口函数4个子节点内容完善完成！")
