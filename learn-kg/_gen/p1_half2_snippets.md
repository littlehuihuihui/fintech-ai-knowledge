# P1 后半片段

## P1-3 dwh-lakehouse-sec

### 课前 · 章节导读

- **章节**：湖仓一体
- **为什么学**：现代数仓常把「廉价对象存储上的湖」与「可治理、可服务的仓」合在一套架构；不会边界就会既失去湖的灵活，又失去仓的可信。
- **学习目标**：能区分湖 / 仓 / 湖仓；能说明 Iceberg/Hudi/Delta 的核心能力；能按场景选型并对应 ODS→ADS 落点。
- **先修**：`dwh-ssot`（SSOT）；`dwh-layers`（层级职责）；`dwh-incr-sec`（增量与分区）。
- **难度**：`???`（见 `kg-data/难度词典.md`）

### 本节地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | 湖仓一体直觉 | ??? | 湖存文件，仓要治理；湖仓要两边都站住 |
| 2 | Iceberg/Hudi/Delta 对比 | ??? | 表格式提供 ACID、演进、时间旅行 |
| 3 | 湖仓边界与选型 | ??? | 什么时候上湖仓，什么时候别硬上 |

### 推荐顺序

```text
湖仓一体直觉 → Iceberg/Hudi/Delta 对比 → 湖仓边界与选型
```

### 强制引用（node_id）

- 分层落点：`dwh-layers`
- 增量与分区回刷：`dwh-incr-sec`（细读 `dwh-incremental` / `dwh-partition`）
- 与工程选型交叉：`etl-tool-map`

### 下一动

从「湖仓一体直觉」开始。本章 **3** 片叶讲义。


## dwh-lakehouse-intro

### 课前

- **场景**：数据湖里堆了大量 Parquet，BI 要查「昨日支付 GMV」，却无法增量更新单行；ML 又要同一批订单特征做训练；业务问「能不能回到上周 schema 还能查」。
- **目标**：建立湖 / 仓 / 湖仓一体的边界直觉，并用同源四表说明「文件堆」与「可治理表」的差别。
- **先修**：`dwh-ssot`；`dwh-layers`。
- **难度**：`???`
- **学完标准**：能用一句话区分三者；能指出「仅 Parquet 目录」缺哪三类仓能力。

### 是什么

- **数据湖**：对象存储 + 开放文件格式（Parquet/ORC），写便宜、schema-on-read，默认**弱治理**。
- **数据仓**：强治理、强口径、面向分析服务（主题、分层、权限、SLA）。
- **湖仓一体**：在湖的存储上补齐**表格式与事务语义**，让同一份数据既能被 BI 可信查询，又能被 ML 扫描训练。
- **核心要素**：开放格式、表元数据、ACID/快照、与分层（ODS/DWD/DWS/ADS）对齐。
- **边界**：湖仓不是「不要数仓分层」；分层职责仍以 `dwh-layers` 为准。
- **引用**：`dwh-layers`、`dwh-incr-sec`、`etl-tool-map`。

### 怎么写

1. 把宪法 `orders`（8 行）想象成落在 `s3://lake/ods/orders/dt=2024-01-03/*.parquet`。  
2. 列出「裸湖」做不到的三件事：行级更新、可靠并发写、按快照时间旅行。  
3. 对照仓侧需求：支付 GMV 口径（映射表）必须可复算。  
4. 画对应：ODS 贴源文件 → DWD 治理明细表 → DWS/ADS 服务表（仍在湖仓表格式上）。  
5. 写边界句：「ML 可以扫 ODS/DWD 文件；对外指标必须以认证 ADS/语义层为准」。

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 把「有 Parquet」当成有数仓 | 口径漂移、无法增量 | 补表格式 + 分层 + SSOT（`dwh-ssot`） |
| 湖仓后取消分层 | 明细与指标混用 | 仍按 `dwh-layers` |
| BI 与 ML 抢同一未治理明细当官方 | 数字互撕 | 消费面分级：探索 vs 认证 |

### 动手

同源四表：`users=4` / `orders=8` / `order_events=7` / `order_items=5`。

1. 写一张三列对照表：湖 / 仓 / 湖仓，每列至少 3 条能力（存储、更新、治理）。  
2. 针对「无法增量更新 Parquet 目录」写出：若只有文件覆盖，重跑 `dt=2024-01-03` 时如何避免双倍行（文字步骤 ≥ 4 步，对应 `dwh-partition` 回刷思路）。  
3. 计算支付 GMV（`status='paid'`，`COALESCE(amount,0)`）：结果应为 **宪法种子 Ada 相关校验用全表 paid GMV**——全表 paid 金额合计按宪法样例核对为 **540**（若你本地构造不同，以宪法页种子为准并在答案注明）。  

