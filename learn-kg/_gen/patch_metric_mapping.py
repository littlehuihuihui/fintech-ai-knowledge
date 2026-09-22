# -*- coding: utf-8 -*-
"""Add platform metric口径 mapping to SQL constitution; cite it from 5 other constitutions."""
from __future__ import annotations

import json
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

SQL_ID = "SQL.学习路径.教程宪法.统一样例与课模板"
REF_LINE = (
    "> **指标口径以 SQL 宪法页为准**："
    "[SQL.学习路径.教程宪法.统一样例与课模板]"
    "（全平台指标口径映射表；本树不另立口径）。"
)

SQL_SECTION = r"""
## 全平台指标口径映射表

> **目的**：同一业务概念，在「订单四表」与 Superstore、以及 SQL / Python / BI 三种写法之间可对照。  
> **权威源**：本页。其余学科宪法只引用，不另立口径。  
> **验收种子**：暂留空，标记 `TODO: 待宪法页补齐`（数值种子后续统一回填）。

| 业务概念 | 订单四表字段 | Superstore 字段 | SQL 写法 | Python 写法 | BI 写法 | 验收种子 |
|---|---|---|---|---|---|---|
| 销售额 / GMV | `orders.amount`（支付口径：仅 `status='paid'`；空值按 0） | `Sales` | `SUM(CASE WHEN status='paid' THEN COALESCE(amount,0) ELSE 0 END)` | `orders.query("status=='paid'")['amount'].fillna(0).sum()` | Tableau：`SUM(IF [Order Status]="paid" THEN ZN([Amount]) END)`；若用 Superstore：`SUM([Sales])`；Power BI：`SUMX(FILTER(Orders, Orders[status]="paid"), COALESCE(Orders[amount],0))` | TODO: 待宪法页补齐 |
| 订单数 | `orders.order_id`（通常计行：`COUNT(*)`；去重：`COUNT(DISTINCT order_id)`） | `Order ID`（计数） | `COUNT(*)` 或 `COUNT(DISTINCT order_id)`（按是否可能重复选） | `orders['order_id'].nunique()` 或 `len(orders)` | Tableau：`COUNTD([Order ID])` 或 `SUM([Number of Records])`；Superstore 常用 `COUNTD([Order ID])` | TODO: 待宪法页补齐 |
| 用户数 | `users.user_id` / `orders.user_id` | `Customer ID` / `Customer Name` | 注册用户：`COUNT(DISTINCT user_id) FROM users`；下单用户：`COUNT(DISTINCT user_id) FROM orders` | `users['user_id'].nunique()`；下单用户：`orders['user_id'].nunique()` | Tableau：`COUNTD([Customer ID])`；订单侧：`COUNTD([User ID])` | TODO: 待宪法页补齐 |
| 支付状态 | `orders.status`（样例约定：`paid` / `created` / `cancelled`） | Superstore 无直接等价列；常用 `Order Status` 自定义，或用是否退货/`Profit` 场景近似，**不以退货代替支付** | `WHERE status = 'paid'` | `orders['status'].eq('paid')` / `.query("status=='paid'")` | Tableau 筛选：`[Order Status] = "paid"`；度量内：`IF [Order Status]="paid" THEN …` | TODO: 待宪法页补齐 |
| 城市 | `users.city`（可为 NULL） | `City` / `State` / `Region`（Superstore 地理层次；跨树对比时优先 `City`） | `u.city`；`LEFT JOIN users u ON u.user_id = o.user_id` | `users.merge(orders, on='user_id', how='left')['city']`；空城：`city.isna()` | Tableau：维度 `[City]`（Superstore）或关联用户表后的 `[City]`；空值单独成桶「未知」 | TODO: 待宪法页补齐 |
| 订单日期 | `orders.created_at`（TIMESTAMP） | `Order Date` | `DATE(created_at)` / `created_at::date`；筛选：`created_at >= DATE '2024-01-01'` | `pd.to_datetime(orders['created_at']).dt.date` | Tableau：`[Order Date]`（连续月份/精确日期）；订单四表模型：`[Created At]` 设为日期角色 | TODO: 待宪法页补齐 |

### 口径纪律（强制）

1. **GMV 默认支付口径**：未特别声明时，销售额/GMV = 仅 `paid`，并对 `amount` 做 `COALESCE(...,0)`。  
2. **不要把 Superstore 的 Sales 直接当成含未支付订单的 amount 全量**；对照时先声明「样本是否已等价于 paid」。  
3. **城市以 users.city 为准**；仅有订单表、无用户维时，禁止臆造城市字段。  
4. **日期用订单创建时间**（`orders.created_at` ↔ `Order Date`），不要把发货日/事件时间误当订单日。  
5. **验收种子**列统一回填前，各叶讲义可写「预期形态」，但跨树对账数字以本表补齐后的种子为准。
""".strip(
    "\n"
)

