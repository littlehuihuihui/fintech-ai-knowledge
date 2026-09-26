#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQL 窗口函数细分"""

import json, re

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

# ========== 子叶子节点 ==========

leaf_rank = make_leaf("SQL.聚合分析.窗口函数.排名函数", "排名函数", "??", """### 课前

- **场景**：要给每个区域的销售额排名、取 Top N、给用户分位数分组。
- **目标**：掌握 ROW_NUMBER、RANK、DENSE_RANK、NTILE 四个排名函数的区别和适用场景。
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
-- 样例数据：每个员工的销售额
-- emp_id | dept | sales
-- 1      | 销售部 | 100
-- 2      | 销售部 | 100
-- 3      | 销售部 | 80
-- 4      | 销售部 | 60
-- 5      | 技术部 | 90
-- 6      | 技术部 | 90
-- 7      | 技术部 | 70

-- 1. ROW_NUMBER()：唯一序号，并列时按 ORDER BY 后续字段或隐含顺序
SELECT 
  emp_id, dept, sales,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY sales DESC) AS rn
FROM employees;
-- 结果：
-- 销售部：100→1, 100→2, 80→3, 60→4（两个100强行排1和2）
-- 技术部：90→1, 90→2, 70→3

-- 2. RANK()：并列排名，跳过后续序号
SELECT 
  emp_id, dept, sales,
  RANK() OVER (PARTITION BY dept ORDER BY sales DESC) AS rk
FROM employees;
-- 结果：
-- 销售部：100→1, 100→1, 80→3, 60→4（两个并列第1，下一个直接第3）
-- 技术部：90→1, 90→1, 70→3

-- 3. DENSE_RANK()：并列排名，不跳过序号
SELECT 
  emp_id, dept, sales,
  DENSE_RANK() OVER (PARTITION BY dept ORDER BY sales DESC) AS dr
FROM employees;
-- 结果：
-- 销售部：100→1, 100→1, 80→2, 60→3（两个并列第1，下一个第2，连续）
-- 技术部：90→1, 90→1, 70→2

-- 4. NTILE(n)：平均分成 n 组
SELECT 
  emp_id, dept, sales,
  NTILE(2) OVER (PARTITION BY dept ORDER BY sales DESC) AS tile2,
  NTILE(4) OVER (ORDER BY sales DESC) AS tile4_all
FROM employees;
-- 销售部4人分2组：前2名→1，后2名→2
-- 全部7人分4组：尽量平均（2,2,2,1人）

-- 5. 取每个部门销售额 Top 2（最常用场景）
WITH ranked AS (
  SELECT 
    emp_id, dept, sales,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY sales DESC) AS rn
  FROM employees
)
SELECT * FROM ranked WHERE rn <= 2;
-- 每个部门取前2名（用 ROW_NUMBER 保证正好取2个，不会因为并列多取）

-- 6. 取前 10% 的员工（NTILE 分位数）
WITH tiled AS (
  SELECT 
    emp_id, dept, sales,
    NTILE(10) OVER (ORDER BY sales DESC) AS tile
  FROM employees
)
SELECT * FROM tiled WHERE tile = 1;
-- tile=1 就是前 10%
```

### 四个函数对比表

| 函数 | 并列处理 | 序号特点 | 适用场景 |
|---|---|---|---|
| ROW_NUMBER | 强行排序，无并列 | 连续唯一 | Top N（正好取N个）、去重取第一条 |
| RANK | 并列同排名，跳过后续 | 不连续（1,1,3） | 考试排名、竞赛排名（并列名次） |
| DENSE_RANK | 并列同排名，不跳过 | 连续（1,1,2） | 产品等级、分数段（名次连续） |
| NTILE(n) | 平均分组 | 组号1~n | 分位数、四分位、Top N% |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 用 RANK() 取 Top N | 并列时可能多取（如 Top2 取出3条） | 正好取 N 条用 ROW_NUMBER()，需要包含并列用 RANK() + 子查询 |
| 忘记 PARTITION BY | 全局排名，不是分组排名 | 需要每个组内排名必须加 PARTITION BY |
| ORDER BY 方向搞反 | 排名顺序反了 | 降序排名用 DESC（高的排前面），升序用 ASC |
| NTILE 分组不均匀以为是 bug | NTILE 尽量平均，不能整除时前几组多1个 | 正常行为，前 (总数%n) 组多1个 |
| 排名函数里加 DISTINCT | 语法错误或结果意外 | 排名函数不支持 DISTINCT，先去重再排名 |

### 动手

1. 用 ROW_NUMBER() 给每个区域的订单按金额降序排名，取每个区域 Top 3
2. 对比 RANK() 和 DENSE_RANK() 的结果，解释什么时候用哪个
3. 用 NTILE(4) 把用户按消费金额分成4组，统计每组的人数和平均消费
""")

