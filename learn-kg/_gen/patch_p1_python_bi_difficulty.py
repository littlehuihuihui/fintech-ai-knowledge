# -*- coding: utf-8 -*-
"""P1: Python error/log leaf, BI semantic layer, difficulty dictionary."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"D:\cursor\数据学习平台")
KG = ROOT / "kg-data"
LESSONS = ROOT / "_gen" / "lessons"
MIRRORS = [
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\kg-data"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\kg-data"),
]
HTMLS = [
    ROOT / "数据知识图谱.html",
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\learn.html"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\learn.html"),
]
HUB = {
    "sql": "hub-query.json",
    "bi": "hub-viz.json",
    "python": "hub-python.json",
    "database": "hub-database.json",
    "ml": "hub-ml.json",
    "etl": "hub-etl.json",
    "dwh": "hub-dwh.json",
}

DIFF_REF = (
    "> **难度判定标准见** `kg-data/难度词典.md`（`?` / `??` / `???` 统一词典；跨树同知识点难度以该文件为准）。"
)

PY_LEAF = r'''### 课前

- **场景**：读取 `orders.csv` 时文件不存在；`to_sql` 写入时数据库连接断开；清洗 `amount` 列遇到非法字符串 `"N/A"`；脚本失败后要留下可排查日志。
- **目标**：能用 `try/except/finally` + `logging` 写出可重跑、可定位的生产向小脚本；区分内置异常与自定义异常。
- **先修**：Python 教程宪法（同源四表）；`DataFrame` 读写基础；工程化前序叶课可并行。
- **难度**：`??`（L4 工程切片；判定见 `kg-data/难度词典.md`）
- **学完标准**：
  1. 文件缺失时不 Traceback 裸奔，而是记录 ERROR 并返回可预期退出码/空结果约定
  2. `amount` 非法值被隔离并记入日志，合法行 `shape` 可核对
  3. 日志文件至少含时间、级别、模块、消息四要素

### 是什么

- **一句话定义**：异常处理决定「失败时程序怎么停」；日志决定「事后怎么复盘」。
- **核心要素**：
  - `try/except/finally`：捕获、分支、必定清理（关连接/关文件）
  - 内置异常（`FileNotFoundError` / `ValueError` / `OperationalError`）vs 自定义异常（业务语义，如 `AmountParseError`）
  - `logging`：级别（DEBUG/INFO/WARNING/ERROR）、格式、输出到文件
- **边界**：笔记本里临时 `print` 不等于生产日志；吞掉所有异常（`except Exception: pass`）会让管道「假成功」。
- **与数据管道**：失败必须可定位、可重跑（幂等写入主树在 ETL；本课只保证**脚本侧**留下证据）。

### 怎么写

建议步骤：

1. **先配日志**：`logging.basicConfig` 或 `FileHandler`，格式含 `asctime/levelname/name/message`，写入 `pipeline.log`。
2. **读文件包一层**：`Path("orders.csv")` 不存在 → 捕获 `FileNotFoundError`，`logger.error`，再决定退出或返回空表约定。
3. **清洗 amount**：对非法字符串不要让整表炸掉——逐值/`to_numeric(errors="coerce")`，统计变 NaN 的行数并 `WARNING`。
4. **写库包一层**：`to_sql` / DBAPI 捕获连接类异常，`finally` 里关闭连接；失败时不要半写入无日志。
5. **自定义异常**：业务规则（如「paid 订单 amount 不得为空」）抛 `AmountParseError`，外层统一转成 ERROR 日志。

```python
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("orders_job")

class AmountParseError(ValueError):
    """业务：金额字段无法解析为数值。"""

def load_orders(path="orders.csv"):
    p = Path(path)
    try:
        df = pd.read_csv(p)
        log.info("loaded orders path=%s shape=%s", p, df.shape)
        return df
    except FileNotFoundError:
        log.error("orders file missing: %s", p.resolve())
        raise
    finally:
        log.debug("load_orders finished attempt path=%s", p)

def coerce_amount(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    out = df.copy()
    out["amount_num"] = pd.to_numeric(out["amount"], errors="coerce")
    bad = int(out["amount_num"].isna().sum() - out["amount"].isna().sum())
    # 上面在全空时需按实际样例调整；样例用非法字符串计数：
    bad = int((out["amount"].notna() & out["amount_num"].isna()).sum())
    if bad:
        log.warning("amount coerce failed rows=%s / %s", bad, before)
    return out
```

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| `except: pass` 或裸 `except Exception` 后继续跑 | 管道假成功，下游用脏数据 | 按异常类型分支；未知异常 ERROR 后抛出或失败退出 |
| 只用 `print` 当日志 | 无级别、无时间、难检索 | 使用 `logging`，至少 INFO/ERROR，输出到文件 |
| 自定义异常却不记录上下文（行号/order_id） | 无法定位坏行 | 日志带 `order_id` / 行号 / 原始值 |
| `finally` 里又写业务逻辑且可能再抛错 | 掩盖原始异常 | `finally` 只做资源清理 |

### 动手

同源四表：`users` / `orders` / `order_items` / `order_events`（先按宪法构造，再可选 `orders.to_csv("orders.csv", index=False)`）。

**题 1（文件不存在）**  
调用 `load_orders("orders_missing.csv")`：必须留下一条 ERROR 日志，且异常类型为 `FileNotFoundError`。验收：`pipeline.log` 中 ERROR 行数 ≥ 1，且包含文件名 `orders_missing.csv`。

**题 2（非法 amount + 连接失败模拟）**  
在内存 `orders` 中把某一行 `amount` 改成 `"N/A"`，跑 `coerce_amount`：  
- `amount_num` 为 NaN 的「由非法串导致」行数 = **1**  
- 日志中 WARNING 含 `amount coerce failed rows=1`  
再用一个假连接函数（`raise ConnectionError("db down")`）包在 `try/except/finally`：必须 ERROR 记录 `db down`，且 `finally` 中执行 `log.info("connection closed")`（各 ≥ 1 次）。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 日志格式 | `pipeline.log` 每行匹配：时间 \| 级别 \| 名称 \| 消息 |
| 缺文件 | ERROR ≥ 1，含路径片段 `orders_missing` |
| 非法金额 | 由 `"N/A"` 导致的 NaN = 1；WARNING 含 `rows=1` |
| finally | 模拟断连后出现 `connection closed` INFO ≥ 1 |
| 自定义异常 | `AmountParseError` 为 `ValueError` 子类（`issubclass` 为 True） |
'''

BI_CHAPTER = r'''### 课前 · 章节导读

- **章节**：语义层与指标体系
- **为什么学**：企业里同一指标被各人各写一遍就会口径漂移；语义层把「指标定义」从单张报表里抽离出来。
- **学习目标**：能定义可复用指标、区分原子/派生/复合、指出权威（认证）数据集；并回指全平台口径与数仓 SSOT。
- **先修**：BI 教程宪法；SQL 宪法页「全平台指标口径映射表」；DWH「SSOT 单一事实来源」相关叶课。
- **难度**：`??`（见 `kg-data/难度词典.md`）

### 本节地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | 指标定义与复用 | ?? | 指标只定义一次，报表只引用 |
| 2 | 原子/派生/复合指标 | ?? | 毛利率等必须拆清分子分母 |
| 3 | 认证数据集 | ?? | 新人只连「已认证」的权威集 |

### 推荐顺序

```text
指标定义与复用 → 原子/派生/复合指标 → 认证数据集
```

### 强制引用

1. **指标字段与跨树写法**：以 `SQL.学习路径.教程宪法.统一样例与课模板` 中的「全平台指标口径映射表」为准（`amount` ↔ `Sales` 等）。  
2. **单一事实来源**：以 DWH 树 SSOT / 单一事实来源相关叶课为准；语义层是消费侧契约，不另起炉灶改数。

### 验收（章级）

| 检查 | 标准 |
|---|---|
| 三叶都完成动手 | 每叶验收表勾选通过 |
| 口述 | 能说明「语义层 vs 单图私有计算」差别 |
| 引用 | 能指出口径表与 SSOT 各一条 |

### 下一动

从「指标定义与复用」开始。本章 **3** 片叶讲义。
'''

BI_LEAF_1 = r'''### 课前

- **场景**：同一「销售额/GMV」在三人的报表里各写一遍，有人含未支付，有人没 `COALESCE`，周会数字对不上。
- **目标**：把指标定义成可复用对象（名称、口径、表达式、责任人），报表只引用不改写。
- **先修**：BI 宪法；SQL 宪法「全平台指标口径映射表」。
- **难度**：`??`
- **学完标准**：能写出 GMV 的一页定义卡，并指出与映射表一致；能列出至少 2 个「禁止私自改口径」的检查项。

### 是什么

- **一句话定义**：语义层里的指标是**共享度量**，不是某张工作表上的临时字段。
- **核心要素**：业务名称、口径文字、技术表达式（SQL/DAX/Tableau）、维度兼容、认证状态。
- **边界**：语义层不替代数仓建模；数从哪来仍服从 DWH SSOT。
- **引用**：字段级对照见 SQL 宪法映射表（`orders.amount` / Superstore `Sales`）。

### 怎么写

1. 从映射表锁定业务概念「销售额/GMV」→ 四表字段 `orders.amount` + `status='paid'`。  
2. 写口径文案：「仅支付成功订单，amount 空视作 0」。  
3. 落技术表达式（SQL 示例）：`SUM(CASE WHEN status='paid' THEN COALESCE(amount,0) ELSE 0 END)`。  
4. 在 BI 侧只引用该度量（Tableau 计算 / Power BI 度量），禁止在图上再改 IF。  
5. 登记责任人与认证状态（草稿/已认证）。

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 每张图复制粘贴一个「销售额」计算 | 口径漂移 | 一处定义，多处引用 |
| 忽略映射表，把 Superstore `Sales` 当成含未支付的 amount | 跨树对账失败 | 先声明样本是否等价 paid |
| 口径只写在聊天记录 | 新人找不到 | 定义卡进语义层/指标字典 |

### 动手

1. 基于同源 `orders`（8 行样例），按支付口径计算 GMV：Ada（user_id=1）的支付 GMV 应为 **350**（与 SQL 宪法种子一致：`80+120+120+30` 视你构造；若用平台宪法四表，按宪法页 Ada 支付 GMV=**350** 核对）。  
2. 写一张「GMV 定义卡」Markdown，含：业务名、口径、SQL 表达式、BI 引用方式、责任人；并粘贴映射表链接句。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| Ada 支付 GMV | 数值 = **350**（宪法四表） |
| 定义卡字段 | ≥ 5 项：名称/口径/表达式/引用方式/责任人 |
| 禁止项 | 定义卡中明确写「报表内不得改写 IF 过滤支付状态」 |
'''

BI_LEAF_2 = r'''### 课前

- **场景**：业务要「毛利率」，A 报表用 `AVG(利润/销售额)`，B 报表用 `SUM(利润)/SUM(销售额)`，结果差出好几个百分点。
- **目标**：会拆分原子 / 派生 / 复合指标，并规定毛利率必须用「先汇总再相除」。
- **先修**：指标定义与复用；SQL/BI 基础聚合。
- **难度**：`??`
- **学完标准**：能给「订单数、GMV、毛利率」标注类型；能指出错误毛利率算法并改正。

### 是什么

- **原子指标**：不可再拆的度量，如订单数 `COUNT(order_id)`、GMV（支付口径）。  
- **派生指标**：原子 + 统计或过滤，如「取消订单数」。  
- **复合指标**：由多个指标运算，如毛利率 = 利润 / GMV（必须先汇总）。  
- **边界**：比率类禁止「行上算比率再平均」；与映射表中 GMV 口径绑定。  
- **引用**：分子分母字段最终仍落到映射表与 DWH SSOT。

### 怎么写

1. 列出原子：订单数、支付 GMV、利润（若有 `profit`/`Profit`）。  
2. 标注复合：毛利率。  
3. 规定计算序：`SUM(profit) / NULLIF(SUM(gmv),0)`。  
4. 在语义层同时发布「禁止 AVG(行利率)」。  
5. 用样例数手算一行验收。

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| `AVG([利润]/[销售额])` | 被小单扭曲 | `SUM(利润)/SUM(销售额)` |
| 复合指标分子分母口径不一致（利润含税、GMV 不含） | 看似合理实则不可比 | 分子分母同认证、同过滤 |
| 把派生指标再当原子乱拼 | 重复过滤 | 类型标签进指标字典 |

### 动手

用宪法 `orders`：设演示利润列（若无利润，用 `amount * 0.25` 作为 `profit_est` 仅本练习）。  
1. 错误算法：对 paid 行算 `mean(profit_est/amount)`。  
2. 正确算法：`sum(profit_est)/sum(amount)`（paid，amount 空作 0）。  
写出两数差值绝对值 ≥ **0.01** 即视为演示成功（若样例恰好接近，再改一行 amount 放大差异）。  
3. 给三个指标打标签：订单数=原子，取消订单数=派生，毛利率=复合。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 类型标注 | 3 个指标标签正确 |
| 正确毛利率公式 | 使用 SUM/SUM 或等价，而非 AVG(行比率) |
| 差异演示 | 错误 vs 正确至少差 0.01，或说明样例行级改动 |
'''

BI_LEAF_3 = r'''### 课前

- **场景**：新同事入职，文件夹里一堆「最终版_真的最终_v3」数据集，不知道连哪个。
- **目标**：建立「认证数据集」制度：权威来源、认证状态、可用指标列表、责任人。
- **先修**：前两叶；DWH SSOT。
- **难度**：`??`
- **学完标准**：能写一份认证清单（名称、状态、SSOT 映射、允许指标 ≥ 3 个）；能说明未认证集禁止上生产看板。

### 是什么

- **一句话定义**：认证数据集是企业约定的**唯一推荐消费面**（表或语义模型），不是个人抽取。  
- **核心要素**：数据集 ID/名称、认证等级（草稿/已认证/退役）、映射到的 SSOT 表、可用指标、刷新 SLA、责任人。  
- **边界**：认证不保证数据永远对，但保证「出问题找得到人、改得动一处」。  
- **引用**：指标口径 → SQL 宪法映射表；事实/维表权威 → DWH SSOT。

### 怎么写

1. 盘点：列出候选集（个人抽取 / 部门库 / 仓内 ADS）。  
2. 对照 SSOT：只有映射到仓内发布主题的才能申请认证。  
3. 绑定指标：GMV、订单数、用户数必须来自映射表口径。  
4. 打标：`certified=true`，写入责任人与更新日期。  
5. 治理：未认证集可学习，不可直接挂生产仪表板。

### 易错对照

| 错法 | 后果 | 纠正 |
|---|---|---|
| 认证了含未支付的宽表还叫 GMV | 名称与口径冲突 | 认证前核对映射表 |
| 多人认证多份「官方」 | SSOT 名存实亡 | 一主题一认证集 |
| 只有名没有责任人 | 坏了无人修 | 责任人必填 |

### 动手

1. 起草认证记录一行：`ads_trade_paid_daily`（示例名），状态=已认证，SSOT= DWH 交易主题，允许指标=`GMV,订单数,用户数`。  
2. 写一条门禁：生产仪表板数据源必须 `认证状态=已认证`，否则驳回。  
3. 指出若有人用 Superstore 私有抽取做「官方 GMV」，应驳回并指向映射表 + SSOT。

### 验收

| 检查项 | 可量化标准 |
|---|---|
| 认证记录字段 | ≥ 6：名称/状态/SSOT/指标列表/责任人/日期 |
| 允许指标 | 恰好包含 GMV、订单数、用户数 3 个名 |
| 门禁句 | 明确「未认证不得上生产」 |
'''

DIFF_MD = r'''# Data Nexus · 难度词典

> **适用**：全平台 7 棵树（SQL / BI / Python / 数据库 / ML / ETL / DWH）  
> **标记**：`?` 初级 · `??` 中级 · `???` 高级  
> **原则**：难度看「学完独立上手的成本」，不是看标题炫不炫；跨树同一知识点必须同级。

---

## 1. 判定标准（不是凭感觉）

对每个知识点打三维分（各 1–3 分），再汇总：

| 维度 | 1 分 | 2 分 | 3 分 |
|---|---|---|---|
| 前置知识量 | 本树前 1–2 节即可 | 需跨 1 个相邻主题 | 需跨树或多机制叠加 |
| 概念抽象度 | 可直接映射到一行语法 | 需模型（粒度/窗口/状态） | 需引擎或体系语义（优化器/时点/版本） |
| 工程复杂度 | 单机可验证 | 需约定口径与边界 | 需重跑/并发/物理存储等生产约束 |

**汇总规则**：

| 总分 | 难度 |
|---|---|
| 3–4 | `?` |
| 5–6 | `??` |
| 7–9 | `???` |

**并列时**：优先抬高「工程复杂度」；涉及资金口径 / 重跑 / 并发 → 至少 `??`。

---

## 2. 使用纪律

1. 新叶讲义必须标 `level` 为 `?` / `??` / `???`（或 `L0–L1`→`?`，`L2–L4`→`??`，`L5+`→`???`，并与本表冲突时以本表为准）。  
2. 同一知识点在从树切片中的难度不得高于主树完整课（可同级或仅作导读不标更高）。  
3. 修改本表后，回头抽查对照表内条目在各树的标记是否一致。

---

## 3. 全平台高频知识点难度对照表

| 知识点 | 统一难度 | 理由（三维直觉） |
|---|---|---|
| SQL JOIN | ?? | 需理解粒度与连接类型 |
| SQL 窗口函数 | ?? | 需理解分区与排序 |
| SQL 索引失效 | ??? | 需理解 B 树与优化器 |
| Python groupby | ?? | 需理解分组语义 |
| Python transform | ??? | 需理解索引对齐 |
| Python 异常处理 | ?? | 需理解错误传播 |
| ETL 幂等写入 | ??? | 需理解重跑语义 |
| ETL CDC | ??? | 需理解日志与乱序 |
| DWH SCD2 | ??? | 需理解时点关联 |
| DWH 分区裁剪 | ??? | 需理解物理存储 |
| BI LOD.FIXED | ??? | 需理解聚合上下文 |
| DB MVCC | ??? | 需理解版本链 |
| DB 行锁与死锁 | ??? | 需理解等待环 |
| SQL 基础 SELECT/WHERE | ? | 前置少、抽象低 |
| BI 柱状图/饼图入门 | ? | 操作路径短 |
| 指标语义层（定义/认证） | ?? | 需口径与治理，但不碰引擎内核 |

---

## 4. 与主树规则、口径表的关系

- **知识点主从**：`kg-data/知识点主树规则.md`  
- **指标字段口径**：SQL 宪法页「全平台指标口径映射表」  
- **本文件**：只统一「难不难」，不定义主从、不定义字段。

（完）
'''


def find(n, nid):
    if n.get("id") == nid:
        return n
    for c in n.get("children") or []:
        h = find(c, nid)
        if h:
            return h
    return None


def sync(name: str, tree: dict):
    compact = json.dumps(tree, ensure_ascii=False, separators=(",", ":"))
    pretty = json.dumps(tree, ensure_ascii=False, indent=2)
    (KG / f"{name}.json").write_text(compact, encoding="utf-8")
    if LESSONS.exists():
        (LESSONS / f"{name}.json").write_text(pretty, encoding="utf-8")
    hub = HUB.get(name)
    if hub:
        (KG / hub).write_text(compact, encoding="utf-8")
    (KG / f"embed-{name}.js").write_text(
        'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {};\n'
        f'window.__KG_EMBEDDED["{name}"]={compact}\n',
        encoding="utf-8",
    )
    for mirror in MIRRORS:
        if not mirror.exists():
            continue
        (mirror / f"{name}.json").write_text(compact, encoding="utf-8")
        if hub:
            (mirror / hub).write_text(compact, encoding="utf-8")
        (mirror / f"embed-{name}.js").write_text(
            'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {};\n'
            f'window.__KG_EMBEDDED["{name}"]={compact}\n',
            encoding="utf-8",
        )


def ensure_unique(tree, nid):
    if find(tree, nid):
        raise SystemExit(f"id already exists: {nid}")


def patch_py_eng_map(content: str) -> str:
    # Update story, map, order, count — without touching other leaves' files
    content = content.replace(
        "性能与内存 → 可复现环境",
        "性能与内存 → 可复现环境 → 异常处理与日志",
    )
    old_map = """| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | 性能与内存 | ??? | CSV 太大把 pandas 撑爆内存。 |
