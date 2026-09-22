# -*- coding: utf-8 -*-
"""Add root-node '与相邻树的关系' sections; sync kg-data mirrors."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"D:\cursor\数据学习平台")
KG = ROOT / "kg-data"
LESSONS = ROOT / "_gen" / "lessons"
RULE_MD = KG / "知识点主树规则.md"

MIRRORS = [
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\kg-data"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\kg-data"),
]
HTMLS = [
    ROOT / "数据知识图谱.html",
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\learn.html"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\learn.html"),
]

HUB_MAP = {
    "sql": "hub-query.json",
    "bi": "hub-viz.json",
    "python": "hub-python.json",
    "database": "hub-database.json",
    "ml": "hub-ml.json",
    "etl": "hub-etl.json",
    "dwh": "hub-dwh.json",
}

SECTIONS = {
    "sql": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（SQL）与 **数据库 / ETL / DWH** 共享部分机制类知识点。SQL **不是**下列主题的主树，只保留业务侧切片：

| 知识点 | 以谁为主 | 本树（SQL）只保留 |
|---|---|---|
| 事务 / 隔离 / 锁 | **数据库** | 业务侧事务写法（`BEGIN/COMMIT`、支付与事件同事务） |
| 索引 / EXPLAIN / 统计信息 | **数据库** | 业务侧索引改写与读 `EXPLAIN` 结论 |
| 增量 / CDC / 幂等写入 | **ETL** | `UPSERT` / `MERGE` 语法 |
| 分区 / 裁剪 | **DWH** | （查询中命中分区的写法可点到为止，机制回指 DWH） |
| SCD | **DWH** | 本树不展开维表理论 |

另：指标字段口径以 SQL 宪法页「全平台指标口径映射表」为准；与 BI Superstore 对照也在该表。
""".strip(),
    "bi": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（BI）主要消费 **SQL / DWH** 已对齐的业务口径与汇总结果，**不担任**「事务 / 索引 / CDC / SCD / 分区」等机制主题的主树。

| 关系 | 说明 |
|---|---|
| 与 SQL | 指标口径、支付 GMV 等以 SQL 宪法映射表为准；Superstore 字段在映射表中对照 |
| 与 DWH | 看板取数优先已发布的汇总/集市；分区与 SCD 机制回指 DWH |
| 与 ETL | 不在本树重讲增量作业；刷新依赖调度结果 |
| 与 数据库 | 不在本树重讲锁与隔离 |

本树主责：可视化语法、计算（含 LOD）、仪表板与交互；机制类主题请转到对应主树。
""".strip(),
    "python": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（Python）与 SQL / 数据库 / 数仓 **同源四表**，负责 DataFrame 侧用法；**不担任**「事务 / 索引 / CDC / SCD / 分区」主树。

| 关系 | 说明 |
|---|---|
| 与 SQL | 同口径 diff；复杂集合运算可对照 SQL，机制不改写 |
| 与 ETL / DWH | 仓内增量、SCD、分区回刷回指 ETL/DWH；本树可做小样本原型 |
| 与 数据库 | 连接与事务边界以数据库树为准 |

本树主责：pandas 清洗聚合、可视化与原型；跨树机制主题按主树规则学习。
""".strip(),
    "database": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（数据库）是下列知识点的 **主树**：

| 本树为主 | 从树如何收敛 |
|---|---|
| 事务 / 隔离 / 锁 | SQL 只保留业务侧事务写法 |
| 索引 / EXPLAIN / 统计信息 | SQL 只保留业务侧索引改写 |

本树为 **从** 的知识点：

| 知识点 | 主树 | 本树只保留 |
|---|---|---|
| 分区 / 裁剪 | **DWH** | 分区表 DDL / 引擎语法；分析型裁剪与回刷语义回指 DWH |

与 ETL：连接、权限、备份等工程能力可协作，但不在本树重写 CDC 作业语义（CDC 主树为 ETL）。
""".strip(),
    "ml": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（机器学习 / 算法）消费特征与样本，**不担任**「事务 / 索引 / CDC / SCD / 分区」主树。

| 关系 | 说明 |
|---|---|
| 与 SQL / Python | 取数与特征原型可同源四表；指标口径回指 SQL 宪法映射表 |
| 与 DWH | 训练样本优先用已治理的明细/汇总；SCD 与分区机制回指 DWH |
| 与 ETL | 特征定时生产属作业范畴时回指 ETL |

本树主责：范式、特征、模型、评估与落地；工程机制类主题按主树规则转到 DB / ETL / DWH。
""".strip(),
    "etl": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（ETL）是下列知识点的 **主树**：

