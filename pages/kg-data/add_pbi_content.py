#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充 Power BI 详细内容"""

import json, re

def make_leaf(node_id, title, level, content):
    return {"id": node_id, "title": title, "level": level, "content": content, "children": []}

# ========== 新叶子节点 ==========

leaf_pq = make_leaf("BI.Power BI.Power Query", "Power Query 数据获取", "??", """### 课前

- **场景**：要从 Excel、数据库、API 等多种来源获取数据，清洗后加载到 Power BI 模型。
- **目标**：掌握 Power Query（M 语言）的数据获取、清洗、转换流程，常用操作。
- **先修**：Power BI 基础

### 是什么

- **一句话定义**：Power Query 是 Power BI 的数据连接和清洗引擎，通过图形化界面或 M 语言实现从多种数据源获取、清洗、转换数据，是 Power BI 的 ETL 层。
- **核心能力**：连接 100+ 数据源、数据清洗、类型转换、合并追加、逆透视、分组聚合、参数化、自定义函数。

### 怎么写

```text
# Power Query 常用操作（图形化界面，自动生成 M 代码）

# 1. 获取数据
#    主页 → 获取数据 → 选择数据源：
#    - Excel/CSV/文本文件
#    - 数据库：SQL Server / Oracle / MySQL / PostgreSQL
#    - 在线服务：SharePoint / Dynamics / Salesforce
#    - Web：从 URL 获取 JSON/HTML
#    - 空白查询：手写 M 代码

# 2. 常用清洗步骤（添加列 → 转换）
#    - 提升标题：将第一行作为列名
#    - 更改类型：文本/整数/小数/日期/布尔
#    - 移除列/选择列：删除不需要的列
#    - 重命名列
#    - 替换值：查找替换
#    - 填充：向下/向上填充空值
#    - 删除重复项
#    - 拆分列：按分隔符拆分
#    - 合并列：多列合并为一列

# 3. 表操作
#    - 追加查询：纵向合并多个表（UNION ALL）
#    - 合并查询：横向关联（JOIN），选择连接类型和匹配列
#    - 逆透视列：宽表变长表（列转行）
#    - 透视列：长表变宽表（行转列）
#    - 分组依据：分组聚合（GROUP BY）
#    - 排序/筛选行

# 4. 参数化
#    主页 → 管理参数 → 新建参数：
#    - 服务器名、数据库名、文件路径、日期范围
#    - 在查询中引用参数，方便环境切换和增量刷新

# 5. 自定义函数（M 语言）
#    高级编辑器中编写函数，可复用逻辑：
#    (table as table) as table =>
#    let
#        源 = table,
#        清洗 = Table.TransformColumnTypes(源, {{"金额", type number}})
#    in
#        清洗
```

### M 语言基础

```powerquery-m
// M 语言基本语法
let
    // 步骤1：获取数据
    源 = Excel.Workbook(File.Contents("C:\data\sales.xlsx"), null, true),
    Sheet1 = 源{[Item="Sheet1",Kind="Sheet"]}[Data],
    
    // 步骤2：提升标题
    提升标题 = Table.PromoteHeaders(Sheet1, [PromoteAllScalars=true]),
    
    // 步骤3：更改类型
    更改类型 = Table.TransformColumnTypes(提升标题, {
        {"订单号", type text}, 
        {"金额", type number}, 
        {"日期", type date}
    }),
    
    // 步骤4：筛选
    筛选 = Table.SelectRows(更改类型, each [金额] > 100)
in
    筛选
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 在报表视图里改数据类型 | 只影响显示，不影响模型 | 数据清洗在 Power Query 里做 |
| 忘记设置正确的数据类型 | DAX 计算错误或可视化异常 | 每列都要确认类型，尤其是日期和数字 |
| 大表全量加载到 Power Query | 刷新慢、内存占用高 | 尽量在数据源侧过滤（查询折叠），只取需要的列和行 |
| 合并查询时选了错误的连接类型 | 数据丢失或重复 | 理解左外/右外/完全外部/内部连接的区别 |
| 硬编码文件路径 | 换电脑后刷新失败 | 用参数化路径，或使用相对路径/SharePoint |

### 动手

1. 用 Power Query 从 Excel 获取数据，提升标题、更改类型、筛选金额>100 的行
2. 用合并查询把订单表和用户表按 user_id 关联（左外连接）
3. 用逆透视列把宽表（1月/2月/3月列）转成长表（月份/值列）
""")

