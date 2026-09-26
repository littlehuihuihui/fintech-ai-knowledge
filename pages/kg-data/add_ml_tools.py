#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充机器学习实战工具：XGBoost/LightGBM、模型融合、超参数调优、SHAP可解释性"""

import json, re

filepath = r"D:\cursor\数据学习平台\kg-data\embed-ml.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["ml"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def make_leaf(node_id, title, content):
    return {"id": node_id, "title": title, "level": "??", "content": content, "children": []}

# ========== 1. XGBoost / LightGBM ==========
xgb_content = '''### 课前

- **场景**：结构化数据竞赛和工业界最常用的模型，需要掌握梯度提升树的两大主流框架。
- **目标**：掌握 XGBoost 和 LightGBM 的原理区别、安装、基本用法、调参要点、实战技巧。
- **先修**：决策树、随机森林、GBDT/梯度提升、scikit-learn 基础

### 是什么

- **一句话定义**：XGBoost（eXtreme Gradient Boosting）和 LightGBM（Light Gradient Boosting Machine）是 GBDT 的高效工程实现，通过正则化、并行计算、直方图算法等优化，在结构化数据任务上表现卓越，是 Kaggle 竞赛和工业界的首选模型。
- **两者区别**：
  - **XGBoost**：陈天奇开发，精确贪心算法+近似算法，成熟稳定，文档完善
  - **LightGBM**：微软开发，直方图算法+叶子优先生长+GOSS采样，训练更快、内存更少
  - 两者都是 GBDT 的优化实现，核心原理相同，工程实现不同

### 怎么写

```python
# ============================================================
# 例1：XGBoost 基本用法（分类）
# ============================================================
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

# 加载数据
data = load_breast_cancer()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 方式1：sklearn 接口（推荐，简单易用）
model = xgb.XGBClassifier(
    n_estimators=100,        # 树的数量
    max_depth=6,              # 树的最大深度
    learning_rate=0.1,        # 学习率（步长）
    subsample=0.8,            # 行采样比例
    colsample_bytree=0.8,     # 列采样比例
    reg_alpha=0.1,             # L1 正则化
    reg_lambda=1.0,            # L2 正则化
    random_state=42,
    use_label_encoder=False,
    eval_metric="logloss"
)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")
print(f"AUC: {roc_auc_score(y_test, y_prob):.4f}")

# 方式2：原生 DMatrix 接口（性能更好，功能更全）
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {
    "objective": "binary:logistic",  # 目标函数
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": ["logloss", "auc"]
}

# 训练，用 early_stopping_rounds 防止过拟合
evals = [(dtrain, "train"), (dtest, "test")]
model = xgb.train(
    params, dtrain, 
    num_boost_round=1000,
    evals=evals,
    early_stopping_rounds=50,  # 50轮没提升就停止
    verbose_eval=50
)
print(f"最佳迭代轮数: {model.best_iteration}")
print(f"最佳测试AUC: {model.best_score:.4f}")

# ============================================================
# 例2：XGBoost 回归
# ============================================================
from sklearn.datasets import load_diabetes
from sklearn.metrics import mean_squared_error

data = load_diabetes()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42
)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f"RMSE: {rmse:.4f}")

# ============================================================
# 例3：LightGBM 基本用法（分类）
# ============================================================
import lightgbm as lgb

# 方式1：sklearn 接口
model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=-1,           # -1 表示不限制深度（LightGBM 默认叶子优先）
    num_leaves=31,          # 叶子节点数（LightGBM 核心参数）
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    verbose=-1
)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")

# 方式2：原生 Dataset 接口
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

params = {
    "objective": "binary",
    "metric": ["binary_logloss", "auc"],
    "num_leaves": 31,
    "learning_rate": 0.1,
    "feature_fraction": 0.8,  # 同 colsample_bytree
    "bagging_fraction": 0.8,   # 同 subsample
    "bagging_freq": 5,          # 每5轮采样一次
    "lambda_l1": 0.1,
    "lambda_l2": 1.0,
    "verbose": -1
}

model = lgb.train(
    params, train_data,
    num_boost_round=1000,
    valid_sets=[train_data, test_data],
    valid_names=["train", "test"],
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(50)]
)
print(f"最佳迭代轮数: {model.best_iteration}")

# ============================================================
# 例4：XGBoost vs LightGBM 参数对照
# ============================================================
# | 功能 | XGBoost | LightGBM |
# |---|---|---|
# | 树数量 | n_estimators | n_estimators |
# | 最大深度 | max_depth | max_depth（默认-1不限制） |
# | 叶子数 | （通过max_depth控制） | num_leaves（核心参数，默认31） |
# | 学习率 | learning_rate | learning_rate |
# | 行采样 | subsample | subsample / bagging_fraction |
# | 列采样 | colsample_bytree | colsample_bytree / feature_fraction |
# | L1正则 | reg_alpha | reg_alpha / lambda_l1 |
# | L2正则 | reg_lambda | reg_lambda / lambda_l2 |
# | 最小子节点权重 | min_child_weight | min_child_weight / min_sum_hessian |
# | 生长策略 | 层优先（level-wise） | 叶子优先（leaf-wise，更快但易过拟合） |

# ============================================================
# 例5：特征重要性
# ============================================================
import matplotlib.pyplot as plt

# XGBoost 特征重要性
xgb_model = xgb.XGBClassifier().fit(X_train, y_train)
importance = xgb_model.feature_importances_
feature_names = data.feature_names

# 排序并展示
sorted_idx = importance.argsort()
plt.figure(figsize=(10, 6))
plt.barh(range(len(sorted_idx)), importance[sorted_idx])
plt.yticks(range(len(sorted_idx)), [feature_names[i] for i in sorted_idx])
plt.title("XGBoost 特征重要性")
plt.tight_layout()
# plt.show()

# LightGBM 特征重要性
lgb_model = lgb.LGBMClassifier(verbose=-1).fit(X_train, y_train)
lgb.plot_importance(lgb_model, max_num_features=20, figsize=(10, 6))
# plt.show()

# ============================================================
# 例6：处理缺失值（XGBoost/LightGBM 原生支持）
# ============================================================
import numpy as np

# 不需要手动填充缺失值，XGBoost/LightGBM 自动学习缺失值的最佳分裂方向
X_train_missing = X_train.copy()
X_train_missing[X_train_missing < 0] = np.nan  # 制造一些缺失值

model = xgb.XGBClassifier()
model.fit(X_train_missing, y_train)  # 直接训练，自动处理缺失值
# 这是树模型的一大优势，不需要像线性模型那样手动填充

# ============================================================
# 例7：类别特征处理（LightGBM 原生支持类别特征）
# ============================================================
# LightGBM 可以直接处理类别特征（不需要 one-hot 编码）
# 只需要把列设为 category 类型
# import pandas as pd
# df["category_col"] = df["category_col"].astype("category")
# model = lgb.LGBMClassifier()
# model.fit(df[features], df[label])  # 自动处理类别特征

# XGBoost 也支持类别特征（1.6.0+）
# model = xgb.XGBClassifier(enable_categorical=True)
# model.fit(df[features], df[label])

# ============================================================
# 例8：调参策略（从粗到细）
# ============================================================
# 第一步：固定学习率，确定树数量（用 early_stopping）
# 第二步：调 max_depth / num_leaves（树复杂度）
# 第三步：调 min_child_weight / min_sum_hessian（防止过拟合）
# 第四步：调 subsample / colsample_bytree（采样，增加随机性）
# 第五步：调 reg_alpha / reg_lambda（正则化）
# 第六步：降低学习率，增加树数量（最终精调）

# 常用参数范围：
# max_depth: 3-10（太深过拟合，太浅欠拟合）
# num_leaves (LightGBM): 15-255（通常 31-63）
# learning_rate: 0.01-0.3（最终用 0.01-0.05，配合更多树）
# n_estimators: 100-2000（用 early_stopping 自动确定）
# subsample: 0.6-1.0
# colsample_bytree: 0.6-1.0
# reg_alpha: 0-1.0
# reg_lambda: 0.1-10.0
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 不用 early_stopping | 过拟合，树太多 | 必须用 early_stopping_rounds，自动确定最佳轮数 |
| LightGBM num_leaves 太大 | 过拟合 | num_leaves 通常 31-63，配合 max_depth 限制 |
| 学习率太高 | 收敛快但精度低 | 最终模型用 0.01-0.05，配合更多树 |
| 不做特征工程直接用 | 精度低 | 树模型虽然鲁棒，但好的特征工程仍然重要 |
| XGBoost 用 label_encoder | 警告或错误 | 用 use_label_encoder=False，类别特征用 one-hot 或原生支持 |
| 忽略缺失值处理 | 线性模型报错 | 树模型原生支持缺失值，不需要手动填充 |
| 只看准确率不看 AUC | 不平衡数据误导 | 分类任务看 AUC、F1、召回率等综合指标 |

### 动手

1. 用 XGBoost 和 LightGBM 分别训练一个分类模型，对比准确率、AUC、训练时间
2. 用 early_stopping 自动确定最佳树数量，观察训练过程
3. 绘制特征重要性图，找出 Top 10 重要特征
4. 尝试不同的 max_depth（3/6/9），观察对训练集和测试集性能的影响
5. （进阶）用 GridSearchCV 对 XGBoost 进行超参数搜索
'''