| 本树为主 | 从树如何收敛 |
|---|---|
| 增量 / CDC / 幂等写入 | SQL 只保留 UPSERT 语法；DWH 只保留分区回刷 |

本树为 **从** 的知识点：

| 知识点 | 主树 | 本树只保留 |
|---|---|---|
| SCD / 缓慢变化维 | **DWH** | 日批闭链步骤（开链/闭链顺序），理论回指 DWH |
| 分区 / 裁剪 | **DWH** | 分区覆盖写入；裁剪与策略回指 DWH |

与数据库：抽取连接与权限协作，锁/隔离机制以数据库树为准。
""".strip(),
    "dwh": """
## 与相邻树的关系

> 全平台知识点主从规则见：`kg-data/知识点主树规则.md`。

本树（数据仓库）是下列知识点的 **主树**：

| 本树为主 | 从树如何收敛 |
|---|---|
| SCD / 缓慢变化维 | ETL 只保留日批闭链步骤 |
| 分区 / 裁剪 | ETL 只保留分区覆盖写入；数据库只保留分区表 DDL |

本树为 **从** 的知识点：

| 知识点 | 主树 | 本树只保留 |
|---|---|---|
| 增量 / CDC / 幂等写入 | **ETL** | 分区回刷（按 `dt` 重跑/覆盖）；CDC 语义回指 ETL |

与 SQL / BI：指标口径回指 SQL 宪法映射表；本树提供可发布的汇总与维表，不替代机制主树职责。
""".strip(),
}


def sync(name: str, tree: dict):
    compact = json.dumps(tree, ensure_ascii=False, separators=(",", ":"))
    pretty = json.dumps(tree, ensure_ascii=False, indent=2)
    (KG / f"{name}.json").write_text(compact, encoding="utf-8")
    if LESSONS.exists():
        (LESSONS / f"{name}.json").write_text(pretty, encoding="utf-8")
    hub = HUB_MAP.get(name)
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
        shutil.copy2(RULE_MD, mirror / RULE_MD.name)


def upsert_section(content: str, section: str) -> str:
    marker = "## 与相邻树的关系"
    if marker in content:
        # replace from marker to EOF-ish: until next ## at start or end
        i = content.find(marker)
        rest = content[i + len(marker) :]
        m = re.search(r"\n## ", rest)
        if m:
            end = i + len(marker) + m.start()
            return content[:i].rstrip() + "\n\n" + section + "\n" + content[end:]
        return content[:i].rstrip() + "\n\n" + section + "\n"
    return content.rstrip() + "\n\n" + section + "\n"


def main():
    if not RULE_MD.exists():
        raise SystemExit("missing rule md")
    for name, section in SECTIONS.items():
        path = KG / f"{name}.json"
        tree = json.loads(path.read_text(encoding="utf-8"))
        assert str(tree.get("id", "")).endswith("-root") or tree.get("id") in {
            "sql-root",
            "bi-root",
            "python-root",
            "db-root",
            "ml-root",
            "etl-root",
            "dwh-root",
        }, tree.get("id")
        before_kids = json.dumps([c.get("id") for c in (tree.get("children") or [])], ensure_ascii=False)
        tree["content"] = upsert_section(tree.get("content") or "", section)
        after_kids = json.dumps([c.get("id") for c in (tree.get("children") or [])], ensure_ascii=False)
        assert before_kids == after_kids
        sync(name, tree)
        print("root patched", name, tree.get("id"), "len", len(tree["content"]))

    for html in HTMLS:
        if not html.exists():
            continue
        t = html.read_text(encoding="utf-8")
        t2 = re.sub(r'const KG_DATA_VER = "[^"]+"', 'const KG_DATA_VER = "20260922b"', t, count=1)
        html.write_text(t2, encoding="utf-8")

    # export snippets for chat
    snip = ROOT / "_gen" / "master_tree_root_snippets.md"
    parts = ["# 7 个根节点新增章节（可粘贴）\n"]
    for name, section in SECTIONS.items():
        parts.append(f"\n## {name}-root\n\n```markdown\n{section}\n```\n")
    snip.write_text("\n".join(parts), encoding="utf-8")
    print("snippets", snip)


if __name__ == "__main__":
    main()