leaf_agg = make_leaf("SQL.聚合分析.窗口函数.聚合窗口", "聚合窗口", "??", """### 课前

- **场景**：要计算累计销售额、移动平均、每行占分区总计的比例，用 GROUP BY 会丢失明细行。
- **目标**：掌握 SUM/AVG/COUNT/MIN/MAX 配合 OVER 子句实现窗口聚合，包括累计、移动平均、占比。
- **先修**：窗口函数基础、GROUP BY

### 是什么

- **一句话定义**：聚合窗口函数将聚合函数（SUM/AVG/COUNT 等）应用于窗口内的行集合，为每一行返回一个聚合值，同时保留明细行，解决了 GROUP BY 只能返回聚合行的限制。
- **核心能力**：累计求和（running total）、移动平均（moving average）、占比（ratio to total）、分区内统计。

### 怎么写

```sql
-- 样例：每日销售额
-- date       | sales
-- 2024-01-01 | 100
-- 2024-01-02 | 150
-- 2024-01-03 | 120
-- 2024-01-04 | 200
-- 2024-01-05 | 180

-- 1. 累计求和（Running Total）：从第一行到当前行的累计
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

-- 2. 分区内累计：每个月内累计
SELECT 
  date, month, sales,
  SUM(sales) OVER (PARTITION BY month ORDER BY date) AS month_running
FROM daily_sales;
-- 每个月从1号开始重新累计

-- 3. 移动平均（Moving Average）：前 N 行到当前行的平均
SELECT 
  date, sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma3
FROM daily_sales;
-- 3日移动平均（含当天和前2天）
-- 01-01 | 100 | 100（只有1天）
-- 01-02 | 150 | 125（2天平均）
-- 01-03 | 120 | 123.33（3天平均：(100+150+120)/3）
-- 01-04 | 200 | 156.67（(150+120+200)/3）
-- 01-05 | 180 | 166.67（(120+200+180)/3）

-- 4. 占比（Ratio to Total）：每行占分区总计的百分比
SELECT 
  date, sales,
  SUM(sales) OVER () AS total,
  ROUND(sales * 100.0 / SUM(sales) OVER (), 2) AS pct
FROM daily_sales;
-- 总计 750，每行占比：
-- 01-01 | 100 | 750 | 13.33%
-- 01-02 | 150 | 750 | 20.00%
-- ...

-- 5. 分区内占比：每个区域内的占比
SELECT 
  region, date, sales,
  SUM(sales) OVER (PARTITION BY region) AS region_total,
  ROUND(sales * 100.0 / SUM(sales) OVER (PARTITION BY region), 2) AS region_pct
FROM daily_sales;

-- 6. 计数窗口：分区内总行数、累计行数
SELECT 
  date, sales,
  COUNT(*) OVER (PARTITION BY month) AS month_days,
  COUNT(*) OVER (ORDER BY date) AS running_count
FROM daily_sales;

-- 7. 窗口内最大/最小值：到当前行为止的历史最高
SELECT 
  date, sales,
  MAX(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS max_so_far,
  MIN(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS min_so_far
FROM daily_sales;

-- 8. 综合应用：计算同比增长率（需要 LAG，见偏移函数章节）
-- 或计算每日销售额占当月累计的比例
SELECT 
  date, month, sales,
  SUM(sales) OVER (PARTITION BY month ORDER BY date) AS month_running,
  SUM(sales) OVER (PARTITION BY month) AS month_total,
  ROUND(SUM(sales) OVER (PARTITION BY month ORDER BY date) * 100.0 
        / SUM(sales) OVER (PARTITION BY month), 2) AS pct_of_month
FROM daily_sales;
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

### 动手

1. 计算每日销售额的累计值和7日移动平均
2. 计算每个产品销售额占总销售额的百分比，以及占所属类别的百分比
3. 计算每个月的累计销售额，以及当月累计占全年的比例
""")

