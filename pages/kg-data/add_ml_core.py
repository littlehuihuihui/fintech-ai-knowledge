#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充机器学习核心缺失：scikit-learn、PCA降维、交叉验证"""

import json, re

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

# ========== scikit-learn 工具入门 ==========
leaf_sklearn = make_leaf("ml-sklearn", "scikit-learn 入门", "??", """### 课前

- **场景**：学了一堆机器学习算法理论，要真正跑起来做预测，需要一个统一的工具库。
- **目标**：掌握 scikit-learn 的统一 API 设计（fit/predict/transform）、常用模块、建模全流程。
- **先修**：Python 基础、pandas、机器学习基础范式

### 是什么

- **一句话定义**：scikit-learn（sklearn）是 Python 最主流的机器学习库，提供统一的 API 封装了分类、回归、聚类、降维、特征工程、模型评估等几乎所有经典算法，是数据分析师的必备工具。
- **核心设计**：所有模型遵循统一接口——`fit()` 训练、`predict()` 预测、`transform()` 转换、`score()` 评估。
- **六大模块**：分类（sklearn.ensemble、sklearn.linear_model、sklearn.svm、sklearn.neighbors）、回归、聚类（sklearn.cluster）、降维（sklearn.decomposition）、特征工程（sklearn.preprocessing、sklearn.feature_selection）、模型评估（sklearn.metrics、sklearn.model_selection）。

### 怎么写

```python
# ===== scikit-learn 建模全流程 =====

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. 加载数据
data = pd.read_csv("data.csv")
X = data.drop("target", axis=1)  # 特征
y = data["target"]                # 标签

# 2. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
# test_size=0.2：20% 作为测试集
# random_state=42：固定随机种子，结果可复现
# stratify=y：按标签分层抽样，保持训练/测试集类别比例一致

# 3. 特征预处理（标准化）
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # 训练集：fit + transform
X_test_scaled = scaler.transform(X_test)        # 测试集：只 transform（用训练集的均值方差）
# 注意：测试集不能 fit，否则数据泄露！

# 4. 创建模型并训练
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train_scaled, y_train)  # 训练：统一用 fit()

# 5. 预测
y_pred = model.predict(X_test_scaled)        # 预测类别
y_pred_proba = model.predict_proba(X_test_scaled)  # 预测概率

# 6. 评估
print("准确率:", accuracy_score(y_test, y_pred))
print("\n分类报告:")
print(classification_report(y_test, y_pred))
print("\n混淆矩阵:")
print(confusion_matrix(y_test, y_pred))

# 7. 交叉验证（更可靠的评估）
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring="accuracy")
print(f"5折交叉验证准确率: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# 8. 特征重要性（树模型特有）
importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)
print(importance.head(10))
```

### 统一 API 速查

| 操作 | 方法 | 说明 |
|---|---|---|
| 训练模型 | `model.fit(X, y)` | 监督学习；无监督学习 `fit(X)` |
| 预测 | `model.predict(X)` | 分类/回归都用这个 |
| 预测概率 | `model.predict_proba(X)` | 分类模型返回各类别概率 |
| 转换数据 | `transformer.transform(X)` | 标准化/PCA/编码等 |
| 训练+转换 | `transformer.fit_transform(X)` | 训练集用，一步到位 |
| 评估 | `model.score(X, y)` | 分类返回准确率，回归返回 R² |
| 交叉验证 | `cross_val_score(model, X, y, cv=5)` | k 折交叉验证 |

### 常用模块与类

```python
# 预处理
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer  # 缺失值填充

# 特征选择
from sklearn.feature_selection import SelectKBest, RFE

# 降维
from sklearn.decomposition import PCA

# 分类模型
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# 回归模型
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# 聚类
from sklearn.cluster import KMeans, DBSCAN

# 模型评估
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report, mean_squared_error, r2_score)
from sklearn.model_selection import (train_test_split, cross_val_score, 
                                      GridSearchCV, StratifiedKFold)

# 管道（防止数据泄露的最佳实践）
from sklearn.pipeline import Pipeline
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestClassifier())
])
pipeline.fit(X_train, y_train)
pipeline.score(X_test, y_test)
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 测试集也做 fit_transform | 数据泄露，评估结果虚高 | 测试集只用 transform()，用训练集 fit 出的参数 |
| 不划分训练/测试集直接评估 | 过拟合，模型在新数据上表现差 | 必须 train_test_split，或用交叉验证 |
| 类别不平衡时用准确率评估 | 误导（全猜多数类也能90%准确率） | 用精确率/召回率/F1/AUC，或 stratify 分层抽样 |
| 模型参数不调 | 效果不好 | 用 GridSearchCV 或 RandomizedSearchCV 调参 |
| 不用 Pipeline 分步处理 | 交叉验证时数据泄露 | 用 Pipeline 把预处理和模型封装在一起 |
| random_state 不固定 | 每次结果不同，无法复现 | 所有涉及随机的地方都设 random_state=42 |

### 动手

1. 用 scikit-learn 完整跑一个分类任务：加载数据→划分训练测试集→标准化→训练随机森林→评估准确率/F1/AUC
2. 用 Pipeline 封装标准化+模型，再用 cross_val_score 做 5 折交叉验证
3. 用 GridSearchCV 调优随机森林的 n_estimators 和 max_depth 参数
""")