leaf_dax_func = make_leaf("BI.Power BI.DAX 常用函数", "DAX 常用函数", "??", """### 课前

- **场景**：要写度量值计算同比环比、累计值、占比、筛选条件下的聚合，需要掌握常用 DAX 函数。
- **目标**：掌握 DAX 常用函数分类：聚合、时间智能、筛选、逻辑、信息、数学统计。
- **先修**：DAX 度量基础

### 是什么

- **一句话定义**：DAX（Data Analysis Expressions）是 Power BI 的公式语言，用于创建度量值、计算列、计算表，支持丰富的函数库实现复杂业务逻辑。
- **函数分类**：聚合函数、时间智能函数、筛选函数、逻辑函数、信息函数、数学统计函数、文本函数、关系函数。

### 常用函数详解

#### 1. 聚合函数

```dax
-- 基础聚合
总销售额 = SUM(Sales[Amount])
平均金额 = AVERAGE(Sales[Amount])
订单数 = COUNT(Sales[OrderID])
不重复客户数 = DISTINCTCOUNT(Sales[CustomerID])
最大金额 = MAX(Sales[Amount])
最小金额 = MIN(Sales[Amount])

-- 带条件聚合（SUMX 系列，逐行计算后聚合）
总折扣金额 = SUMX(Sales, Sales[Amount] * Sales[DiscountRate])
平均订单金额 = AVERAGEX(VALUES(Sales[OrderID]), [总销售额])
```

#### 2. 时间智能函数（最常用，需日期表）

```dax
-- 同比/环比
本月销售额 = CALCULATE([总销售额], DATESMTD('Date'[Date]))
上月销售额 = CALCULATE([总销售额], DATEADD('Date'[Date], -1, MONTH))
去年同期 = CALCULATE([总销售额], SAMEPERIODLASTYEAR('Date'[Date]))
同比增长率 = DIVIDE([本月销售额] - [去年同期], [去年同期])

-- 累计/YTD
年初至今 = CALCULATE([总销售额], DATESYTD('Date'[Date]))
季度累计 = CALCULATE([总销售额], DATESQTD('Date'[Date]))
移动平均3月 = CALCULATE([总销售额], DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH))

-- 期初/期末
期初库存 = CALCULATE([库存量], OPENINGBALANCEMONTH('Date'[Date]))
期末库存 = CALCULATE([库存量], CLOSINGBALANCEMONTH('Date'[Date]))
```

#### 3. 筛选函数（DAX 的核心，控制计算上下文）

```dax
-- CALCULATE：修改筛选上下文（最重要的函数）
华东销售额 = CALCULATE([总销售额], Sales[Region] = "华东")
剔除退款 = CALCULATE([总销售额], Sales[Status] <> "Refund")
多条件 = CALCULATE([总销售额], Sales[Region]="华东", Sales[Amount]>100)

-- FILTER：返回筛选后的表（用于复杂条件）
高价值客户数 = CALCULATE(DISTINCTCOUNT(Sales[CustomerID]), 
    FILTER(VALUES(Sales[CustomerID]), [总销售额] > 10000))

-- ALL / ALLEXCEPT：移除筛选
全渠道销售额 = CALCULATE([总销售额], ALL(Sales[Channel]))
占比 = DIVIDE([总销售额], CALCULATE([总销售额], ALLSELECTED()))

-- KEEPFILTERS：保留外部筛选（与 CALCULATE 的覆盖行为区分）
华东且外部筛选 = CALCULATE([总销售额], KEEPFILTERS(Sales[Region] = "华东"))
```

#### 4. 逻辑与条件函数

```dax
-- IF / SWITCH
等级 = IF([总销售额] > 10000, "A", IF([总销售额] > 5000, "B", "C"))
状态文本 = SWITCH(TRUE(),
    [总销售额] > 10000, "高价值",
    [总销售额] > 5000, "中价值",
    "低价值")

-- AND / OR / NOT
高价值华东 = CALCULATE([总销售额], AND(Sales[Region]="华东", [总销售额]>10000))

-- COALESCE：返回第一个非空值
安全金额 = COALESCE(Sales[Amount], 0)
```

#### 5. 关系与表函数

```dax
-- RELATED：从关联表获取列（多端取一端）
订单城市 = RELATED(Customer[City])

-- VALUES / DISTINCT：返回单列去重表
客户列表 = VALUES(Customer[CustomerID])

-- TOPN：返回前 N 行
Top10客户 = TOPN(10, VALUES(Customer[CustomerID]), [总销售额])

-- SUMMARIZE：分组汇总（类似 GROUP BY）
区域汇总 = SUMMARIZE(Sales, Sales[Region], "销售额", [总销售额], "订单数", [订单数])
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 度量值里直接引用列而不聚合 | 报错"需要聚合" | 度量值必须用聚合函数包裹列，或用 CALCULATE |
| 时间智能函数不工作 | 返回空或错误 | 必须有标记的日期表，且日期连续无间断 |
| CALCULATE 筛选条件写在 FILTER 里 | 性能差 | 简单条件直接写 CALCULATE 参数，复杂条件才用 FILTER |
| 计算列里用 CALCULATE | 上下文转换，可能结果意外 | 计算列尽量不用 CALCULATE，度量值才是 CALCULATE 的主场 |
| 除法不处理除零 | 显示 Infinity 或错误 | 用 DIVIDE(分子, 分母, 0) 安全除法 |
| ALL 和 ALLSELECTED 混淆 | 占比计算错误 | ALL=忽略所有筛选，ALLSELECTED=保留外部切片器筛选 |

### 动手

1. 写一个度量值：计算本月销售额、上月销售额、环比增长率
2. 写一个度量值：计算华东地区销售额占总销售额的百分比（用 ALLSELECTED）
3. 写一个度量值：用 SWITCH 根据销售额给客户分等级（A/B/C）
""")