leaf_offset = make_leaf("SQL.聚合分析.窗口函数.偏移函数", "偏移函数", "???", """### 课前

- **场景**：要计算同比环比（和上一期比）、获取上一行/下一行的值、取分区内第一个/最后一个值。
- **目标**：掌握 LAG、LEAD、FIRST_VALUE、LAST_VALUE 四个偏移函数的用法。
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
-- 样例：月度销售额
-- month    | sales
-- 2024-01  | 100
-- 2024-02  | 120
-- 2024-03  | 150
-- 2024-04  | 140
-- 2024-05  | 180
-- 2024-06  | 200

-- 1. LAG()：获取上一行的值（环比基础）
SELECT 
  month, sales,
  LAG(sales) OVER (ORDER BY month) AS prev_month_sales,
  LAG(sales, 1) OVER (ORDER BY month) AS prev1,  -- 上1行（默认）
  LAG(sales, 2, 0) OVER (ORDER BY month) AS prev2  -- 上2行，默认值0
FROM monthly_sales;
-- 结果：
-- 01 | 100 | NULL | NULL | 0
-- 02 | 120 | 100  | 100  | 0
-- 03 | 150 | 120  | 120  | 100
-- 04 | 140 | 150  | 150  | 120
-- ...

-- 2. 环比增长率（最常用）
SELECT 
  month, sales,
  LAG(sales) OVER (ORDER BY month) AS prev_sales,
  ROUND((sales - LAG(sales) OVER (ORDER BY month)) * 100.0 
        / NULLIF(LAG(sales) OVER (ORDER BY month), 0), 2) AS mom_pct
FROM monthly_sales;
-- 02月环比：(120-100)/100 = 20%
-- 03月环比：(150-120)/120 = 25%
-- ...

-- 3. LEAD()：获取下一行的值
SELECT 
  month, sales,
  LEAD(sales) OVER (ORDER BY month) AS next_month_sales,
  LEAD(sales, 2) OVER (ORDER BY month) AS next2
FROM monthly_sales;
-- 01 | 100 | 120 | 150
-- 02 | 120 | 150 | 140
-- ...
-- 06 | 200 | NULL | NULL（最后一行没有下一行）

-- 4. 同比增长率（需要按月对齐，假设数据有多年）
-- 用 LAG(sales, 12) 获取去年同月
SELECT 
  year, month, sales,
  LAG(sales, 12) OVER (ORDER BY year, month) AS last_year_sales,
  ROUND((sales - LAG(sales, 12) OVER (ORDER BY year, month)) * 100.0 
        / NULLIF(LAG(sales, 12) OVER (ORDER BY year, month), 0), 2) AS yoy_pct
FROM monthly_sales;
-- LAG(sales, 12) = 往前12行 = 去年同月

-- 5. FIRST_VALUE()：获取分区内第一行的值
SELECT 
  month, sales,
  FIRST_VALUE(sales) OVER (ORDER BY month) AS first_sales,
  FIRST_VALUE(sales) OVER (PARTITION BY year ORDER BY month) AS year_first
FROM monthly_sales;
-- 每行都显示第一个月的销售额
-- 可用于计算"相对于首月的增长倍数"

-- 6. LAST_VALUE()：获取窗口帧内最后一行的值
-- 注意：LAST_VALUE 默认窗口帧是 RANGE UNBOUNDED PRECEDING（到当前行）
-- 所以直接用 LAST_VALUE 会返回当前行自己！必须指定窗口帧到分区末尾
SELECT 
  month, sales,
  LAST_VALUE(sales) OVER (ORDER BY month) AS wrong_last,  -- 错误：返回当前行
  LAST_VALUE(sales) OVER (ORDER BY month 
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS correct_last
FROM monthly_sales;
-- correct_last 每行都返回最后一个月（6月）的销售额 200

-- 7. 综合应用：计算每月销售额相对于全年最高月的比例
SELECT 
  month, sales,
  MAX(sales) OVER () AS max_sales,
  ROUND(sales * 100.0 / MAX(sales) OVER (), 2) AS pct_of_max
FROM monthly_sales;

-- 8. 综合应用：相邻行差值（差分）
SELECT 
  month, sales,
  sales - LAG(sales) OVER (ORDER BY month) AS diff,
  sales - LAG(sales, 1, sales) OVER (ORDER BY month) AS diff_safe
FROM monthly_sales;
-- 每月比上月增长了多少（绝对值）
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

### 动手

1. 计算月度销售额的环比增长率和环比增长量（绝对值）
2. 假设有两年数据，用 LAG(sales, 12) 计算同比增长率
3. 用 FIRST_VALUE 和 LAST_VALUE 计算每月销售额相对于首月和末月的比例
""")

