#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""系统扫描7大领域核心内容是否齐全"""

import json, re, os

data_dir = r"D:\cursor\数据学习平台\kg-data"

def load_domain(domain):
    filepath = os.path.join(data_dir, f"embed-{domain}.js")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'window\.__KG_EMBEDDED\["' + domain + r'"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
    return json.loads(match.group(1))

def get_all_titles(node, titles=None):
    if titles is None:
        titles = []
    titles.append(node.get("title", ""))
    for child in node.get("children", []):
        get_all_titles(child, titles)
    return titles

def get_all_ids(node, ids=None):
    if ids is None:
        ids = []
    ids.append(node.get("id", ""))
    for child in node.get("children", []):
        get_all_ids(child, ids)
    return ids

def check_keywords(titles, keywords, domain_name):
    """检查关键词是否在标题中出现"""
    all_text = " ".join(titles)
    missing = []
    found = []
    for kw in keywords:
        if kw.lower() in all_text.lower():
            found.append(kw)
        else:
            missing.append(kw)
    return found, missing

# ========== 各领域核心检查清单 ==========

core_checks = {
    "sql": {
        "name": "SQL",
        "core_concepts": ["SELECT", "WHERE", "JOIN", "GROUP BY", "HAVING", "ORDER BY", 
                          "子查询", "窗口函数", "视图", "索引", "事务", "执行计划",
                          "DISTINCT", "LIMIT", "UNION", "CASE WHEN", "日期函数", "字符串函数"],
        "core_tools": ["MySQL", "PostgreSQL", "SQL Server", "Oracle"]
    },
    "python": {
        "name": "Python",
        "core_concepts": ["变量", "数据类型", "控制流", "函数", "列表", "字典", 
                          "循环", "条件", "字符串", "模块", "异常", "面向对象",
                          "文件操作", "正则", "推导式"],
        "core_tools": ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", 
                       "requests", "jupyter", "sklearn"]
    },
    "database": {
        "name": "数据库",
        "core_concepts": ["索引", "事务", "范式", "锁", "隔离级别", "主键", "外键",
                          "备份", "恢复", "优化", "执行计划", "连接池", "分库分表",
                          "读写分离", "主从复制"],
        "core_tools": ["MySQL", "PostgreSQL", "Redis", "MongoDB", "Oracle", "SQL Server"]
    },
    "ml": {
        "name": "机器学习",
        "core_concepts": ["监督学习", "无监督学习", "分类", "回归", "聚类", "降维",
                          "过拟合", "欠拟合", "交叉验证", "特征工程", "模型评估",
                          "准确率", "精确率", "召回率", "F1", "AUC", "ROC",
                          "训练集", "测试集", "验证集", "梯度下降", "损失函数"],
        "core_tools": ["scikit-learn", "sklearn", "XGBoost", "LightGBM", "TensorFlow",
                       "PyTorch", "pandas", "numpy"]
    },
    "etl": {
        "name": "ETL",
        "core_concepts": ["抽取", "转换", "装载", "数据质量", "调度", "血缘",
                          "增量", "全量", "CDC", "数据清洗", "数据校验", "错误处理",
                          "重试", "监控", "参数化"],
        "core_tools": ["Kettle", "PDI", "Airflow", "dbt", "DataX", "Airbyte", 
                       "Flink", "Sqoop", "NiFi", "Talend", "Informatica"]
    },
    "dwh": {
        "name": "数据仓库",
        "core_concepts": ["维度建模", "星型", "雪花", "事实表", "维度表", "SCD",
                          "缓慢变化维", "ODS", "DWD", "DWS", "ADS", "分层",
                          "指标体系", "数据集市", "OLAP", "MOLAP", "ROLAP",
                          "一致性维度", "退化维度", "拉链表"],
        "core_tools": ["Hive", "ClickHouse", "Doris", "StarRocks", "Snowflake",
                       "Redshift", "BigQuery", "MaxCompute"]
    },
    "bi": {
        "name": "BI",
        "core_concepts": ["可视化", "仪表板", "数据故事", "图表", "钻取", "筛选",
                          "交互", "KPI", "指标", "报表", "维度", "度量",
                          "配色", "布局", "用户体验"],
        "core_tools": ["Tableau", "Power BI", "FineBI", "FineReport", "Superset",
                       "Quick BI", "Looker", "Qlik"]
    }
}

# ========== 执行检查 ==========
print("=" * 70)
print("7大领域核心内容完整性扫描")
print("=" * 70)

all_missing = {}

for domain, checks in core_checks.items():
    data = load_domain(domain)
    titles = get_all_titles(data)
    all_text = " ".join(titles)
    
    print(f"\n{'='*70}")
    print(f"【{checks['name']}】 共 {len(titles)} 个节点")
    print(f"{'='*70}")
    
    # 检查核心概念
    found_concepts, missing_concepts = check_keywords(titles, checks["core_concepts"], checks["name"])
    print(f"\n核心概念（{len(found_concepts)}/{len(checks['core_concepts'])}）:")
    print(f"  ✓ 已覆盖: {', '.join(found_concepts)}")
    if missing_concepts:
        print(f"  ✗ 缺失: {', '.join(missing_concepts)}")
    
    # 检查核心工具
    found_tools, missing_tools = check_keywords(titles, checks["core_tools"], checks["name"])
    print(f"\n核心工具（{len(found_tools)}/{len(checks['core_tools'])}）:")
    print(f"  ✓ 已覆盖: {', '.join(found_tools)}")
    if missing_tools:
        print(f"  ✗ 缺失: {', '.join(missing_tools)}")
    
    all_missing[domain] = {
        "concepts": missing_concepts,
        "tools": missing_tools,
        "found_concepts": found_concepts,
        "found_tools": found_tools
    }

# ========== 汇总 ==========
print(f"\n\n{'='*70}")
print("缺失内容汇总")
print(f"{'='*70}")

for domain, checks in core_checks.items():
    missing = all_missing[domain]
    total_missing = len(missing["concepts"]) + len(missing["tools"])
    if total_missing > 0:
        print(f"\n【{checks['name']}】缺失 {total_missing} 项:")
        if missing["concepts"]:
            print(f"  概念: {', '.join(missing['concepts'])}")
        if missing["tools"]:
            print(f"  工具: {', '.join(missing['tools'])}")
    else:
        print(f"\n【{checks['name']}】核心内容齐全 ✓")