leaf_viz = make_leaf("BI.Power BI.可视化与交互", "可视化与交互", "??", """### 课前

- **场景**：数据模型和度量值都建好了，要做美观、交互性强的报表给业务看。
- **目标**：掌握 Power BI 常用可视化图表、交互设置、格式美化、钻取、书签、工具提示。
- **先修**：DAX 度量

### 是什么

- **一句话定义**：Power BI 报表视图提供丰富的可视化图表和交互功能，通过拖拽字段、设置格式、配置交互来制作数据故事，是业务用户消费数据的接口。
- **核心能力**：30+ 原生图表、自定义视觉对象、切片器筛选、钻取、书签、工具提示、条件格式、主题。

### 常用图表选择

| 图表类型 | 适用场景 | 示例 |
|---|---|---|
| 柱状图/条形图 | 类别对比、排名 | 各区域销售额对比、Top10 客户 |
| 折线图/面积图 | 趋势变化、时间序列 | 月度销售额趋势、库存变化 |
| 饼图/环形图 | 占比构成（类别少） | 渠道占比、性别比例 |
| 组合图（柱+线） | 双指标对比（量+率） | 销售额（柱）+ 增长率（线） |
| 矩阵/表格 | 明细数据、交叉表 | 产品×区域销售矩阵 |
| 卡片/多行卡片 | 核心 KPI 指标 | 总销售额、订单数、客户数 |
| KPI 指示器 | 目标达成、趋势 | 销售额 vs 目标、同比 |
| 散点图 | 相关性分析、分布 | 金额 vs 数量、客户分群 |
| 地图 | 地理分布 | 各省市销售额、门店分布 |
| 漏斗图 | 转化漏斗 | 访问→加购→下单→支付 |
| 桑基图 | 流向分析 | 用户行为路径、资金流向 |
| 热力图 | 密度/强度 | 时段×星期订单密度 |

### 交互设置

```text
# 1. 切片器（Slicer）
#    可视化 → 切片器 → 拖入字段（日期/区域/类别）
#    格式设置：
#    - 日期切片器： between（范围）/ before / after / 列表 / 下拉
#    - 单选/多选：格式 → 切片器设置 → 单选
#    - 全选按钮：格式 → 切片器设置 → 显示"全选"
#    - 垂直/水平布局

# 2. 视觉对象交互（Edit interactions）
#    格式 → 编辑交互
#    选中一个视觉对象，其他视觉对象显示：
#    - 筛选（Filter）：点击后筛选其他图表
#    - 高亮（Highlight）：点击后高亮对应部分（默认）
#    - 无（None）：不响应点击
#    按需设置每个图表的交互行为

# 3. 钻取（Drillthrough）
#    (1) 层级钻取：在字段里建立层级（年→季→月→日）
#        图表右上角出现钻取按钮，可上钻/下钻
#    (2) 页面钻取：新建详情页 → 页面设置 → 钻取 → 添加钻取字段
#        主页面右键数据点 → 钻取 → 跳转到详情页（自动带筛选）

# 4. 书签（Bookmark）
#    视图 → 书签 → 添加书签
#    保存当前页面状态（筛选、可视化可见性、排序）
#    用途：
#    - 视图切换（如汇总视图/明细视图）
#    - 分步演示（讲故事）
#    - 自定义导航（按钮+书签）

# 5. 工具提示（Tooltip）
#    新建工具提示页 → 页面设置 → 工具提示页面
#    在图表格式 → 工具提示 → 选择工具提示页
#    鼠标悬停时显示自定义的迷你图表（而非默认数据列表）

# 6. 按钮（Button）
#    插入 → 按钮 → 选择类型（后退/书签/问答/链接）
#    配置操作类型和目标
#    用于自定义导航、视图切换、跳转外部链接
```

### 格式美化要点

```text
# 1. 主题（Theme）
#    视图 → 主题 → 浏览主题（应用官方主题）
#    或自定义主题：颜色、字体、图表默认样式
#    企业报表建议统一品牌色

# 2. 条件格式
#    矩阵/表格 → 格式 → 条件格式：
#    - 背景色色阶（如销售额从低到高渐变）
#    - 字体颜色（如正负值红绿）
#    - 数据条（条形图显示在单元格内）
#    - 图标（上下箭头、等级标记）

# 3. 图表格式
#    - 标题：清晰描述图表内容，字体大小适中
#    - 坐标轴：单位（万/亿）、格式、网格线
#    - 数据标签：关键图表显示数值
#    - 图例：位置（顶部/右侧/底部），类别多时考虑排序
#    - 颜色：同一类别跨图表保持颜色一致

# 4. 页面布局
#    - 页面大小：16:9（默认）/ 4:3 / 自定义
#    - 对齐：视觉对象对齐网格，大小一致
#    - 留白：不要太拥挤，适当留白
#    - 分组：相关图表放在一起，用形状/容器分隔
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 饼图类别太多 | 看不清、颜色难区分 | 超过5个类别用条形图，或合并小类别为"其他" |
| 双轴图表不说明 | 读者误解数据 | 明确标注左右轴分别是什么，单位不同时尤其注意 |
| 所有图表都响应所有点击 | 交互混乱 | 用编辑交互设置合理的筛选/高亮/无响应 |
| 颜色不统一 | 同一类别在不同图表颜色不同 | 用主题或手动设置，确保跨图表颜色一致 |
| 截断纵轴制造假趋势 | 误导决策 | 纵轴尽量从0开始，确需截断时明确标注 |
| 报表太拥挤 | 看不清、找不到重点 | 适当留白，核心KPI放大，次要信息放详情页 |

### 动手

1. 做一个销售仪表盘：顶部3个KPI卡片（销售额/订单数/客户数），中间柱状图（区域销售），底部折线图（月度趋势）
2. 添加日期切片器和区域切片器，设置编辑交互让柱状图点击后筛选折线图
3. 给矩阵添加条件格式：销售额列用数据条，增长率列用红绿字体颜色
""")