leaf_def = make_leaf("SQL.聚合分析.窗口函数.窗口定义", "窗口定义", "???", """### 课前

- **场景**：要精确控制窗口函数计算哪些行、按什么顺序、窗口帧的范围，需要理解 OVER 子句的完整语法。
- **目标**：掌握 PARTITION BY、ORDER BY、ROWS/RANGE 窗口帧、窗口命名（WINDOW 子句）的完整用法。
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
-- 1. PARTITION BY：分区（分组）
-- 将数据分成多个分区，窗口函数在每个分区内独立计算
SELECT 
  dept, emp_name, salary,
  AVG(salary) OVER (PARTITION BY dept) AS dept_avg_salary,
  AVG(salary) OVER () AS company_avg_salary
FROM employees;
-- PARTITION BY dept：每个部门内的平均工资
-- 无 PARTITION BY：全公司平均工资

-- 2. ORDER BY：排序
-- 定义分区内行的顺序，影响排名函数、累计、窗口帧
SELECT 
  dept, emp_name, salary,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_in_dept,
  SUM(salary) OVER (PARTITION BY dept ORDER BY salary DESC) AS running_sum
FROM employees;
-- ORDER BY salary DESC：工资从高到低排名和累计

-- 3. 多字段排序
SELECT 
  dept, emp_name, salary, hire_date,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, hire_date ASC) AS rn
FROM employees;
-- 工资相同的按入职时间早的排前面

-- 4. NULLS FIRST / LAST：空值排序位置
SELECT 
  emp_name, bonus,
  ROW_NUMBER() OVER (ORDER BY bonus DESC NULLS LAST) AS rn
FROM employees;
-- NULLS LAST：空值排最后（默认升序时空值排最后，降序时空值排最前）
-- NULLS FIRST：空值排最前

-- 5. ROWS 窗口帧：物理行数
-- 定义窗口包含哪些行（基于物理位置）
SELECT 
  month, sales,
  -- 从分区第一行到当前行（累计）
  SUM(sales) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS running_total,
  -- 前2行到当前行（3日移动平均）
  AVG(sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma3,
  -- 当前行到后2行
  AVG(sales) OVER (ORDER BY month ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING) AS forward3,
  -- 前1行到后1行（中心移动平均）
  AVG(sales) OVER (ORDER BY month ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS centered3,
  -- 整个分区（总计）
  SUM(sales) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS total
FROM monthly_sales;

-- 6. RANGE 窗口帧：逻辑范围（基于 ORDER BY 的值）
-- RANGE 是按值的范围，不是物理行数
-- 相同 ORDER BY 值的行会被视为同一组
SELECT 
  dept, emp_name, salary,
  -- RANGE UNBOUNDED PRECEDING：到当前行（含相同值的行）
  SUM(salary) OVER (PARTITION BY dept ORDER BY salary RANGE UNBOUNDED PRECEDING) AS range_sum,
  -- ROWS UNBOUNDED PRECEDING：到当前行（物理行）
  SUM(salary) OVER (PARTITION BY dept ORDER BY salary ROWS UNBOUNDED PRECEDING) AS rows_sum
FROM employees;
-- 区别：如果有两人工资相同，RANGE 会把两人都算进去，ROWS 只算到当前物理行

-- 7. WINDOW 子句：命名窗口（复用窗口定义）
-- 当多个窗口函数使用相同的 OVER 定义时，可以命名复用
SELECT 
  month, sales,
  SUM(sales) OVER w AS running_total,
  AVG(sales) OVER w AS running_avg,
  COUNT(*) OVER w AS running_count
FROM monthly_sales
WINDOW w AS (ORDER BY month ROWS UNBOUNDED PRECEDING);
-- 等价于每个函数都写一遍 OVER (ORDER BY month ROWS UNBOUNDED PRECEDING)

-- 8. 多个命名窗口
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

-- 9. 窗口函数的执行顺序
-- SQL 执行顺序：FROM → WHERE → GROUP BY → HAVING → WINDOW → SELECT → DISTINCT → ORDER BY → LIMIT
-- 窗口函数在 GROUP BY/HAVING 之后、SELECT 之前执行
-- 所以窗口函数可以看到 GROUP BY 后的聚合结果，但 WHERE 看不到窗口函数的结果
-- （要在 WHERE 中用窗口函数结果，必须用子查询/CTE）

-- 错误：WHERE 中直接用窗口函数
-- SELECT * FROM t WHERE ROW_NUMBER() OVER (...) = 1  -- 语法错误！

-- 正确：用子查询/CTE
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
  FROM employees
)
SELECT * FROM ranked WHERE rn = 1;
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

### ROWS vs RANGE 对比

| 维度 | ROWS | RANGE |
|---|---|---|
| 定义方式 | 物理行数 | ORDER BY 值的逻辑范围 |
| 相同值处理 | 每行独立 | 相同值的行合并为一组 |
| 适用类型 | 所有类型 | 数值/日期/字符串（可排序类型） |
| 常用场景 | 移动平均、精确行数控制 | 累计、按值范围 |
| 性能 | 略好 | 略差（需处理相同值） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| WHERE 中直接用窗口函数 | 语法错误 | 用子查询/CTE 包裹，外层过滤 |
| 有 ORDER BY 时以为窗口是整个分区 | 实际是累计（到当前行） | 需要整个分区必须写 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING |
| ROWS 和 RANGE 混淆 | 相同值时结果不同 | 移动平均必须用 ROWS，累计可用 RANGE |
| PARTITION BY 和 GROUP BY 混淆 | 行数改变 vs 行数不变 | PARTITION BY 不改变行数（每行都有结果），GROUP BY 会聚合行 |
| 窗口函数嵌套 | 语法错误或结果不对 | 窗口函数不能嵌套，需要用子查询分层计算 |
| 忘记窗口函数在 GROUP BY 之后执行 | 引用了未聚合的列 | 理解执行顺序，窗口函数看到的是 GROUP BY 后的结果 |

### 动手

1. 用 WINDOW 子句定义一个命名窗口，被 SUM/AVG/COUNT 三个函数复用
2. 计算 7 日中心移动平均（前3天+当天+后3天），注意用 ROWS BETWEEN
3. 用 CTE + ROW_NUMBER 实现：每个部门取工资最高的员工（去重取第一条）
""")