> 本地可用 DuckDB 只读演示「文件当表」，**不要**假装已有 Iceberg catalog。

```sql
-- DuckDB 伪演示：把 orders 当成湖文件读入
-- CREATE TABLE orders AS SELECT * FROM read_csv_auto('orders.csv');
SELECT SUM(COALESCE(amount,0)) AS gmv
FROM orders
WHERE status = 'paid';
```

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 三者对照 | 表 ≥ 3×3 单元格非空 |
| 回刷步骤 | ≥ 4 步且提到按 `dt` 覆盖 |
| paid GMV | 给出明确数字，并注明与宪法种子一致或差异原因 |
| 引用 | 正文出现 node_id：`dwh-layers`、`dwh-incr-sec` |


## dwh-table-format

### 课前

- **场景**：湖里 schema 加了一列，下游 Spark 作业全挂；又希望「时间旅行」查昨天快照的订单表；同时还要支持 upsert 订单状态。
- **目标**：对比 Iceberg / Hudi / Delta 的核心能力：ACID、schema 演进、时间旅行、增量消费。
- **先修**：`dwh-lakehouse-intro`；`dwh-partition`。
- **难度**：`???`
- **学完标准**：能列出三套表格式的共同能力 ≥ 4 项；能各举 1 个更适合的场景。

### 是什么

- **表格式（Table Format）**：在对象存储文件之上增加**元数据层**（快照、清单、事务日志），使多引擎可共享同一张「表」。
- **共同能力（现代标配）**：
  1. ACID on 湖（提交/快照隔离）
  2. Schema 演进（加列/改注释等，策略因实现而异）
  3. 时间旅行 / 回滚到快照
  4. 增量读取（CDC 风格消费变更）
- **粗对比（教学用，非厂商评测）**：

| 能力 | Iceberg | Hudi | Delta Lake |
|---|---|---|---|
| 快照/ACID | 强 | 强 | 强 |
| upsert/增量 | 支持 | 强（MOR/COW） | 支持 |
| 多引擎开放 | 很强 | 强 | 强（生态偏 Databricks 历史） |
| 时间旅行 | 有 | 有 | 有 |

- **引用**：增量语义主树在 ETL（`etl-tool-map` 工具地图）；本课只讲**表层能力**。分区回刷见 `dwh-incr-sec`。

### 怎么写

1. 用伪代码描述一次「订单状态更新」提交：写数据文件 → 写清单/日志 → 提交快照。  
2. 演示 schema 演进：`orders` 增加 `pay_channel` 列，旧快照仍可读。  
3. 时间旅行：`SELECT * FROM orders VERSION AS OF <snapshot>`（语法示意）。  
4. 说明与分层：ODS 可用 append；DWD 常用 upsert；ADS 可快照物化。  
5. 用 DuckDB **模拟**快照表（两张物理表 `orders_v1`/`orders_v2`），不要连真实湖。

```sql
-- 本地 DuckDB：用两版表模拟时间旅行（非 Iceberg）
CREATE TABLE orders_v1 AS SELECT * FROM orders;
-- 假设订单 101 从 created -> paid
CREATE TABLE orders_v2 AS
SELECT * REPLACE('paid' AS status) FROM orders_v1 WHERE order_id = 101
UNION ALL
SELECT * FROM orders_v1 WHERE order_id <> 101;

SELECT SUM(COALESCE(amount,0)) FROM orders_v1 WHERE status='paid';
SELECT SUM(COALESCE(amount,0)) FROM orders_v2 WHERE status='paid';
```

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 以为换了表格式就自动有质量 | 脏数据进湖 | 门禁仍要 ETL DQ（交叉 `etl-checks`） |
| schema 演进无兼容策略 | 下游全挂 | 先加列可空，再回填；版本化发布 |
| 时间旅行当 SCD | 概念混用 | 快照≠拉链表；SCD 见 DWH 主树 SCD 课 |

### 动手

1. 填一张 4 行「共同能力」清单，每行用 orders 举一例（如：状态从 created→paid 需要 upsert）。  
2. 用上面 DuckDB 双版本：报告 `orders_v1` 与 `orders_v2` 的 paid GMV **两个数字**，并写清差值为哪一单引起。  
3. 写一段「schema 加列」发布说明（≥ 5 行），点名影响的下游：BI、ML 特征作业。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 共同能力 | ≥ 4 条 |
| 双版本 GMV | 给出 v1、v2 两个数值与差值 |
| 发布说明 | ≥ 5 行且含 node_id 引用 `dwh-layers` |
| 未要求真实 Iceberg | 仅伪代码/DuckDB |