leaf_security = make_leaf("BI.Power BI.发布与安全", "发布与安全", "???", """### 课前

- **场景**：报表做好了，要发布给业务用户看，需要控制谁能看什么数据，确保数据安全。
- **目标**：掌握 Power BI 发布、共享、权限管理、行级安全（RLS）、增量刷新、网关配置。
- **先修**：可视化与交互

### 是什么

- **一句话定义**：Power BI 发布与安全涵盖从本地报表到云端共享的全流程，包括发布到服务、工作区权限管理、行级安全控制数据可见范围、增量刷新优化大数据刷新、本地数据网关连接内部数据源。
- **核心能力**：发布共享、角色权限、RLS 行级安全、增量刷新、网关、应用工作区。

### 怎么写

```text
# ===== 1. 发布与共享 =====

# (1) 发布到 Power BI 服务
#    Power BI Desktop → 主页 → 发布
#    选择工作区（我的工作区/团队工作区）
#    发布后可在 powerbi.com 网页端查看

# (2) 共享方式
#    - 直接共享：报表 → 共享 → 输入用户邮箱
#    - 发布应用：工作区 → 创建应用 → 配置导航/权限 → 发布
#      （适合大量用户，统一入口，权限可控）
#    - 导出：导出为 PDF/PPT/Excel（静态，无交互）
#    - 嵌入：嵌入到 SharePoint/Teams/自定义应用

# (3) 工作区角色
#    - 管理员：完全控制（管理权限、删除工作区）
#    - 成员：编辑内容（创建/编辑报表、数据集）
#    - 参与者：查看内容（可查看、导出，不能编辑）
#    - 查看者：仅查看（最基础权限）
#    按需给用户分配角色，遵循最小权限原则


# ===== 2. 行级安全（RLS）=====

# 场景：销售经理只能看自己区域的数据，高管看全部

# (1) 创建角色和规则
#    建模 → 管理角色 → 创建角色（如"区域经理"）
#    选择表 → 输入 DAX 过滤表达式：
#      区域表[区域名称] = USERPRINCIPALNAME()
#    或用映射表：
#      区域表[区域名称] IN 
#        CALCULATETABLE(VALUES(用户区域映射[区域]), 
#          用户区域映射[用户邮箱] = USERPRINCIPALNAME())

# (2) 测试 RLS
#    建模 → 以角色身份查看 → 选择角色
#    输入测试用户邮箱，验证数据筛选是否正确

# (3) 在服务端配置
#    发布后 → 数据集 → 安全 → 角色 → 添加成员
#    将用户/安全组添加到对应角色

# (4) USERPRINCIPALNAME() 函数
#    返回当前登录用户的 UPN（通常是邮箱）
#    用于动态判断当前用户能看到哪些数据


# ===== 3. 增量刷新（Incremental Refresh）=====

# 场景：数据表有几百万行，全量刷新太慢，只刷新最新数据

# (1) 配置步骤
#    a. 创建参数：RangeStart（日期/时间）、RangeEnd（日期/时间）
#    b. 在 Power Query 中用参数过滤：
#       筛选行 = Table.SelectRows(源, each [日期] >= RangeStart and [日期] < RangeEnd)
#    c. 关闭并应用
#    d. 表右键 → 增量刷新 → 配置：
#       - 存档数据开始：如 5 年前
#       - 增量数据开始：如 1 天前
#       - 检测数据更改（可选）：选择时间戳列
#       - 仅刷新完整周期（可选）
#    e. 发布到服务

# (2) 原理
#    Power BI 自动将历史分区（不刷新）和增量分区（每次刷新）分开
#    只刷新最新 N 天的数据，大幅缩短刷新时间
#    历史数据只在首次发布时全量加载

# (3) 注意事项
#    - 必须在 Power Query 中用 RangeStart/RangeEnd 过滤
#    - 过滤列必须是日期/时间类型
#    - 查询折叠必须生效（否则退化为全量）
#    - 大数据源建议配合查询折叠下推到数据库


# ===== 4. 本地数据网关（On-premises Gateway）=====

# 场景：数据源在公司内网（如 SQL Server），Power BI 服务需要连接

# (1) 安装网关
#    下载 Power BI 网关（个人模式/标准模式）
#    安装在能访问数据源的机器上（建议服务器，常开）
#    登录 Power BI 账号，注册网关

# (2) 配置数据源
#    Power BI 服务 → 管理网关 → 添加数据源
#    选择类型（SQL Server/Oracle/文件等）
#    填写连接信息和凭据
#    测试连接成功

# (3) 数据集绑定网关
#    数据集 → 设置 → 网关连接 → 选择网关和数据源
#    配置刷新计划（每日/每周，具体时间）

# (4) 网关模式
#    - 个人模式：单用户，简单，适合个人开发
#    - 标准模式：多用户共享，高可用集群，适合企业
#    - 建议生产环境用标准模式，配置集群高可用


# ===== 5. 生产部署 checklist =====

# □ 报表已测试，数据准确
# □ 性能优化：DAX 优化、增量刷新、查询折叠
# □ 权限规划：工作区角色、RLS 行级安全
# □ 网关配置：数据源连接、刷新计划
# □ 发布应用：配置导航、权限、品牌
# □ 用户培训：使用说明、常见问题
# □ 监控告警：刷新失败告警、使用情况监控
```

### 易错对照

| 错法 | 现象 | 纠正 |
|---|---|---|
| 直接共享报表给大量用户 | 权限混乱，难以管理 | 用发布应用，统一入口和权限 |
| RLS 规则写错 | 用户看到不该看的数据 | 用"以角色身份查看"充分测试，用真实用户验证 |
| 增量刷新不生效（还是全量） | 刷新时间没缩短 | 检查 RangeStart/RangeEnd 过滤、查询折叠是否生效 |
| 网关装在个人电脑上 | 电脑关机后刷新失败 | 网关装在常开的服务器上，配置集群高可用 |
| 数据集刷新失败不告警 | 数据过期没人发现 | 配置刷新失败邮件告警，定期检查刷新历史 |
| 导出 PDF 当交互报表用 | 没有交互，数据静态 | 需要交互用 Power BI 服务/应用，PDF 只用于静态分发 |

### 动手

1. 配置行级安全：创建"区域经理"角色，用 USERPRINCIPALNAME() 过滤，测试不同用户看到的数据
2. 配置增量刷新：创建 RangeStart/RangeEnd 参数，在 Power Query 中过滤，设置增量刷新策略
3. 发布报表到工作区，创建应用，配置导航和权限，分享给测试用户
""")