# ========== PCA 降维 ==========
leaf_pca = make_leaf("ml-pca", "PCA 降维", "???", """### 课前

- **场景**：特征有几百维，模型训练慢、过拟合、可视化不了，需要把高维数据压缩到低维同时保留主要信息。
- **目标**：掌握 PCA（主成分分析）的原理、scikit-learn 用法、方差解释率选择、降维可视化。
- **先修**：线性代数基础（特征值/特征向量）、scikit-learn 入门

### 是什么

- **一句话定义**：PCA（Principal Component Analysis，主成分分析）是最常用的无监督降维方法，通过线性变换将高维特征投影到正交的主成分方向上，在保留最大方差（信息量）的同时降低维度。
- **核心思想**：找到数据方差最大的方向（第一主成分），然后找与它正交的方差次大的方向（第二主成分），依此类推，取前 k 个主成分作为降维后的特征。
- **主要用途**：数据可视化（高维→2D/3D）、加速模型训练、减少过拟合、去除噪声、特征压缩。

### 怎么写

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris

# 1. 加载数据（以鸢尾花为例，4个特征）
iris = load_iris()
X = iris.data  # 150样本 × 4特征
y = iris.target

# 2. 标准化（PCA 对尺度敏感，必须先标准化！）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. PCA 降维到 2 维（用于可视化）
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

print(f"原始维度: {X.shape[1]}")
print(f"降维后维度: {X_pca.shape[1]}")
print(f"各主成分方差解释率: {pca.explained_variance_ratio_}")
print(f"累计方差解释率: {sum(pca.explained_variance_ratio_):.4f}")
# 输出示例：
# 各主成分方差解释率: [0.7277 0.2303]
# 累计方差解释率: 0.9581（前2个主成分保留了95.8%的信息）

# 4. 可视化降维结果
plt.figure(figsize=(8, 6))
for i, target_name in enumerate(iris.target_names):
    plt.scatter(X_pca[y == i, 0], X_pca[y == i, 1], 
                label=target_name, alpha=0.7)
plt.xlabel("第一主成分 (PC1)")
plt.ylabel("第二主成分 (PC2)")
plt.title("PCA 降维可视化 - 鸢尾花数据集")
plt.legend()
plt.show()

# 5. 选择最佳降维维度：保留 95% 方差
pca_auto = PCA(n_components=0.95)  # 保留95%方差，自动选择维度
X_pca_auto = pca_auto.fit_transform(X_scaled)
print(f"保留95%方差需要的维度数: {pca_auto.n_components_}")
print(f"累计方差解释率: {sum(pca_auto.explained_variance_ratio_):.4f}")

# 6. 绘制方差解释率曲线（碎石图 Scree Plot）
pca_full = PCA()
pca_full.fit(X_scaled)
cumulative_var = np.cumsum(pca_full.explained_variance_ratio_)

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(range(1, len(pca_full.explained_variance_ratio_)+1), 
         pca_full.explained_variance_ratio_, 'bo-')
plt.xlabel("主成分")
plt.ylabel("方差解释率")
plt.title("碎石图 (Scree Plot)")

plt.subplot(1, 2, 2)
plt.plot(range(1, len(cumulative_var)+1), cumulative_var, 'ro-')
plt.axhline(y=0.95, color='gray', linestyle='--', label='95% 阈值')
plt.xlabel("主成分数量")
plt.ylabel("累计方差解释率")
plt.title("累计方差解释率")
plt.legend()
plt.tight_layout()
plt.show()

# 7. PCA 在建模管道中的应用
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=0.95)),  # 保留95%方差
    ("model", RandomForestClassifier(random_state=42))
])
pipeline.fit(X_train, y_train)
print(f"测试集准确率: {pipeline.score(X_test, y_test):.4f}")
```

### PCA 核心概念

| 概念 | 说明 |
|---|---|
| 主成分（PC） | 数据方差最大的正交方向，按方差从大到小排列 |
| 方差解释率 | 每个主成分保留的信息量占比，所有主成分之和=1 |
| 累计方差解释率 | 前 k 个主成分的方差解释率之和，通常取 95% 或 99% |
| 特征向量 | 主成分的方向向量，即投影矩阵 |
| 特征值 | 每个主成分的方差大小，特征值越大信息量越多 |
| 碎石图（Scree Plot） | 各主成分方差解释率的折线图，用于选择降维维度 |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 不标准化直接 PCA | 量纲大的特征主导主成分，结果错误 | PCA 前必须 StandardScaler 标准化 |
| 用 PCA 处理分类特征 | 结果无意义 | 分类特征先 OneHot 编码，或用 MCA（多重对应分析） |
| 降维维度选太少 | 信息丢失过多，模型效果下降 | 用累计方差解释率≥95% 来选择维度 |
| 以为 PCA 能做特征选择 | PCA 是特征提取（线性组合），不是特征选择 | 需要保留原始特征含义时用特征选择（SelectKBest/RFE） |
| 测试集也 fit PCA | 数据泄露 | 测试集只用 transform()，用训练集 fit 出的投影矩阵 |
| 降维后不解释主成分含义 | 业务方看不懂 | 分析主成分的特征向量，解释每个 PC 主要由哪些原始特征构成 |

### 动手

1. 对一个高维数据集（如手写数字 MNIST，784维）做 PCA 降维到 2 维并可视化
2. 绘制碎石图，确定保留 95% 方差需要多少个主成分
3. 对比 PCA 降维前后模型的训练时间和准确率
""")