# ========== 2. 模型融合 ==========
ensemble_content = '''### 课前

- **场景**：单个模型精度到了瓶颈，需要通过组合多个模型进一步提升性能，是竞赛和工业界的常用技巧。
- **目标**：掌握 Voting、Bagging、Boosting、Stacking、Blending 等模型融合方法的原理和实现。
- **先修**：逻辑回归、决策树、随机森林、XGBoost/LightGBM、交叉验证

### 是什么

- **一句话定义**：模型融合（Ensemble Learning）是将多个基模型的预测结果通过某种策略组合起来，利用不同模型的互补性降低方差和偏差，获得比单个模型更好的性能，是机器学习竞赛中提升精度的关键技巧。
- **核心思想**：三个臭皮匠顶个诸葛亮——不同模型犯错的地方不同，组合后可以互相弥补。
- **主要方法**：Voting（投票）、Bagging（并行独立）、Boosting（串行纠错）、Stacking（分层堆叠）、Blending（简化版Stacking）。

### 怎么写

```python
# ============================================================
# 例1：Voting 投票融合（最简单的融合）
# ============================================================
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score

data = load_breast_cancer()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 定义基模型
clf1 = LogisticRegression(max_iter=1000, random_state=42)
clf2 = RandomForestClassifier(n_estimators=100, random_state=42)
clf3 = SVC(probability=True, random_state=42)

# 硬投票（Hard Voting）：少数服从多数，取预测类别
eclf_hard = VotingClassifier(
    estimators=[("lr", clf1), ("rf", clf2), ("svc", clf3)],
    voting="hard"
)
eclf_hard.fit(X_train, y_train)
print(f"硬投票准确率: {eclf_hard.score(X_test, y_test):.4f}")

# 软投票（Soft Voting）：加权平均概率，取概率最高的类别
eclf_soft = VotingClassifier(
    estimators=[("lr", clf1), ("rf", clf2), ("svc", clf3)],
    voting="soft",
    weights=[1, 2, 1]  # 可以给不同模型不同权重（性能好的权重高）
)
eclf_soft.fit(X_train, y_train)
print(f"软投票准确率: {eclf_soft.score(X_test, y_test):.4f}")

# 对比单个模型
for name, clf in [("LR", clf1), ("RF", clf2), ("SVC", clf3)]:
    scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
    print(f"{name}: {scores.mean():.4f} (+/- {scores.std():.4f})")

# ============================================================
# 例2：Bagging（并行独立训练，随机森林是Bagging的特例）
# ============================================================
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier

# Bagging：对同一基模型进行多次有放回采样，训练多个模型，最后投票
bagging = BaggingClassifier(
    estimator=DecisionTreeClassifier(),  # 基模型
    n_estimators=100,                     # 基模型数量
    max_samples=0.8,                      # 每个模型采样80%的数据
    max_features=0.8,                     # 每个模型采样80%的特征
    random_state=42,
    n_jobs=-1                             # 并行训练
)
bagging.fit(X_train, y_train)
print(f"Bagging准确率: {bagging.score(X_test, y_test):.4f}")

# 随机森林 = Bagging + 决策树 + 特征随机选择
# （已经在经典模型章节学习过）

# ============================================================
# 例3：Stacking 分层堆叠（最强大的融合方法）
# ============================================================
from sklearn.ensemble import StackingClassifier
from sklearn.model_selection import StratifiedKFold

# 第一层：基模型（学习器）
base_models = [
    ("rf", RandomForestClassifier(n_estimators=100, random_state=42)),
    ("xgb", xgb.XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric="logloss")),
    ("lgb", lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)),
]

# 第二层：元模型（学习器，通常用简单模型如逻辑回归）
meta_model = LogisticRegression(max_iter=1000, random_state=42)

# Stacking 分类器
stacking = StackingClassifier(
    estimators=base_models,
    final_estimator=meta_model,
    cv=5,                          # 交叉验证折数
    stack_method="predict_proba", # 用概率作为元特征（比类别更好）
    n_jobs=-1,
    passthrough=False             # 是否保留原始特征（False只用预测结果）
)
stacking.fit(X_train, y_train)
print(f"Stacking准确率: {stacking.score(X_test, y_test):.4f}")

# Stacking 原理：
# 1. 用 K 折交叉验证，每个基模型在训练集上生成"离群预测"（out-of-fold predictions）
# 2. 这些预测结果作为元特征（meta-features），和原始标签一起训练元模型
# 3. 预测时，基模型先预测，结果输入元模型得到最终预测
# 这样避免了信息泄露（基模型不会在自己训练过的数据上预测）

# ============================================================
# 例4：手动实现 Stacking（理解原理）
# ============================================================
def stacking_predict(base_models, meta_model, X_train, y_train, X_test, n_splits=5):
    """手动实现 Stacking"""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    # 生成训练集的离群预测
    oof_preds = np.zeros((len(X_train), len(base_models)))
    test_preds = np.zeros((len(X_test), len(base_models)))
    
    for i, (name, model) in enumerate(base_models):
        test_fold_preds = np.zeros((len(X_test), n_splits))
        for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
            X_tr, X_val = X_train[train_idx], X_train[val_idx]
            y_tr, y_val = y_train[train_idx], y_train[val_idx]
            
            model.fit(X_tr, y_tr)
            oof_preds[val_idx, i] = model.predict_proba(X_val)[:, 1]
            test_fold_preds[:, fold] = model.predict_proba(X_test)[:, 1]
        
        # 测试集预测取平均
        test_preds[:, i] = test_fold_preds.mean(axis=1)
        print(f"{name} 完成")
    
    # 用离群预测训练元模型
    meta_model.fit(oof_preds, y_train)
    final_preds = meta_model.predict_proba(test_preds)[:, 1]
    
    return final_preds, oof_preds, test_preds

# ============================================================
# 例5：Blending（简化版 Stacking，用 holdout 代替 K 折）
# ============================================================
# Blending 原理：
# 1. 把训练集分成两部分：train（70%）+ holdout（30%）
# 2. 基模型在 train 上训练，在 holdout 上预测（生成元特征）
# 3. 元模型在 holdout 的预测结果上训练
# 4. 预测时，基模型先预测，元模型得到最终结果
# 比 Stacking 简单，但用的数据更少，可能性能略差

# 实现：
# X_train, X_holdout, y_train, y_holdout = train_test_split(X, y, test_size=0.3)
# 基模型在 X_train 上训练
# 基模型在 X_holdout 上预测 → meta_features
# 元模型在 meta_features 上训练
# 预测时：基模型预测 X_test → 元模型预测

# ============================================================
# 例6：回归任务的融合
# ============================================================
from sklearn.ensemble import VotingRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

reg1 = Ridge(alpha=1.0)
reg2 = RandomForestRegressor(n_estimators=100, random_state=42)
reg3 = xgb.XGBRegressor(n_estimators=100, random_state=42)

# 投票回归（平均预测值）
voting_reg = VotingRegressor(
    estimators=[("ridge", reg1), ("rf", reg2), ("xgb", reg3)],
    weights=[1, 2, 2]
)
# voting_reg.fit(X_train, y_train)
# y_pred = voting_reg.predict(X_test)

# Stacking 回归
stacking_reg = StackingRegressor(
    estimators=[("ridge", reg1), ("rf", reg2), ("xgb", reg3)],
    final_estimator=Ridge(alpha=1.0),
    cv=5
)

# ============================================================
# 例7：融合的注意事项和最佳实践
# ============================================================
# 1. 基模型要"好而不同"：
#    - 好：每个基模型性能不能太差（至少比随机好）
#    - 不同：模型之间要有差异性（不同算法、不同特征、不同参数）
#    - 相关性低的模型融合效果更好

# 2. 常见的基模型组合：
#    - 线性模型（LR/Ridge）+ 树模型（RF/XGBoost/LightGBM）+ SVM/KNN
#    - XGBoost + LightGBM + CatBoost（三个 GBDT 框架，差异在实现）
#    - 不同特征子集训练的模型（特征多样性）

# 3. 元模型选择：
#    - 分类：逻辑回归（最常用）、简单的树模型
#    - 回归：Ridge/Lasso（最常用）
#    - 元模型要简单，避免过拟合元特征

# 4. 性能提升预期：
#    - 单个模型已经很好时，融合提升有限（1-3%）
#    - 模型差异大时，融合提升明显（5-10%）
#    - 不要期望融合带来质的飞跃，特征工程更重要

# 5. 计算成本：
#    - Stacking 需要 K 折交叉验证，训练时间是 K 倍
#    - 可以用较少的折数（如3折）平衡性能和时间
#    - 预测时也需要运行所有基模型+元模型

# ============================================================
# 例8：加权平均（简单有效的融合）
# ============================================================
# 对于概率输出，加权平均是最简单有效的融合方式
# 权重可以根据验证集性能来确定

# 假设三个模型的预测概率
# pred1 = model1.predict_proba(X_test)[:, 1]
# pred2 = model2.predict_proba(X_test)[:, 1]
# pred3 = model3.predict_proba(X_test)[:, 1]

# 等权重平均
# final_pred = (pred1 + pred2 + pred3) / 3

# 按性能加权（AUC高的权重高）
# final_pred = 0.2 * pred1 + 0.5 * pred2 + 0.3 * pred3

# 秩平均（Rank Averaging，对排序更鲁棒）
# from scipy.stats import rankdata
# rank1 = rankdata(pred1)
# rank2 = rankdata(pred2)
# final_rank = (rank1 + rank2) / 2
# final_pred = final_rank / len(final_rank)  # 归一化
```

### 融合方法对比

| 方法 | 原理 | 复杂度 | 性能提升 | 适用场景 |
|---|---|---|---|---|
| Voting | 投票/平均 | 低 | 小 | 快速 baseline |
| Bagging | 并行独立采样 | 中 | 中 | 降低方差（随机森林） |
| Boosting | 串行纠错 | 中 | 大 | 降低偏差（GBDT） |
| Stacking | 分层堆叠+元模型 | 高 | 最大 | 竞赛/追求极致性能 |
| Blending | holdout+元模型 | 中 | 中 | 简单版Stacking |
| 加权平均 | 权重加权 | 低 | 中 | 概率输出融合 |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 基模型太相似 | 融合效果差，几乎无提升 | 选择不同算法/特征/参数的模型，保证差异性 |
| 元模型太复杂 | 过拟合元特征 | 元模型用简单模型（LR/Ridge），不要用复杂的树模型 |
| Stacking 不用交叉验证 | 信息泄露，过拟合 | 必须用 K 折交叉验证生成离群预测 |
| 基模型性能太差 | 融合后性能被拉低 | 每个基模型至少要达到 baseline 水平 |
| 只融合不做特征工程 | 性能瓶颈在特征不在模型 | 特征工程是上限，模型融合只是逼近上限 |
| 忽略计算成本 | 训练/预测时间太长 | 根据时间预算选择融合方法，Stacking 最耗时 |
| 软投票模型不输出概率 | 报错 | 软投票要求所有模型支持 predict_proba，SVC 要设 probability=True |

### 动手

1. 用 VotingClassifier 组合逻辑回归、随机森林、SVM，对比硬投票和软投票
2. 用 StackingClassifier 组合 XGBoost、LightGBM、随机森林，元模型用逻辑回归
3. 手动实现一个简单的 Stacking（理解离群预测的生成过程）
4. 对比单个模型和融合模型的交叉验证性能，计算融合带来的提升
5. （进阶）尝试不同的基模型组合，找出性能最好的融合方案
'''