# ========== 读取并修改 embed-bi.js ==========
with open(r"D:\cursor\数据学习平台\kg-data\embed-bi.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'window\.__KG_EMBEDDED\["bi"\]\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
data = json.loads(match.group(1))

def find_node(node, node_id):
    if node.get("id") == node_id:
        return node
    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result:
            return result
    return None

pbi = find_node(data, "BI.Power BI")
if not pbi:
    print("ERROR: Cannot find Power BI node")
    exit(1)

print(f"Current Power BI leaves: {[c['title'] for c in pbi['children']]}")

# 检查是否已存在新节点
new_leaves = [leaf_pq, leaf_dax_func, leaf_viz, leaf_security]
existing_titles = [c["title"] for c in pbi["children"]]
for leaf in new_leaves:
    if leaf["title"] not in existing_titles:
        pbi["children"].append(leaf)
        print(f"Added: {leaf['title']}")
    else:
        print(f"Already exists: {leaf['title']}")

print(f"New Power BI leaves: {[c['title'] for c in pbi['children']]}")

# 更新 Power BI 节点的 content（更新叶课地图）
pbi_content = pbi["content"]
# 简单替换：在内容末尾添加新章节说明
if "Power Query" not in pbi_content:
    pbi["content"] = pbi_content + """

### 补充内容

本节点已补充以下详细讲义：

| 叶课 | 难度 | 一句话 |
|---|---|---|
| Power Query 数据获取 | ?? | 数据连接、清洗、M 语言、参数化 |
| DAX 常用函数 | ?? | 聚合、时间智能、筛选、逻辑函数详解 |
| 可视化与交互 | ?? | 图表选择、切片器、钻取、书签、格式美化 |
| 发布与安全 | ??? | 发布共享、RLS 行级安全、增量刷新、网关 |
"""

# 序列化
new_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["bi"]={new_json_str}\n'

with open(r"D:\cursor\数据学习平台\kg-data\embed-bi.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\nDone! embed-bi.js size: {len(new_content)} bytes")
print("Power BI 详细内容已补充完成")