# ========== 读取并修改 embed-sql.js ==========
with open(r"D:\cursor\数据学习平台\kg-data\embed-sql.js", "r", encoding="utf-8") as f:
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

window_node = find_node(data, "SQL.聚合分析.窗口函数")
if not window_node:
    print("ERROR: Cannot find 窗口函数 node")
    exit(1)

print(f"Current 窗口函数: children={len(window_node.get('children', []))}")

# 保存原来的 content 作为基础，更新为章节导读
old_content = window_node["content"]

# 新的章节导读内容
chapter_content = """### 课前 · 章节导读

- **章节**：窗口函数
- **为什么学本章**：窗口函数是 SQL 进阶的核心，解决 GROUP BY 丢失明细、自连接性能差的问题，是数据分析必备技能。
- **学习目标**：掌握排名函数、聚合窗口、偏移函数、窗口定义四大类，能独立写出累计、同比环比、Top N、移动平均等常见分析。
- **先修**：GROUP BY、HAVING

### 本章故事线

```text
排名函数 → 聚合窗口 → 偏移函数 → 窗口定义
```

### 本章叶课地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | 排名函数 | ?? | ROW_NUMBER/RANK/DENSE_RANK/NTILE，Top N 与分位数 |
| 2 | 聚合窗口 | ?? | SUM/AVG OVER，累计求和、移动平均、占比 |
| 3 | 偏移函数 | ??? | LAG/LEAD/FIRST_VALUE/LAST_VALUE，同比环比 |
| 4 | 窗口定义 | ??? | PARTITION BY/ORDER BY/ROWS/RANGE，精确控制窗口 |

### 推荐顺序

```text
排名函数 → 聚合窗口 → 偏移函数 → 窗口定义
```

### 怎么学本章

1. **先扫地图**：知道本章有哪些叶、各自解决什么
2. **按序开叶**：每叶走完「怎么写 → 易错对照 → 动手」
3. **章末串讲**：用 3 分钟向同伴复述窗口函数的四大分类和适用场景

### 章末验收

| 检查项 | 通过标准 |
|---|---|
| 主路径 | 每叶示例可跑通或可手推结果 |
| 易错 | 能举本章至少 2 个反例 |
| 迁移 | 能说出换表后要改的 3 处 |
| 口述 | 不看笔记讲清「窗口函数」和 GROUP BY 的区别 |

### 下一动

点开地图中的第 1 片绿色叶节点。本章合计约 **4** 片叶讲义。
"""

window_node["content"] = chapter_content
window_node["lessonParent"] = True
window_node["children"] = [leaf_rank, leaf_agg, leaf_offset, leaf_def]

print(f"New 窗口函数 children: {[c['title'] for c in window_node['children']]}")

# 序列化
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["sql"]={new_json_str}\n'

with open(r"D:\cursor\数据学习平台\kg-data\embed-sql.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-sql.js size: {len(new_content)} bytes")
print("SQL 窗口函数细分完成")