TARGETS = {
    "sql": SQL_ID,
    "bi": "BI.学习路径.教程宪法.统一样例与课模板",
    "python": "py-constitution",
    "database": "db-constitution",
    "etl": "etl-constitution",
    "dwh": "dwh-constitution",
}

HUB_MAP = {
    "sql": "hub-query.json",
    "bi": "hub-viz.json",
    "python": "hub-python.json",
    "database": "hub-database.json",
    "etl": "hub-etl.json",
    "dwh": "hub-dwh.json",
}


def find(n, nid):
    if n.get("id") == nid:
        return n
    for c in n.get("children") or []:
        hit = find(c, nid)
        if hit:
            return hit
    return None


def sync(name: str, tree: dict):
    compact = json.dumps(tree, ensure_ascii=False, separators=(",", ":"))
    pretty = json.dumps(tree, ensure_ascii=False, indent=2)
    (KG / f"{name}.json").write_text(compact, encoding="utf-8")
    if (LESSONS / f"{name}.json").parent.exists():
        (LESSONS / f"{name}.json").write_text(pretty, encoding="utf-8")
    hub = HUB_MAP.get(name)
    if hub:
        (KG / hub).write_text(compact, encoding="utf-8")
    embed = KG / f"embed-{name}.js"
    embed.write_text(
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


def main():
    snippets = {
        "sql_section": SQL_SECTION,
        "ref_line": REF_LINE,
    }
    for name, nid in TARGETS.items():
        tree = json.loads((KG / f"{name}.json").read_text(encoding="utf-8"))
        node = find(tree, nid)
        if not node:
            raise SystemExit(f"missing {name} {nid}")
        content = node.get("content") or ""
        if name == "sql":
            if "全平台指标口径映射表" in content:
                # refresh section: replace from ## heading to end or previous append
                idx = content.find("## 全平台指标口径映射表")
                content = content[:idx].rstrip() + "\n\n" + SQL_SECTION + "\n"
            else:
                content = content.rstrip() + "\n\n" + SQL_SECTION + "\n"
        else:
            if "指标口径以 SQL 宪法页为准" in content:
                # replace existing ref block line(s)
                lines = content.splitlines()
                out = []
                skip_blank_after = False
                for line in lines:
                    if "指标口径以 SQL 宪法页为准" in line:
                        continue
                    out.append(line)
                content = "\n".join(out).rstrip() + "\n\n" + REF_LINE + "\n"
            else:
                content = content.rstrip() + "\n\n" + REF_LINE + "\n"
        node["content"] = content
        sync(name, tree)
        print("patched", name, nid, "len", len(content))

    out_md = ROOT / "_gen" / "metric_口径_snippets.md"
    out_md.write_text(
        "# 可粘贴 Markdown 片段\n\n"
        "## 1) SQL 宪法页新增章节（完整）\n\n"
        + SQL_SECTION
        + "\n\n## 2) BI / Python / ETL / DWH / DB 宪法页各新增一行\n\n"
        + REF_LINE
        + "\n",
        encoding="utf-8",
    )

    for html in HTMLS:
        if not html.exists():
            continue
        t = html.read_text(encoding="utf-8")
        import re

        t2 = re.sub(
            r'const KG_DATA_VER = "[^"]+"',
            'const KG_DATA_VER = "20260922a"',
            t,
            count=1,
        )
        html.write_text(t2, encoding="utf-8")

    print("snippets", out_md)
    return snippets


if __name__ == "__main__":
    main()