# ========== 3. 超参数调优 ==========
tuning_content = '''### 课前

- **场景**：模型默认参数不是最优的，需要系统地搜索最佳超参数组合，提升模型性能。
- **目标**：掌握 GridSearch、RandomSearch、贝叶斯优化三种调参方法的原理和实现，了解调参策略和注意事项。
- **先修**：交叉验证、XGBoost/LightGBM、scikit-learn 基础

### 是什么

- **一句话定义**：超参数调优是在模型训练前设定的参数（如树深度、学习率）中搜索最佳组合的过程，通过系统地尝试不同参数组合，找到在验证集上性能最好的配置，是机器学习实战中提升性能的关键步骤。
- **三种主要方法**：
  - **网格搜索（GridSearch）**：穷举所有参数组合，简单但计算量大
  - **随机搜索（RandomSearch）**：随机采样参数组合，效率高，适合高维空间
  - **贝叶斯优化（Bayesian Optimization）**：基于历史结果智能选择下一组参数，样本效率最高

### 怎么写

```python
# ============================================================
# 例1：GridSearchCV 网格搜索（最基础）
# ============================================================
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

data = load_breast_cancer()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 定义参数网格
param_grid = {
    "n_estimators": [50, 100, 200],      # 3 个值
    "max_depth": [None, 5, 10, 15],       # 4 个值
    "min_samples_split": [2, 5, 10],       # 3 个值
    "min_samples_leaf": [1, 2, 4],         # 3 个值
}
# 总共 3*4*3*3 = 108 种组合，5折交叉验证 = 540 次训练

# 网格搜索
grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42, n_jobs=-1),
    param_grid=param_grid,
    cv=5,                          # 5折交叉验证
    scoring="roc_auc",             # 优化指标
    n_jobs=-1,                     # 并行计算
    verbose=1,                     # 打印进度
    return_train_score=True        # 返回训练集分数（用于判断过拟合）
)
grid_search.fit(X_train, y_train)

print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳交叉验证分数: {grid_search.best_score_:.4f}")
print(f"测试集分数: {grid_search.score(X_test, y_test):.4f}")

# 查看所有结果
import pandas as pd
results = pd.DataFrame(grid_search.cv_results_)
print(results[["params", "mean_test_score", "std_test_score", "rank_test_score"]]
      .sort_values("rank_test_score").head(10))

# ============================================================
# 例2：RandomizedSearchCV 随机搜索（高维参数空间更高效）
# ============================================================
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

# 定义参数分布（不是固定值，而是分布）
param_dist = {
    "n_estimators": randint(50, 500),           # 50-500 之间的整数均匀分布
    "max_depth": randint(3, 20),                  # 3-20 之间
    "min_samples_split": randint(2, 20),          # 2-20
    "min_samples_leaf": randint(1, 10),           # 1-10
    "max_features": uniform(0.5, 0.5),            # 0.5-1.0 连续均匀分布
    "bootstrap": [True, False]
}

# 随机搜索（只尝试 n_iter 组随机组合）
random_search = RandomizedSearchCV(
    estimator=RandomForestClassifier(random_state=42, n_jobs=-1),
    param_distributions=param_dist,
    n_iter=50,                      # 只尝试50组随机组合（比网格搜索的108组少）
    cv=5,
    scoring="roc_auc",
    n_jobs=-1,
    verbose=1,
    random_state=42
)
random_search.fit(X_train, y_train)

print(f"最佳参数: {random_search.best_params_}")
print(f"最佳分数: {random_search.best_score_:.4f}")

# 随机搜索 vs 网格搜索：
# - 参数维度高、连续参数多时，随机搜索更高效
# - 随机搜索可以在更宽的范围内探索，不会只在固定值上
# - 研究表明：随机搜索在相同计算预算下通常比网格搜索找到更好的结果

# ============================================================
# 例3：XGBoost 调参实战（分阶段调参策略）
# ============================================================
import xgboost as xgb

# 第一阶段：确定学习率和树数量
params1 = {
    "learning_rate": [0.05, 0.1, 0.2],
    "n_estimators": [100, 200, 500]
}
# 用 early_stopping 更高效（不需要搜索 n_estimators）

# 第二阶段：调树复杂度
params2 = {
    "max_depth": [3, 5, 7, 9],
    "min_child_weight": [1, 3, 5, 7]
}

# 第三阶段：调采样
params3 = {
    "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0]
}

# 第四阶段：调正则化
params4 = {
    "reg_alpha": [0, 0.01, 0.1, 1, 10],
    "reg_lambda": [0, 0.01, 0.1, 1, 10]
}

# 第五阶段：降低学习率，增加树数量
# learning_rate: 0.01, n_estimators: 1000+（用 early_stopping）

# 实际操作：每阶段固定其他参数，只搜索当前阶段的参数
# 例如先固定 learning_rate=0.1，搜索 max_depth 和 min_child_weight
# 找到最佳后固定，再搜索下一组参数

# ============================================================
# 例4：贝叶斯优化（optuna 库，最先进的调参方法）
# ============================================================
# pip install optuna
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial):
    """Optuna 目标函数：返回要优化的指标（最大化）"""
    # 定义参数搜索空间
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 15),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10, log=True),
    }
    
    model = xgb.XGBClassifier(**params, random_state=42, use_label_encoder=False, eval_metric="logloss")
    score = cross_val_score(model, X_train, y_train, cv=5, scoring="roc_auc", n_jobs=-1).mean()
    return score

# 创建 study 并优化
study = optuna.create_study(direction="maximize", study_name="xgb_tuning")
study.optimize(objective, n_trials=50, show_progress_bar=True)

print(f"最佳参数: {study.best_params}")
print(f"最佳分数: {study.best_value:.4f}")

# 可视化优化过程
# optuna.visualization.plot_optimization_history(study)
# optuna.visualization.plot_param_importances(study)
# optuna.visualization.plot_parallel_coordinate(study)

# 贝叶斯优化原理：
# 1. 建立一个代理模型（通常是高斯过程或TPE），预测参数→性能的映射
# 2. 根据代理模型，选择"可能好"且"不确定"的参数（探索 vs 利用平衡）
# 3. 评估这组参数，更新代理模型
# 4. 重复，直到达到预算
# 比随机搜索样本效率高（用更少的试验找到更好的参数）

# ============================================================
# 例5：嵌套交叉验证（防止调参过拟合）
# ============================================================
# 问题：用同一批数据调参和评估，会导致乐观估计（调参过拟合）
# 解决：嵌套交叉验证
# - 外层循环：评估模型泛化性能（测试集）
# - 内层循环：在训练集上做交叉验证调参

from sklearn.model_selection import cross_val_score, KFold

# 外层：5折
outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)

# 内层：用 GridSearchCV（自带 cv）
grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid={"n_estimators": [50, 100], "max_depth": [5, 10]},
    cv=3,
    scoring="roc_auc",
    n_jobs=-1
)

# 嵌套交叉验证
nested_scores = cross_val_score(grid_search, X, y, cv=outer_cv, scoring="roc_auc")
print(f"嵌套交叉验证分数: {nested_scores.mean():.4f} (+/- {nested_scores.std():.4f})")
# 这个分数更真实地反映模型的泛化性能

# ============================================================
# 例6：调参的注意事项和最佳实践
# ============================================================
# 1. 先做特征工程，再调参：
#    特征工程决定上限，调参只是逼近上限
#    不要在差特征上浪费时间调参

# 2. 从粗到细：
#    先用大范围随机搜索找到大致最优区域
#    再在最优区域附近用小范围网格搜索精调

# 3. 固定学习率，用 early_stopping 确定树数量：
#    不要把 n_estimators 作为搜索参数（浪费计算）
#    固定 learning_rate，用 early_stopping 自动确定最佳 n_estimators

# 4. 关注过拟合：
#    训练集分数高、验证集分数低 = 过拟合
#    调参时同时看训练集和验证集分数
#    过拟合时：降低 max_depth、增加 min_child_weight、增加正则化、增加采样随机性

# 5. 参数重要性排序（XGBoost/LightGBM）：
#    最重要：learning_rate, max_depth/num_leaves, n_estimators
#    次重要：subsample, colsample_bytree, min_child_weight
#    再次：reg_alpha, reg_lambda
#    先调重要参数，再调次要参数

# 6. 计算预算：
#    网格搜索：参数组合数 × 折数 × 单模型训练时间
#    随机搜索：n_iter × 折数 × 单模型训练时间
#    贝叶斯优化：n_trials × 折数 × 单模型训练时间
#    根据时间预算选择方法和试验次数

# 7. 可复现性：
#    固定 random_state
#    记录最佳参数和搜索过程
#    保存搜索结果（cv_results_）
```

### 三种调参方法对比

| 方法 | 原理 | 样本效率 | 计算量 | 适用场景 |
|---|---|---|---|---|
| GridSearch | 穷举所有组合 | 低 | 大 | 参数少、离散参数 |
| RandomSearch | 随机采样 | 中 | 中 | 参数多、连续参数 |
| 贝叶斯优化 | 智能选择下一组 | 高 | 小 | 计算昂贵、追求最优 |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 调参过拟合（同一批数据调参+评估） | 测试集分数虚高 | 用嵌套交叉验证，或单独留出测试集 |
| 把 n_estimators 作为搜索参数 | 浪费大量计算 | 用 early_stopping 自动确定树数量 |
| 一次搜索所有参数 | 计算量爆炸，参数空间太大 | 分阶段调参，先重要后次要 |
| 只看验证集分数不看训练集 | 过拟合不知情 | 同时看训练集和验证集，判断过拟合 |
| 不固定 random_state | 结果不可复现 | 所有模型和搜索都固定 random_state |
| 网格搜索参数值太少 | 错过最优值 | 先用随机搜索大范围探索，再网格精调 |
| 调参代替特征工程 | 性能瓶颈在特征 | 先做好特征工程，调参是锦上添花 |
| 忽略调参时间 | 训练几天几夜 | 先估算计算量，根据预算选择方法 |

### 动手

1. 用 GridSearchCV 对随机森林进行超参数搜索，记录最佳参数和分数
2. 用 RandomizedSearchCV 对 XGBoost 进行随机搜索，对比和网格搜索的效率
3. 用 optuna 对 LightGBM 进行贝叶斯优化，尝试50次试验
4. 实现分阶段调参：先调 max_depth/min_child_weight，再调采样参数
5. （进阶）实现嵌套交叉验证，对比普通交叉验证和嵌套交叉验证的分数差异
'''