# ========== 交叉验证 ==========
leaf_cv = make_leaf("ml-cross-val", "交叉验证", "???", """### 课前

- **场景**：单次 train_test_split 的评估结果不稳定（换个随机种子结果就变），需要更可靠的模型评估方法。
- **目标**：掌握 k 折交叉验证、分层交叉验证、时间序列交叉验证、交叉验证在调参中的应用。
- **先修**：训练/验证/测试集划分、scikit-learn 入门

### 是什么

- **一句话定义**：交叉验证（Cross Validation）是一种更可靠的模型评估方法，将数据集分成 k 份，轮流用 k-1 份训练、1 份验证，重复 k 次后取平均性能，避免单次划分的偶然性。
- **核心思想**：每个样本都有机会被用作验证集，评估结果更稳定、更可信。
- **常用类型**：k 折交叉验证（KFold）、分层 k 折（StratifiedKFold）、留一法（LOOCV）、时间序列分割（TimeSeriesSplit）、重复 k 折（RepeatedKFold）。

### 怎么写

```python
import numpy as np
from sklearn.model_selection import (
    KFold, StratifiedKFold, cross_val_score, cross_val_predict,
    TimeSeriesSplit, GridSearchCV, RepeatedStratifiedKFold
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.datasets import load_iris

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target
model = RandomForestClassifier(n_estimators=100, random_state=42)

# ===== 1. 最简单：cross_val_score =====
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"5折交叉验证准确率: {scores}")
print(f"平均准确率: {scores.mean():.4f} ± {scores.std():.4f}")
# cv=5：分成5份，轮流验证
# scoring：评估指标，分类用 accuracy/f1/roc_auc，回归用 neg_mean_squared_error/r2

# 多指标评估
from sklearn.model_selection import cross_validate
results = cross_validate(model, X, y, cv=5, 
                         scoring=["accuracy", "f1_macro", "roc_auc_ovr"],
                         return_train_score=True)
print(f"测试集准确率: {results['test_accuracy'].mean():.4f}")
print(f"测试集F1: {results['test_f1_macro'].mean():.4f}")
print(f"训练集准确率: {results['train_accuracy'].mean():.4f}")
# 训练集和测试集差距大 → 过拟合

# ===== 2. 分层 k 折（分类任务推荐）=====
# 普通 KFold 可能导致某一折全是多数类，评估不准
# StratifiedKFold 保持每折中类别比例与整体一致
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_strat = cross_val_score(model, X, y, cv=skf, scoring="accuracy")
print(f"分层5折准确率: {scores_strat.mean():.4f} ± {scores_strat.std():.4f}")

# 手动实现每折（便于自定义逻辑）
for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    print(f"第{fold}折: 验证集准确率={acc:.4f}, 验证集大小={len(val_idx)}")

# ===== 3. 时间序列交叉验证 =====
# 时间序列不能随机打乱！必须用过去预测未来
tscv = TimeSeriesSplit(n_splits=5)
# 第1折：前1/6训练，第2/6验证
# 第2折：前2/6训练，第3/6验证
# ... 训练集逐渐扩大，验证集始终在未来
for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
    print(f"第{fold}折: 训练索引[{train_idx[0]}:{train_idx[-1]}], 验证索引[{val_idx[0]}:{val_idx[-1]}]")

# ===== 4. 交叉验证 + 网格搜索调参 =====
param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5, 10]
}
grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring="f1_macro",
    n_jobs=-1,  # 用所有CPU核心并行
    verbose=1
)
grid_search.fit(X, y)
print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳交叉验证F1: {grid_search.best_score_:.4f}")
best_model = grid_search.best_estimator_

# ===== 5. 交叉验证预测（cross_val_predict）=====
# 每个样本的预测结果来自它作为验证集时的模型
y_pred_cv = cross_val_predict(model, X, y, cv=5)
print(f"交叉验证预测的混淆矩阵:\n{confusion_matrix(y, y_pred_cv)}")
# 注意：cross_val_predict 不是模型的预测方法，而是评估工具
# 最终模型还是要用全部数据 fit 后再预测新数据

# ===== 6. 重复 k 折（结果更稳定）=====
rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
# 5折 × 重复10次 = 50次评估，结果非常稳定
scores_repeated = cross_val_score(model, X, y, cv=rskf, scoring="accuracy")
print(f"重复10次5折准确率: {scores_repeated.mean():.4f} ± {scores_repeated.std():.4f}")
```

### 交叉验证类型对比

| 类型 | 适用场景 | 特点 |
|---|---|---|
| KFold | 回归、数据分布均匀 | 随机划分，简单通用 |
| StratifiedKFold | 分类（推荐） | 保持每折类别比例一致 |
| TimeSeriesSplit | 时间序列 | 训练集在过去，验证集在未来，不打乱 |
| LeaveOneOut (LOOCV) | 小数据集 | 留一个样本验证，k=N，计算量大 |
| RepeatedKFold | 需要稳定评估 | 重复多次 k 折，取平均 |
| GroupKFold | 有分组的数据 | 同一组不出现在训练和验证集（如同一用户） |

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 分类任务用普通 KFold | 类别不平衡时某折评估不准 | 用 StratifiedKFold 分层抽样 |
| 时间序列随机打乱交叉验证 | 数据泄露，用未来预测过去 | 用 TimeSeriesSplit，不 shuffle |
| 交叉验证后直接用模型预测 | 模型只在最后一折训练了，不完整 | 交叉验证只用于评估，最终模型要用全部数据重新 fit |
| 调参时用测试集做交叉验证 | 测试集信息泄露，调参过拟合 | 调参用训练集做交叉验证，测试集只用于最终评估 |
| k 折数选太小或太大 | k=2 不稳定，k=N 计算慢 | 常用 k=5 或 k=10，平衡稳定性和计算量 |
| 预处理在交叉验证外做 | 验证集信息泄露到预处理中 | 用 Pipeline 把预处理和模型封装，在每折内 fit |

### 动手

1. 对比单次 train_test_split 和 5 折交叉验证的评估结果稳定性（跑 10 次取方差）
2. 用 StratifiedKFold 手动实现 5 折交叉验证，每折输出混淆矩阵
3. 用 GridSearchCV + 交叉验证调优一个模型的超参数，输出最佳参数和得分
""")