## dwh-lakehouse-boundary

### 课前

- **场景**：老板听到「湖仓一体」要求全部上 Iceberg；同时现有仓已能稳定出 ADS；团队不会运维 catalog。
- **目标**：会做选型边界：何时上湖仓，何时维持仓内表 + 湖仅存原始文件。
- **先修**：前两叶；`etl-tool-map`；`dwh-layers`。
- **难度**：`???`
- **学完标准**：能给出「上 / 不上」决策表 ≥ 6 行；能把 ODS/DWD/DWS/ADS 映射到湖仓落点。

### 是什么

- **选型问题**：湖仓解决的是「多引擎共享、开放存储、事务与演进」，不是营销词。  
- **适合上**：多计算引擎（Spark/Flink/Trino）共享同一明细；需要 upsert + 时间旅行；ML 与 BI 同存不同权。  
- **不适合硬上**：团队无平台能力；指标仍混乱（先做 SSOT/`dwh-ssot`）；只有小数据量单仓已够。  
- **与分层对应（示例）**：

| 分层 | 湖仓落点 |
|---|---|
| ODS | append-only 分区表 |
| DWD | upsert 明细表 |
| DWS | 轻度汇总快照 |
| ADS | 服务快照 / 对外认证集 |

- **引用**：`dwh-layers`、`dwh-incr-sec`、`etl-tool-map`。

### 怎么写

1. 列出当前痛点是否命中「多引擎 / upsert / 时间旅行 / schema 演进」。  
2. 对照团队能力：catalog、权限、监控、DQ 门禁是否具备。  
3. 画落点：四表进 ODS，订单事实进 DWD，GMV 进 ADS。  
4. 写风险：小文件、元数据膨胀、误用时间旅行替代 SCD。  
5. 给决策：试点一张 `orders` DWD，再扩维表。

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 为上而上 | 运维崩溃 | 先试点主题域 |
| 忽略质量与口径 | 湖仓放大脏数据 | 先映射表 + DQ |
| 用湖仓替代主树规则里的 SCD/分区课 | 概念真空 | 机制仍回指 DWH 主课 |

### 动手

1. 输出「上湖仓 / 不上」决策表，至少 6 行（条件 → 结论）。  
2. 给同源四表各指定落层：`users`→维、`orders`→事实、`order_items`→事实明细、`order_events`→事件 ODS/DWD。  
3. 写试点成功标准 3 条（必须可量化，例如：DWD `orders` 按 `dt` 回刷成功次数 ≥ 1；paid GMV 与 SQL 口径差 = 0）。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 决策表 | ≥ 6 行 |
| 四表落层 | 4 个表都有分层标签 |
| 试点标准 | ≥ 3 条且含数字 |
| 引用 | 出现 `dwh-layers`、`etl-tool-map`、`dwh-incr-sec` |


## P1-4 etl-dq-engine-sec

### 课前 · 章节导读

- **章节**：质量规则引擎
- **为什么学**：只有「校验清单」不够——规则写死在 SQL 里难扩展，发现太晚，告警又太多。要把质量做成**可配置的规则引擎 + 门禁策略**。
- **学习目标**：掌握质量六维度；会用 YAML 定义断言；会把规则接入管道并区分阻断/告警。
- **先修**：`etl-checks`（校验清单）；交叉 `etl-tool-dbt`、`dwh-reconcile`。
- **难度**：章节 `???`；首叶六维度为 `??`。

### 本节地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | 质量六维度 | ?? | 完整/准确/一致/及时/唯一/有效 |
| 2 | 规则定义与断言 | ??? | 规则即配置，断言可复用 |
| 3 | 质量门禁接入管道 | ??? | 阻断 vs 告警，失败可定位 |

### 推荐顺序

```text
质量六维度 → 规则定义与断言 → 质量门禁接入管道
```

### 强制引用（node_id）

- 清单基础：`etl-checks`
- 变换测试交叉：`etl-tool-dbt`
- 仓侧对账交叉：`dwh-reconcile`

### 下一动

从「质量六维度」开始。本章 **3** 片叶讲义。


## etl-dq-dimensions

### 课前

- **场景**：校验 SQL 越写越长；有人只查行数，有人只查空值；看板错了才发现「城市为空的用户被算进了地区榜」。
- **目标**：用质量六维度给规则分类，避免清单无结构。
- **先修**：`etl-checks`。
- **难度**：`??`
- **学完标准**：能把 ≥ 6 条具体规则映射到六维度；每维至少 1 条对着同源四表。