| 2 | 可复现环境 | ??? | 同事复现你的笔记本结果不一致。 |"""
    new_map = """| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | 性能与内存 | ??? | CSV 太大把 pandas 撑爆内存。 |
| 2 | 可复现环境 | ??? | 同事复现你的笔记本结果不一致。 |
| 3 | 异常处理与日志 | ?? | 文件缺失、断连、脏 amount 时仍可定位可重跑。 |"""
    if old_map in content:
        content = content.replace(old_map, new_map)
    elif "异常处理与日志" not in content:
        # fuzzy: append row before 推荐顺序
        content = content.replace(
            "### 推荐顺序",
            "| 3 | 异常处理与日志 | ?? | 文件缺失、断连、脏 amount 时仍可定位可重跑。 |\n\n### 推荐顺序",
            1,
        )
    content = content.replace(
        "```text\n性能与内存 → 可复现环境\n```",
        "```text\n性能与内存 → 可复现环境 → 异常处理与日志\n```",
    )
    content = content.replace("合计约 **2** 片叶讲义", "合计约 **3** 片叶讲义")
    content = content.replace("约 **2** 片叶讲义", "约 **3** 片叶讲义")
    return content


def patch_py_path_mid(content: str) -> str:
    old = "pivot → transform/rolling → 时间索引 → 柱状/分布 → NumPy → DuckDB/Polars → 中级练习"
    new = "pivot → transform/rolling → 时间索引 → 柱状/分布 → NumPy → DuckDB/Polars → 异常处理与日志 → 中级练习"
    if "异常处理与日志" in content:
        return content
    if old in content:
        return content.replace(old, new)
    # fallback insert before 中级练习
    return content.replace("→ 中级练习", "→ 异常处理与日志 → 中级练习")


def upsert_diff_ref(content: str) -> str:
    if "难度词典.md" in content:
        return content
    return content.rstrip() + "\n\n" + DIFF_REF + "\n"


def main():
    # --- difficulty dictionary file ---
    diff_path = KG / "难度词典.md"
    diff_path.write_text(DIFF_MD.strip() + "\n", encoding="utf-8")
    for mirror in MIRRORS:
        if mirror.exists():
            shutil.copy2(diff_path, mirror / diff_path.name)

    # --- Python ---
    py = json.loads((KG / "python.json").read_text(encoding="utf-8"))
    eng = find(py, "py-eng")
    if not eng:
        raise SystemExit("py-eng missing")
    ensure_unique(py, "py-eng-error-log")
    leaf = {
        "id": "py-eng-error-log",
        "title": "异常处理与日志",
        "level": "??",
        "content": PY_LEAF.strip() + "\n",
        "children": [],
    }
    eng.setdefault("children", []).append(leaf)
    eng["content"] = patch_py_eng_map(eng.get("content") or "")
    eng["lessonParent"] = True
    mid = find(py, "py-path-mid")
    if not mid:
        raise SystemExit("py-path-mid missing")
    mid["content"] = patch_py_path_mid(mid.get("content") or "")
    sync("python", py)
    print("python: added py-eng-error-log; patched py-eng + py-path-mid")

    # --- BI semantic layer ---
    bi = json.loads((KG / "bi.json").read_text(encoding="utf-8"))
    for nid in (
        "BI.语义层",
        "BI.语义层.指标定义与复用",
        "BI.语义层.原子/派生/复合指标",
        "BI.语义层.认证数据集",
    ):
        ensure_unique(bi, nid)
    domain = {
        "id": "BI.语义层",
        "title": "语义层与指标体系",
        "level": "??",
        "content": BI_CHAPTER.strip() + "\n",
        "lessonParent": True,
        "children": [
            {
                "id": "BI.语义层.指标定义与复用",
                "title": "指标定义与复用",
                "level": "??",
                "content": BI_LEAF_1.strip() + "\n",
                "children": [],
            },
            {
                "id": "BI.语义层.原子/派生/复合指标",
                "title": "原子/派生/复合指标",
                "level": "??",
                "content": BI_LEAF_2.strip() + "\n",
                "children": [],
            },
            {
                "id": "BI.语义层.认证数据集",
                "title": "认证数据集",
                "level": "??",
                "content": BI_LEAF_3.strip() + "\n",
                "children": [],
            },
        ],
    }
    # insert after Tableau if present, else append
    kids = bi.setdefault("children", [])
    idx = next((i for i, c in enumerate(kids) if c.get("id") == "BI.Tableau"), None)
    if idx is None:
        kids.append(domain)
    else:
        kids.insert(idx + 1, domain)
    sync("bi", bi)
    print("bi: added BI.语义层 + 3 leaves")

    # --- root difficulty refs (all 7) ---
    for name in ("sql", "bi", "python", "database", "ml", "etl", "dwh"):
        tree = json.loads((KG / f"{name}.json").read_text(encoding="utf-8"))
        tree["content"] = upsert_diff_ref(tree.get("content") or "")
        sync(name, tree)
        print("root diff-ref", name, tree.get("id"))

    for html in HTMLS:
        if not html.exists():
            continue
        t = html.read_text(encoding="utf-8")
        t2 = re.sub(r'const KG_DATA_VER = "[^"]+"', 'const KG_DATA_VER = "20260922c"', t, count=1)
        html.write_text(t2, encoding="utf-8")

    # export snippets
    out = ROOT / "_gen" / "p1_snippets.md"
    out.write_text(
        "\n\n".join(
            [
                "# P1 产出片段",
                "## P1-1 py-eng-error-log\n\n" + PY_LEAF,
                "## P1-2 BI.语义层 章节导读\n\n" + BI_CHAPTER,
                "## P1-2 叶1\n\n" + BI_LEAF_1,
                "## P1-2 叶2\n\n" + BI_LEAF_2,
                "## P1-2 叶3\n\n" + BI_LEAF_3,
                "## P1-5 难度词典\n\n" + DIFF_MD,
                "## P1-5 根节点引用\n\n" + DIFF_REF,
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out)


if __name__ == "__main__":
    main()