# ========== 4. SHAP 模型可解释性 ==========
shap_content = '''### 课前

- **场景**：模型是黑盒，需要解释模型为什么做出某个预测、哪些特征最重要、特征如何影响预测结果。
- **目标**：掌握 SHAP 值的原理、计算方法、可视化图表，能解释树模型和其他模型的预测。
- **先修**：XGBoost/LightGBM、特征重要性、模型评估

### 是什么

- **一句话定义**：SHAP（SHapley Additive exPlanations）是基于博弈论 Shapley 值的模型解释方法，通过计算每个特征对单个预测的贡献值，实现模型的局部和全局可解释性，是目前最流行、理论最扎实的模型解释工具。
- **核心优势**：
  - **局部解释**：能解释单个预测的特征贡献（为什么这个样本被预测为正类）
  - **全局解释**：能汇总所有样本的 SHAP 值，得到全局特征重要性
  - **一致性**：SHAP 值有理论保证，特征贡献之和等于预测值减去基准值
  - **支持多种模型**：树模型、线性模型、深度学习模型等

### 怎么写

```python
# ============================================================
# 例1：SHAP 基本用法（树模型）
# ============================================================
# pip install shap
import shap
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

data = load_breast_cancer()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练模型
model = xgb.XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric="logloss")
model.fit(X_train, y_train)

# 创建解释器（树模型用 TreeExplainer，速度快）
explainer = shap.TreeExplainer(model)

# 计算 SHAP 值
shap_values = explainer.shap_values(X_test)
# shap_values 形状：(n_samples, n_features)
# 每个值表示该特征对该样本预测的贡献

# 基准值（所有样本的平均预测概率的 logit）
print(f"基准值: {explainer.expected_value}")

# ============================================================
# 例2：单样本解释（Force Plot / Waterfall Plot）
# ============================================================
# 解释第 0 个样本的预测
sample_idx = 0
print(f"样本 {sample_idx} 的真实标签: {y_test[sample_idx]}")
print(f"样本 {sample_idx} 的预测概率: {model.predict_proba(X_test[sample_idx:sample_idx+1])[0, 1]:.4f}")

# 瀑布图（Waterfall Plot）：展示每个特征对预测的贡献
shap.plots.waterfall(
    shap.Explanation(
        values=shap_values[sample_idx],
        base_values=explainer.expected_value,
        data=X_test[sample_idx],
        feature_names=data.feature_names
    )
)
# 瀑布图从基准值开始，每个特征正向（红色）或负向（蓝色）推动预测
# 最终到达该样本的预测值

# 力图（Force Plot）：交互式的单样本解释
# shap.initjs()  # Jupyter 中需要
# shap.force_plot(explainer.expected_value, shap_values[sample_idx], X_test[sample_idx], feature_names=data.feature_names)

# ============================================================
# 例3：全局特征重要性（Summary Plot）
# ============================================================
# 摘要图（Summary Plot / Beeswarm Plot）：最常用的全局解释图
shap.summary_plot(shap_values, X_test, feature_names=data.feature_names)
# 每个点是一个样本，Y轴是特征（按重要性排序），X轴是 SHAP 值（对预测的影响）
# 颜色表示特征值大小（红色=高，蓝色=低）
# 可以看出：
# - 哪些特征最重要（点分布越宽越重要）
# - 特征值高低如何影响预测（红色点在正还是负方向）

# 条形图版本的特征重要性
shap.summary_plot(shap_values, X_test, feature_names=data.feature_names, plot_type="bar")
# 按 SHAP 值绝对值的平均排序，得到特征重要性排名

# ============================================================
# 例4：特征依赖图（Dependence Plot）
# ============================================================
# 分析单个特征如何影响预测（非线性关系、交互效应）
feature_name = "worst perimeter"  # 选一个重要特征
shap.dependence_plot(
    feature_name, 
    shap_values, 
    X_test, 
    feature_names=data.feature_names,
    interaction_index="auto"  # 自动选择交互最强的特征用颜色表示
)
# X轴是特征值，Y轴是 SHAP 值（对预测的影响）
# 每个点是一个样本，可以看出特征值和预测贡献的关系
# 颜色表示另一个特征的值，可以发现交互效应

# ============================================================
# 例5：决策图（Decision Plot）
# ============================================================
# 展示多个样本的预测路径
shap.decision_plot(
    explainer.expected_value,
    shap_values[:20],  # 前20个样本
    X_test[:20],
    feature_names=data.feature_names,
    feature_order="hclust"  # 按层次聚类排序特征
)
# 每条线是一个样本，从基准值开始，经过特征累积，最终到达预测值
# 可以对比不同样本的预测路径差异

# ============================================================
# 例6：SHAP 交互值（Interaction Values）
# ============================================================
# 计算特征之间的交互效应
shap_interaction = explainer.shap_interaction_values(X_test)
# 形状：(n_samples, n_features, n_features)
# shap_interaction[i, j, k] 表示特征 j 和 k 对样本 i 的交互贡献

# 交互摘要图
shap.summary_plot(shap_interaction, X_test, feature_names=data.feature_names)

# ============================================================
# 例7：多分类模型的 SHAP
# ============================================================
# 多分类模型的 SHAP 值形状：(n_classes, n_samples, n_features)
# 每个类别有一组 SHAP 值
# shap_values = explainer.shap_values(X_test)
# shap_values[0] 是类别0的SHAP值，shap_values[1] 是类别1的...

# ============================================================
# 例8：回归模型的 SHAP
# ============================================================
# 回归模型和分类模型用法一样，只是 SHAP 值的单位是目标值的单位
# explainer = shap.TreeExplainer(regression_model)
# shap_values = explainer.shap_values(X_test)
# shap.summary_plot(shap_values, X_test)

# ============================================================
# 例9：其他模型的 SHAP（KernelExplainer / DeepExplainer）
# ============================================================
# 树模型：TreeExplainer（最快，精确计算）
# 线性模型：LinearExplainer
# 深度学习：DeepExplainer（TensorFlow/PyTorch）
# 任意模型：KernelExplainer（模型无关，用核方法近似，较慢）

# KernelExplainer 示例（模型无关）
# def model_predict(X):
#     return model.predict_proba(X)[:, 1]
# 
# # 用背景数据集（通常取训练集的子集或 K-Means 聚类中心）
# background = shap.sample(X_train, 100)
# explainer = shap.KernelExplainer(model_predict, background)
# shap_values = explainer.shap_values(X_test[:50])  # 只解释前50个（慢）

# ============================================================
# 例10：SHAP 特征重要性 vs 模型内置特征重要性
# ============================================================
# 模型内置特征重要性（如 XGBoost 的 feature_importances_）：
# - 基于增益（gain）、覆盖（cover）或频率（frequency）
# - 只能全局排序，不能看单个样本
# - 不能看特征值高低如何影响预测

# SHAP 特征重要性：
# - 基于 Shapley 值，有博弈论理论保证
# - 可以全局排序，也可以局部解释单个样本
# - 可以看特征值高低的影响方向和大小
# - 可以发现特征交互效应

# 对比：
import pandas as pd
# 模型内置重要性
builtin_importance = pd.Series(model.feature_importances_, index=data.feature_names).sort_values(ascending=False)
print("模型内置特征重要性 Top 5:")
print(builtin_importance.head())

# SHAP 重要性
shap_importance = pd.Series(np.abs(shap_values).mean(axis=0), index=data.feature_names).sort_values(ascending=False)
print("\nSHAP 特征重要性 Top 5:")
print(shap_importance.head())

# 两者排序可能不同，SHAP 更可靠（有理论保证）

# ============================================================
# 例11：SHAP 的实际应用场景
# ============================================================
# 1. 模型调试：发现模型依赖了不合理的特征（如数据泄露）
# 2. 特征选择：用 SHAP 重要性筛选重要特征，去掉无用特征
# 3. 业务解释：向业务方解释模型为什么做出这个预测（如信贷审批）
# 4. 公平性分析：检查模型是否对某些群体有偏见
# 5. 异常检测：找出预测异常的样本，分析原因
# 6. 特征工程：通过 SHAP 依赖图发现非线性关系，指导特征变换

# 示例：用 SHAP 发现数据泄露
# 如果某个特征的 SHAP 值异常高，且该特征在预测时不可用，可能是数据泄露
# 例如：预测用户是否流失，但"注销时间"特征的 SHAP 值最高（明显泄露）
```

### SHAP 图表速查

| 图表 | 解释级别 | 用途 |
|---|---|---|
| Waterfall Plot | 局部 | 单样本特征贡献瀑布图 |
| Force Plot | 局部 | 单样本交互式力图 |
| Decision Plot | 局部+全局 | 多样本预测路径对比 |
| Summary Plot (Beeswarm) | 全局 | 特征重要性+值影响方向 |
| Summary Plot (Bar) | 全局 | 特征重要性排名 |
| Dependence Plot | 全局 | 单特征值与预测的关系 |
| Interaction Plot | 全局 | 特征交互效应 |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 树模型用 KernelExplainer | 计算极慢 | 树模型必须用 TreeExplainer（精确且快） |
| 多分类 SHAP 值索引错误 | 形状不对 | 多分类 shap_values 是 (n_classes, n_samples, n_features) |
| 不理解基准值 | 解释不清楚 | 基准值是所有样本的平均预测（logit空间），SHAP值之和=预测-基准 |
| 用 SHAP 代替特征工程 | 本末倒置 | SHAP 是解释工具，不是特征选择工具（但可以辅助） |
| 样本量太大计算慢 | KernelExplainer 尤其慢 | 用 TreeExplainer，或只解释部分样本（如测试集前100个） |
| 忽略特征交互 | 只看主效应 | 用 dependence_plot 和 interaction_values 发现交互效应 |
| SHAP 重要性和模型内置重要性混淆 | 以为一样 | 两者可能不同，SHAP 有理论保证更可靠 |

### 动手

1. 训练一个 XGBoost 分类模型，用 SHAP 计算测试集的 SHAP 值
2. 绘制 Summary Plot，找出 Top 5 重要特征，并分析特征值高低对预测的影响
3. 选择一个样本，绘制 Waterfall Plot，解释该样本的预测原因
4. 选择一个重要特征，绘制 Dependence Plot，分析特征值与预测的关系
5. 对比 SHAP 特征重要性和模型内置特征重要性的排序差异
6. （进阶）计算 SHAP 交互值，找出最强的特征交互对
'''

# ========== 找到工具与实践章节并添加 ==========
def find_node_by_title(node, title):
    if node.get("title") == title:
        return node
    for child in node.get("children", []):
        result = find_node_by_title(child, title)
        if result:
            return result
    return None

tools_chapter = find_node_by_title(data, "工具与实践")
print(f"工具与实践章节原有 {len(tools_chapter['children'])} 子节点")

# 添加4个新叶子
new_leaves = [
    make_leaf("ml-xgboost-lightgbm", "XGBoost与LightGBM", xgb_content),
    make_leaf("ml-ensemble", "模型融合与Stacking", ensemble_content),
    make_leaf("ml-tuning", "超参数调优", tuning_content),
    make_leaf("ml-shap", "SHAP模型可解释性", shap_content),
]

tools_chapter["children"].extend(new_leaves)
print(f"工具与实践章节现有 {len(tools_chapter['children'])} 子节点")

# 保存
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["ml"]={new_json_str}\n'

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-ml.js size: {len(new_content)} bytes")
print("机器学习实战工具补充完成！新增4篇：")
print("  1. XGBoost与LightGBM")
print("  2. 模型融合与Stacking")
print("  3. 超参数调优")
print("  4. SHAP模型可解释性")