### 是什么

质量六维度（教学常用）：

| 维度 | 含义 | 四表示例 |
|---|---|---|
| 完整性 | 该有的在不在 | `orders.user_id` not null |
| 准确性 | 值是否正确 | paid 的 `amount >= 0` |
| 一致性 | 跨表/跨系统是否同口径 | 订单头金额 vs 明细合计 |
| 及时性 | 是否在 SLA 内到达 | 分区 `dt` 今日已产出 |
| 唯一性 | 主键/业务键不重复 | `orders.order_id` unique |
| 有效性 | 落在允许域 | `status ∈ {paid,created,cancelled}` |

- **引用**：清单案例见 `etl-checks`；仓侧对账见 `dwh-reconcile`。

### 怎么写

1. 从 `etl-checks` 已有检查中各抽例子。  
2. 为六维各写 1 条「规则名 + 维度 + 对象表」。  
3. 标出哪些是阻断、哪些是告警（本叶只分类，分级细节见第三叶）。  
4. 用宪法行数核对完整性：`users=4`、`orders=8`。  
5. 有效性：统计 `orders.status` 非法值个数应为 0。

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 只用行数当质量 | 漏逻辑错误 | 六维都要覆盖 |
| 把一致性当成准确性 | 改错方向 | 跨表问题归一致性 |
| 维度写了但无可执行断言 | 无法落地 | 每维绑定可机跑检查 |

### 动手

1. 输出 6 行表：维度 | 规则名 | 针对表.列 | 期望。  
2. 在本地对宪法 `orders` 断言：`status` 的 distinct 集合 ⊆ `{paid,created,cancelled}`，非法行数 = **0**。  
3. 唯一性：`orders.order_id` 重复数 = **0**；完整性：`user_id` 空值数 = **0**。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 六维表 | 正好 6 行且维名不重复 |
| 非法 status | 0 行 |
| 重复 order_id | 0 |
| 引用 | 出现 `etl-checks` |


## etl-dq-rules

### 课前

- **场景**：新增一条规则要改 Python/SQL 代码发版；规则太多误报，没人看告警；不知道如何表达 `accepted_values` / `range`。
- **目标**：把规则写成 YAML/JSON 配置，并映射到 Great Expectations / dbt tests / Deequ 的断言类型。
- **先修**：`etl-dq-dimensions`；`etl-tool-dbt`。
- **难度**：`???`
- **学完标准**：能写 ≥ 5 条 YAML 规则覆盖 not_null/unique/accepted_values/range/custom；能指出与 dbt/GE 的对应名。

### 是什么

- **规则即配置**：规则数据与作业代码分离，新增规则改配置不改代码（理想态）。  
- **常见断言类型**：

| 断言 | 含义 | 对应（示意） |
|---|---|---|
| not_null | 非空 | dbt `not_null` / GE `expect_column_values_to_not_be_null` |
| unique | 唯一 | dbt `unique` / GE unique |
| accepted_values | 枚举 | dbt `accepted_values` |
| range | 区间 | GE `expect_column_values_to_be_between` |
| custom | SQL/函数 | dbt singular test / GE query |

- **引用**：`etl-checks`（清单落地处）、`etl-tool-dbt`（测试承载）、`dwh-reconcile`（跨系统对账常为 custom）。

### 怎么写

1. 为 `orders` 写 YAML 规则集（见下）。  
2. 伪引擎：读取 YAML → 在 DataFrame/SQL 上执行 → 产出 `passed/failed/row_count`。  
3. 把「源订单元金额 vs 明细合计」写成 custom SQL（一致性）。  
4. 标明每条规则的严重级别字段（`block`/`warn`），本叶先占位。  
5. **不要**安装 GE；允许伪代码。

```yaml
# dq_orders.yml（示例）
dataset: orders
rules:
  - id: orders_pk
    type: unique
    column: order_id
    severity: block
  - id: orders_user_not_null
    type: not_null
    column: user_id
    severity: block
  - id: orders_status_domain
    type: accepted_values
    column: status
    values: [paid, created, cancelled]
    severity: block
  - id: orders_amount_range
    type: range
    column: amount
    min: 0
    max: 1000000
    severity: warn
  - id: orders_vs_items
    type: custom
    sql: |
      SELECT COUNT(*) AS bad
      FROM orders o
      LEFT JOIN (
        SELECT order_id, SUM(price*qty) AS item_amt
        FROM order_items GROUP BY order_id
      ) i ON i.order_id = o.order_id
      WHERE o.status='paid' AND o.amount IS NOT NULL
        AND ABS(COALESCE(i.item_amt,0) - o.amount) > 0.01
    expect_bad_eq: 0
    severity: warn
```