# ========== 读取并修改 embed-ml.js ==========
with open(r"D:\cursor\数据学习平台\kg-data\embed-ml.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["ml"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

# 找到"评估与落地"节点，添加交叉验证
def find_node(node, node_id):
    if node.get("id") == node_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result:
            return result
    return None

# 1. 在"离线评估"章节添加交叉验证
eval_ch = find_node(data, "ml-eval-ch")
if eval_ch:
    existing_ids = [c["id"] for c in eval_ch["children"]]
    if "ml-cross-val" not in existing_ids:
        eval_ch["children"].insert(0, leaf_cv)
        print("✓ 交叉验证已添加到 离线评估 章节")

# 2. 在"经典模型"同级添加 scikit-learn 工具节点
# 找到 ml-models 的父节点（根节点），在 ml-models 后插入
root_children = data["children"]
ml_models_idx = None
for i, child in enumerate(root_children):
    if child.get("id") == "ml-models":
        ml_models_idx = i
        break

if ml_models_idx is not None:
    existing_ids = [c["id"] for c in root_children]
    if "ml-sklearn-chapter" not in existing_ids:
        # 创建一个工具章节
        sklearn_chapter = {
            "id": "ml-sklearn-chapter",
            "title": "工具与实践",
            "level": "??",
            "content": """### 课前 · 章节导读

- **章节**：工具与实践
- **为什么学本章**：理论学完要落地，scikit-learn 是机器学习最核心的工具库，PCA 是最常用的降维方法。
- **学习目标**：能用 scikit-learn 完整跑通建模流程，能用 PCA 做降维和可视化。
- **先修**：Python 基础、pandas、机器学习基础范式

### 本章叶课地图

| # | 叶课 | 难度 | 一句话 |
|---|---|---|---|
| 1 | scikit-learn 入门 | ?? | 统一API、建模全流程、常用模块 |
| 2 | PCA 降维 | ??? | 主成分分析、方差解释率、降维可视化 |

### 推荐顺序

```text
scikit-learn 入门 → PCA 降维
```

### 下一动

点开第 1 片绿色叶节点。本章合计约 **2** 片叶讲义。
""",
            "lessonParent": True,
            "children": [leaf_sklearn, leaf_pca]
        }
        root_children.insert(ml_models_idx + 1, sklearn_chapter)
        print("✓ 工具与实践 章节已添加（含 scikit-learn、PCA）")

# 序列化
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["ml"]={new_json_str}\n'

with open(r"D:\cursor\数据学习平台\kg-data\embed-ml.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-ml.js size: {len(new_content)} bytes")
print("机器学习核心内容补充完成")