```python
# 伪代码：执行 accepted_values
def assert_accepted(df, col, values):
    bad = df[~df[col].isin(values)]
    return {"failed": len(bad), "passed": len(bad)==0}
```

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 规则全写 block | 管道瘫痪 | 分级（见下一叶） |
| custom SQL 无 `expect_bad_eq` | 无法自动判 | 必须有期望值 |
| 配置与表名飘了 | 假通过 | dataset 与真实表绑定 |

### 动手

1. 提交一份 ≥ 5 条规则的 YAML（可复制上文并改 id）。  
2. 在宪法 `orders` 上跑 not_null(user_id)、unique(order_id)、accepted_values(status)：失败行数均为 **0**。  
3. 写 dbt 对应：列出至少 3 个 `schema.yml` 测试名与 YAML `type` 的对照表。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| YAML 规则 | ≥ 5 且含 5 种 type |
| 三断言失败行 | 均为 0 |
| 对照表 | ≥ 3 行映射到 dbt/GE |
| 引用 | 出现 `etl-tool-dbt`、`etl-checks` |


## etl-dq-pipeline

### 课前

- **场景**：质量问题发现太晚，下游看板已错；规则太多误报没人看；不知道哪些该阻断发布、哪些只告警。
- **目标**：把规则引擎接入管道：在何处跑、失败如何分级、如何与重跑/回刷协同。
- **先修**：前两叶；`dwh-reconcile`；幂等主树意识（ETL 主树，见主树规则）。
- **难度**：`???`
- **学完标准**：能画出「抽取→变换→DQ→装载/发布」门禁点；给出阻断/告警各 ≥ 2 条；能说明误报治理策略。

### 是什么

- **门禁**：质量检查作为管道节点，失败可 **block**（阻止下游）或 **warn**（告警继续）。  
- **接入点**：源到 ODS 后、DWD 发布前、ADS/对外前（至少一处 block）。  
- **分级策略（示例）**：

| 级别 | 典型规则 | 动作 |
|---|---|---|
| block | PK 唯一、status 枚举、user_id not null | 失败则停止发布 |
| warn | amount 范围、头明细差额 | 告警工单，可带条件放行 |
| info | 行数波动 | 仅记录 |

- **与工具**：dbt test 可放在 transform 后（`etl-tool-dbt`）；对账类 custom 对齐 `dwh-reconcile`。  
- **引用**：`etl-checks`、`etl-tool-dbt`、`dwh-reconcile`。

### 怎么写

1. 画管道：Extract → Load ODS → Transform DWD → **DQ gate** → Publish ADS。  
2. 为宪法四表分配：ODS 后跑唯一/非空；发布前跑对账 custom。  
3. 定义误报治理：连续 3 天同 warn 升级评审；白名单需双人审批。  
4. 失败输出：`dq_result.json` 含 rule_id、failed_rows、severity、sample_keys。  
5. 重跑：block 修复后从失败节点重跑（幂等，不在此展开 CDC 全文）。

```text
伪流程：
run_transform()
rs = run_dq("dq_orders.yml")
if any(r.severity=="block" and not r.passed for r in rs):
    emit_alert(rs); fail_job()
else:
    publish()
    emit_alert([r for r in rs if r.severity=="warn" and not r.passed])
```

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 全部 warn | 等于没门禁 | 主键/枚举必须 block |
| 全部 block | 业务停摆 | 范围类先 warn |
| 告警无样本主键 | 无法修数 | 输出 `order_id` 样例 ≤ 20 个 |
| DQ 在看板之后 | 太晚 | 前移到发布前 |

### 动手

1. 写出门禁点位图（≥ 3 个阶段）并为每阶段标注 block/warn 规则数（数字）。  
2. 给定模拟结果：`unique` failed=0，`range` failed=2，`custom` failed=0——判断作业是否应 block，并说明原因。  
3. 生成一份伪 `dq_result`：至少 2 条记录，含 `rule_id, failed_rows, severity, sample_keys`；`sample_keys` 长度 ≤ 20。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 阶段门禁 | ≥ 3 阶段且每阶段有规则计数 |
| 案例判断 | 明确是否 block + 1 句理由 |
| dq_result | ≥ 2 条且字段齐全 |
| 引用 | 出现 `dwh-reconcile`、`etl-checks`、`etl-tool-dbt` |
