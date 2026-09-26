#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充实时处理与数仓内容：ETL实时流处理、数据压缩序列化、实时数仓、OLAP引擎对比"""

import json, re

def make_leaf(node_id, title, content):
    return {"id": node_id, "title": title, "level": "??", "content": content, "children": []}

def find_node_by_title(node, title):
    if node.get("title") == title:
        return node
    for child in node.get("children", []):
        result = find_node_by_title(child, title)
        if result:
            return result
    return None

# ============================================================
# ETL 部分：实时流处理 + 数据压缩序列化
# ============================================================

etl_streaming_content = '''### 课前

- **场景**：数据需要实时处理和秒级响应，如实时大屏、实时推荐、风控实时计算、监控告警。
- **目标**：掌握流处理核心概念、Flink 和 Spark Streaming 的区别与用法、流批一体架构、实时ETL管道设计。
- **先修**：ETL基础、Kafka消息队列、分布式计算概念

### 是什么

- **一句话定义**：实时流处理是对持续产生的数据流进行实时（秒级/毫秒级）计算和处理的技术，与批处理（T+1）相对，通过流处理引擎（Flink/Spark Streaming）实现低延迟的数据转换、聚合、关联和输出，是现代数据平台的核心能力。
- **批处理 vs 流处理**：
  - **批处理**：有界数据集，定时运行（如每天凌晨），延迟高（小时级），吞吐量大
  - **流处理**：无界数据流，持续运行，延迟低（秒级/毫秒级），需要处理乱序和迟到数据
- **流批一体**：用同一套引擎和API同时处理批和流，Flink 是流批一体的代表。

### 怎么写

```sql
-- ============================================================
-- 例1：流处理核心概念
-- ============================================================
-- 无界数据流（Unbounded Stream）：数据持续产生，没有结束
--   如：用户点击流、交易流水、传感器数据、日志

-- 有界数据流（Bounded Stream）：数据有明确的开始和结束
--   如：昨天的订单数据、历史文件

-- 事件时间（Event Time）vs 处理时间（Processing Time）
--   事件时间：事件实际发生的时间（如用户点击的时间戳）
--   处理时间：流处理引擎收到事件的时间
--   关键区别：网络延迟、系统负载会导致处理时间和事件时间不一致
--   流处理必须基于事件时间，才能正确处理乱序和迟到数据

-- 窗口（Window）：把无界数据流切分成有界的小块进行计算
--   滚动窗口（Tumbling）：固定大小，不重叠（如每5分钟一个窗口）
--   滑动窗口（Sliding）：固定大小，可重叠（如每5分钟计算过去15分钟）
--   会话窗口（Session）：按活动间隙划分（如用户连续活动为一个会话）

-- 水位线（Watermark）：处理乱序和迟到数据的机制
--   水位线表示"到这个时间点为止，不会再有更早的数据了"
--   例如：水位线 = 当前最大事件时间 - 5秒
--   当水位线超过窗口结束时间时，触发窗口计算
--   迟到数据（水位线过后才到达）可以设置允许迟到时间或丢弃

-- 状态（State）：流处理中需要保存的中间计算结果
--   如：过去1小时的用户点击数、用户的会话状态
--   状态需要持久化（Checkpoint/Savepoint），保证故障恢复

-- ============================================================
-- 例2：Flink 基本概念和架构
-- ============================================================
-- Apache Flink：流处理引擎的事实标准，原生支持流处理，流批一体
-- 核心特性：
--   - 事件时间支持（Watermark）
--   - 精确一次语义（Exactly-Once）
--   - 有状态计算（State Backend）
--   - 高可用（Checkpoint + Savepoint）
--   - 流批一体（同一套API处理批和流）

-- Flink 编程模型（DataStream API）：
--   Source → Transform → Sink
--   Source：数据源（Kafka、Socket、文件、自定义）
--   Transform：转换操作（map、filter、keyBy、window、aggregate）
--   Sink：输出（Kafka、数据库、文件、仪表盘）

-- Flink Table API / SQL：
--   用 SQL 写流处理，降低使用门槛
--   支持动态表（Dynamic Table）和连续查询
--   流处理和批处理用同一套 SQL

-- ============================================================
-- 例3：Flink SQL 实时ETL示例
-- ============================================================
-- 场景：实时统计每个区域的销售额，输出到 Kafka 和 MySQL

-- 1. 定义 Source 表（从 Kafka 读取订单流）
-- CREATE TABLE orders (
--   order_id BIGINT,
--   user_id BIGINT,
--   region STRING,
--   amount DECIMAL(10, 2),
--   order_time TIMESTAMP(3),
--   WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
-- ) WITH (
--   'connector' = 'kafka',
--   'topic' = 'orders',
--   'properties.bootstrap.servers' = 'localhost:9092',
--   'properties.group.id' = 'flink-etl',
--   'scan.startup.mode' = 'latest-offset',
--   'format' = 'json'
-- );

-- 2. 定义 Sink 表（输出到 MySQL，实时更新）
-- CREATE TABLE region_sales (
--   region STRING,
--   total_amount DECIMAL(10, 2),
--   order_count BIGINT,
--   PRIMARY KEY (region) NOT ENFORCED
-- ) WITH (
--   'connector' = 'jdbc',
--   'url' = 'jdbc:mysql://localhost:3306/analytics',
--   'table-name' = 'region_sales',
--   'username' = 'root',
--   'password' = 'xxx'
-- );

-- 3. 实时聚合（5分钟滚动窗口）
-- INSERT INTO region_sales
-- SELECT
--   region,
--   SUM(amount) AS total_amount,
--   COUNT(*) AS order_count
-- FROM TABLE(
--   TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '5' MINUTES)
-- )
-- GROUP BY region, window_start, window_end;

-- 4. 实时大屏（输出到 Kafka，供前端消费）
-- CREATE TABLE sales_dashboard (
--   window_start TIMESTAMP(3),
--   region STRING,
--   total_amount DECIMAL(10, 2)
-- ) WITH (
--   'connector' = 'kafka',
--   'topic' = 'sales-dashboard',
--   'properties.bootstrap.servers' = 'localhost:9092',
--   'format' = 'json'
-- );
-- 
-- INSERT INTO sales_dashboard
-- SELECT window_start, region, SUM(amount)
-- FROM TABLE(TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '1' MINUTES))
-- GROUP BY region, window_start, window_end;

-- ============================================================
-- 例4：Spark Streaming / Structured Streaming
-- ============================================================
-- Spark Structured Streaming：Spark 的流处理 API，基于 Spark SQL 引擎
-- 特点：
--   - 和 Spark Batch 统一的 API（DataFrame/Dataset）
--   - 微批处理（Micro-batch），延迟最低约100ms
--   - 连续处理（Continuous）模式，延迟可到1ms（实验性）
--   - 生态丰富（和 Spark MLlib、GraphX 集成）

-- Spark Structured Streaming 示例（Python）：
-- from pyspark.sql import SparkSession
-- from pyspark.sql.functions import *
-- 
-- spark = SparkSession.builder.appName("StreamingETL").getOrCreate()
-- 
-- # 从 Kafka 读取
-- df = spark \
--     .readStream \
--     .format("kafka") \
--     .option("kafka.bootstrap.servers", "localhost:9092") \
--     .option("subscribe", "orders") \
--     .load()
-- 
-- # 解析 JSON
-- parsed = df.select(
--     from_json(col("value").cast("string"), schema).alias("data")
-- ).select("data.*")
-- 
-- # 5分钟窗口聚合
-- windowed = parsed \
--     .withWatermark("order_time", "5 minutes") \
--     .groupBy(window("order_time", "5 minutes"), "region") \
--     .agg(sum("amount").alias("total_amount"))
-- 
-- # 输出到控制台（调试用）
-- query = windowed \
--     .writeStream \
--     .outputMode("update") \
--     .format("console") \
--     .start()
-- 
-- query.awaitTermination()

-- ============================================================
-- 例5：Flink vs Spark Streaming 对比
-- ============================================================
-- | 维度 | Apache Flink | Spark Structured Streaming |
-- |---|---|---|
-- | 处理模型 | 原生流处理（逐条） | 微批处理（默认） |
-- | 延迟 | 毫秒级 | 秒级（最低约100ms） |
-- | 状态管理 | 强大（State Backend） | 较弱 |
-- | 精确一次 | 支持 | 支持 |
-- | 事件时间/Watermark | 原生支持，成熟 | 支持 |
-- | 流批一体 | 是（同一套API） | 是（同一套DataFrame API） |
-- | SQL支持 | Flink SQL（成熟） | Spark SQL（成熟） |
-- | 生态 | 流处理生态强 | 大数据生态强（和Spark全家桶集成） |
-- | 学习曲线 | 较陡（概念多） | 较平缓（会Spark就会） |
-- | 适用场景 | 低延迟、复杂状态、实时风控 | 批量为主、流处理为辅、Spark生态用户 |

-- ============================================================
-- 例6：实时ETL管道设计
-- ============================================================
-- 典型实时ETL架构：
-- 
-- 数据源 → 消息队列 → 流处理引擎 → 存储/查询 → 应用
-- 
-- 数据源：
--   - 业务数据库（MySQL/PostgreSQL）→ CDC（Flink CDC/Debezium）
--   - 应用日志 → Filebeat/Fluentd → Kafka
--   - 用户行为（埋点）→ SDK → Kafka
--   - IoT 传感器 → MQTT → Kafka
-- 
-- 消息队列（缓冲+解耦）：
--   - Apache Kafka（最常用，高吞吐）
--   - Pulsar（云原生，多租户）
--   - RabbitMQ（低延迟，路由灵活）
-- 
-- 流处理引擎：
--   - Apache Flink（低延迟，复杂计算）
--   - Spark Structured Streaming（微批，Spark生态）
--   - Kafka Streams（轻量级，Kafka生态）
-- 
-- 存储/查询：
--   - 实时数仓：ClickHouse / Doris / StarRocks / Druid
--   - 时序数据库：InfluxDB / TimescaleDB
--   - 数据湖：Iceberg / Hudi / Delta
--   - OLTP：MySQL / PostgreSQL（实时更新）
--   - 缓存：Redis（实时查询加速）
-- 
-- 应用：
--   - 实时大屏（Grafana / Superset / 自研）
--   - 实时推荐（特征实时更新）
--   - 实时风控（毫秒级决策）
--   - 监控告警（Prometheus + AlertManager）

-- ============================================================
-- 例7：流处理的常见问题和解决方案
-- ============================================================
-- 1. 乱序数据：
--    问题：网络延迟导致事件到达顺序和发生顺序不一致
--    解决：用事件时间 + Watermark，设置允许迟到时间

-- 2. 状态过大：
--    问题：长时间运行后状态越来越大，内存不足
--    解决：设置状态 TTL（Time-To-Live），用 RocksDB State Backend

-- 3. 背压（Backpressure）：
--    问题：下游处理速度跟不上上游，数据积压
--    解决：增加并行度，优化算子，Kafka 增加分区

-- 4. 精确一次语义：
--    问题：故障恢复后可能重复计算或丢失数据
--    解决：用 Checkpoint + 两阶段提交（Sink 支持幂等或事务）

-- 5. 数据倾斜：
--    问题：某个 key 的数据量特别大，导致该并行度处理慢
--    解决：加盐（两阶段聚合）、预聚合、热点 key 拆分

-- 6. 维表关联（流批 Join）：
--    问题：流数据需要和维度表（如用户信息）关联
--    解决：广播维表（小表）、异步 IO 查询数据库、 temporal join（版本化维表）
'''

etl_compression_content = '''### 课前

- **场景**：数据量越来越大，存储成本高、查询慢，需要选择合适的文件格式和压缩算法来优化存储和查询性能。
- **目标**：掌握 Parquet、ORC、Avro 三种主流列式/行式文件格式的区别、适用场景、压缩算法选择、性能优化。
- **先修**：ETL基础、数据仓库分层、HDFS/对象存储

### 是什么

- **一句话定义**：数据压缩与序列化是将数据以高效的格式存储和传输的技术，通过列式存储（Parquet/ORC）、压缩算法（Snappy/Gzip/ZSTD）、Schema 管理（Avro）来降低存储成本、提升查询性能、支持跨语言数据交换，是大数据存储的基础。
- **行式 vs 列式**：
  - **行式存储**（CSV/JSON/Avro）：一行的数据连续存储，适合整行读取和 OLTP
  - **列式存储**（Parquet/ORC）：一列的数据连续存储，适合分析查询（只读部分列）、压缩率高

### 怎么写

```sql
-- ============================================================
-- 例1：行式存储 vs 列式存储
-- ============================================================
-- 行式存储（Row-based）：
-- 数据按行组织，一行的所有列连续存储
-- 表：user(id, name, age, city)
-- 存储：[1,Alice,25,Beijing][2,Bob,30,Shanghai][3,Carol,28,Guangzhou]...
-- 
-- 优点：整行读取快（OLTP 常用）、插入/更新方便
-- 缺点：查询只需要部分列时也要读整行、压缩率低（不同类型混在一起）

-- 列式存储（Column-based）：
-- 数据按列组织，一列的所有值连续存储
-- 存储：
--   id列: [1,2,3,...]
--   name列: [Alice,Bob,Carol,...]
--   age列: [25,30,28,...]
--   city列: [Beijing,Shanghai,Guangzhou,...]
-- 
-- 优点：
--   - 查询只需要部分列时，只读取相关列（IO少）
--   - 同一列数据类型相同，压缩率高（可以用专用压缩算法）
--   - 支持向量化执行（SIMD 指令加速）
--   - 适合 OLAP 分析查询
-- 缺点：整行写入/更新慢（需要写多个列）、不适合 OLTP

-- 分析查询场景（数仓/OLAP）：列式存储完胜
-- 事务处理场景（OLTP）：行式存储更合适

-- ============================================================
-- 例2：Parquet 列式存储格式
-- ============================================================
-- Apache Parquet：最流行的列式存储格式，Hadoop 生态标准
-- 特点：
--   - 列式存储，高效压缩
--   - 支持嵌套数据结构（Schema 演化）
--   - 语言无关（Java/Python/Go/C++ 都支持）
--   - 支持谓词下推（Min/Max 索引）
--   - 被 Spark/Flink/Hive/Impala/Trino 广泛支持
--   - 数据湖（Iceberg/Hudi/Delta）的默认格式

-- Parquet 文件结构：
--   - Row Group：行组，数据按行组分块（通常 128MB）
--   - Column Chunk：列块，每个行组内每列一个列块
--   - Page：页，列块内按页压缩（通常 1MB）
--   - Footer：文件元数据（Schema、统计信息、索引）

-- Parquet 的优化技术：
--   - 谓词下推：利用 Footer 中的 Min/Max 统计信息，跳过不满足条件的 Row Group
--   - 列裁剪：只读取查询需要的列
--   - 字典编码：低基数字符串列用字典编码，大幅压缩
--   - 游程编码（RLE）：连续相同值用计数表示
--   - 位打包（Bit Packing）：小整数用更少的位存储

-- 写入 Parquet（Python + pandas）：
-- import pandas as pd
-- df = pd.read_csv("data.csv")
-- df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")

-- 读取 Parquet：
-- df = pd.read_parquet("data.parquet", columns=["id", "name"])  # 列裁剪
-- df = pd.read_parquet("data.parquet", filters=[("age", ">", 25)])  # 谓词下推

-- Spark 写入 Parquet：
-- df.write.mode("overwrite").parquet("hdfs:///data/orders.parquet")
-- df.write.partitionBy("date").parquet("hdfs:///data/orders/")  # 分区写入

-- ============================================================
-- 例3：ORC 列式存储格式
-- ============================================================
-- Apache ORC（Optimized Row Columnar）：Hive 生态的列式格式
-- 特点：
--   - 列式存储，压缩率高
--   - 内置索引（Stripe 级、Row Group 级）
--   - 支持 ACID 事务（Hive 事务表）
--   - 对 Hive 优化最好
--   - 在 Hive/TEZ/Spark 中性能优秀
--   - 相比 Parquet：ACID 支持更好、Hive 生态更紧密

-- ORC vs Parquet：
-- | 维度 | Parquet | ORC |
-- |---|---|---|
-- | 发起方 | Twitter/Cloudera | Hortonworks |
-- | 生态 | 通用（Spark/Flink/Impala） | Hive 生态 |
-- | ACID | 不原生支持（需 Hudi/Iceberg） | 原生支持（Hive 事务） |
-- | 嵌套支持 | 好 | 一般 |
-- | 压缩率 | 高 | 高 |
-- | 查询性能 | 优秀 | 优秀（Hive 中略好） |
-- | 数据湖支持 | Iceberg/Hudi/Delta 默认 | 较少 |
-- | 适用场景 | 通用数据湖、多引擎 | Hive 数仓、需要ACID |

-- ============================================================
-- 例4：Avro 行式存储格式
-- ============================================================
-- Apache Avro：行式存储格式，强调 Schema 管理和序列化
-- 特点：
--   - 行式存储（适合整行读取和消息传输）
--   - Schema 随数据一起存储（JSON 格式 Schema）
--   - Schema 演化（字段增删改，向后/向前兼容）
--   - 二进制序列化，紧凑高效
--   - 语言无关（支持多语言）
--   - Kafka 的默认序列化格式之一
--   - 适合数据交换和消息队列

-- Avro Schema 示例（JSON）：
-- {
--   "type": "record",
--   "name": "User",
--   "fields": [
--     {"name": "id", "type": "long"},
--     {"name": "name", "type": "string"},
--     {"name": "age", "type": ["int", "null"]},  // 可空字段
--     {"name": "email", "type": ["string", "null"], "default": null}  // 新增字段带默认值
--   ]
-- }

-- Avro 的核心优势：Schema 演化
--   - 读取时用 Reader Schema，写入时用 Writer Schema
--   - 字段缺失用默认值，多余字段忽略
--   - 支持字段重命名（alias）、类型变更
--   - 非常适合消息队列（生产者和消费者 Schema 可以不同步升级）

-- Avro vs Parquet：
-- | 维度 | Avro | Parquet |
-- |---|---|---|
-- | 存储方式 | 行式 | 列式 |
-- | 适用场景 | 消息传输、数据交换、OLTP | 分析查询、OLAP、数据湖 |
-- | Schema 管理 | 强（Schema 随数据） | 有（Footer 中） |
-- | 压缩率 | 中 | 高 |
-- | 查询性能 | 整行快，分析慢 | 分析快 |
-- | 典型用途 | Kafka 消息、CDC 数据 | 数仓存储、数据湖 |

-- ============================================================
-- 例5：压缩算法对比
-- ============================================================
-- 常见压缩算法：
-- | 算法 | 压缩率 | 压缩速度 | 解压速度 | CPU 占用 | 适用场景 |
-- |---|---|---|---|---|---|
-- | Snappy | 低 | 快 | 快 | 低 | 默认选择，平衡速度和压缩率 |
-- | LZ4 | 低 | 极快 | 极快 | 低 | 追求速度，实时场景 |
-- | Gzip | 高 | 慢 | 中 | 中 | 冷数据，存储优先 |
-- | ZSTD | 中高 | 快 | 快 | 中 | 新一代，平衡好（Facebook） |
-- | Brotli | 高 | 慢 | 中 | 中 | Web 内容、冷数据 |
-- | Bzip2 | 很高 | 很慢 | 很慢 | 高 | 归档存储，极少用 |

-- 选择建议：
--   - 默认用 Snappy（Hadoop 生态标准，速度快）
--   - 追求更高压缩率用 ZSTD（越来越流行）
--   - 冷数据（很少查询）用 Gzip（节省存储）
--   - 实时场景用 LZ4（速度优先）
--   - Parquet/ORC 通常用 Snappy 或 ZSTD
--   - Avro 通常用 Snappy 或不压缩（消息传输追求速度）

-- 压缩率参考（文本数据）：
--   不压缩：100GB
--   Snappy：约 50GB（2:1）
--   Gzip：约 25GB（4:1）
--   Parquet + Snappy：约 15GB（列式+压缩，7:1）
--   Parquet + Gzip：约 8GB（12:1）

-- ============================================================
-- 例6：文件格式选择决策树
-- ============================================================
-- 1. 是分析查询（OLAP）还是事务处理（OLTP）？
--    - OLAP → 列式存储（Parquet 或 ORC）
--    - OLTP → 行式存储（数据库原生格式，不是文件）
-- 
-- 2. 是消息传输/数据交换还是持久化存储？
--    - 消息传输 → Avro（Schema 演化）或 Protobuf
--    - 持久化存储 → 继续
-- 
-- 3. 用什么查询引擎？
--    - Spark/Flink/Impala/Trino → Parquet（通用支持最好）
--    - Hive（需要 ACID）→ ORC
--    - 数据湖（Iceberg/Hudi/Delta）→ Parquet（默认）
-- 
-- 4. 压缩算法选择？
--    - 默认 → Snappy
--    - 追求压缩率 → ZSTD 或 Gzip
--    - 追求速度 → LZ4
-- 
-- 5. 分区策略？
--    - 按高基数字段（如日期）分区 → 提升查询性能
--    - 分区数不要太多（避免小文件问题）
--    - 每个分区文件大小控制在 128MB-1GB

-- ============================================================
-- 例7：性能优化最佳实践
-- ============================================================
-- 1. 文件大小：
--    - 避免大量小文件（NameNode 压力大、查询慢）
--    - 每个文件 128MB-1GB 比较合适
--    - 用 compaction 合并小文件

-- 2. 分区设计：
--    - 按查询常用的过滤字段分区（如日期、地区）
--    - 分区基数不要太高（避免分区数爆炸）
--    - 高基数字段用分桶（Bucketing）而不是分区

-- 3. 排序和聚簇：
--    - 按常用过滤/排序字段排序（提升谓词下推效果）
--    - 用 Z-Order 聚簇（多字段查询优化，Delta/Iceberg 支持）

-- 4. 列裁剪和谓词下推：
--    - 查询时只 SELECT 需要的列（避免 SELECT *）
--    - 过滤条件尽量下推到存储层
--    - 利用 Parquet/ORC 的 Min/Max 统计信息

-- 5. 压缩选择：
--    - 热数据（频繁查询）用 Snappy（解压快）
--    - 冷数据用 Gzip/ZSTD（节省存储）
--    - 不要对已经压缩的数据再压缩（如 JPG/PNG）

-- 6. Schema 设计：
--    - 用合适的数据类型（不要都用 STRING）
--    - 避免嵌套过深（影响查询性能）
--    - 考虑 Schema 演化（预留可空字段）
'''

# 读取并更新 ETL
etl_path = r"D:\cursor\数据学习平台\kg-data\embed-etl.js"
with open(etl_path, "r", encoding="utf-8") as f:
    etl_content = f.read()
match = re.search(r'window\.__KG_EMBEDDED\["etl"\]\s*=\s*(\{.*\})\s*;?\s*$', etl_content, re.DOTALL)
etl_data = json.loads(match.group(1))

# 添加到 ETL 根节点
etl_data["children"].append(make_leaf("etl-real-time-streaming", "实时流处理(Flink/Spark)", etl_streaming_content))
etl_data["children"].append(make_leaf("etl-compression-serialization", "数据压缩与序列化", etl_compression_content))
print(f"ETL 新增2篇，现有 {len(etl_data['children'])} 子节点")

# 保存 ETL
new_json_str = json.dumps(etl_data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["etl"]={new_json_str}\n'
with open(etl_path, "w", encoding="utf-8") as f:
    f.write(new_content)
print(f"embed-etl.js size: {len(new_content)} bytes")

# ============================================================
# 数据仓库部分：实时数仓 + OLAP引擎对比
# ============================================================

dwh_realtime_content = '''### 课前

- **场景**：业务需要秒级数据反馈，如实时大屏、实时监控、实时推荐、实时风控，传统T+1数仓无法满足。
- **目标**：掌握 Lambda 架构、Kappa 架构、实时数仓分层、流批一体设计、实时数仓技术选型。
- **先修**：数据仓库分层、ETL实时流处理、Kafka消息队列

### 是什么

- **一句话定义**：实时数仓是将数据仓库的分层建模思想应用于实时数据流，通过流处理引擎实现数据的实时采集、清洗、关联、聚合和服务，支持秒级甚至毫秒级的数据查询和分析，是现代数据架构的核心趋势。
- **传统数仓 vs 实时数仓**：
  - **传统数仓（T+1）**：批处理，每天凌晨跑任务，数据延迟一天，架构简单，技术成熟
  - **实时数仓**：流处理，数据秒级到达，延迟低，架构复杂，技术要求高
- **核心架构**：Lambda 架构（批流并行）、Kappa 架构（纯流）、流批一体（Flink）

### 怎么写

```sql
-- ============================================================
-- 例1：Lambda 架构（批处理 + 流处理并行）
-- ============================================================
-- Lambda 架构由 Nathan Marz 提出，核心思想：
--   用批处理层保证数据的准确性和完整性（重算全量历史）
--   用速度层处理实时数据（低延迟，但可能不精确）
--   服务层合并批处理和速度层的结果，提供统一查询

-- Lambda 架构三层：
-- 
-- 1. Batch Layer（批处理层）：
--    - 存储全量历史数据（不可变，只追加）
--    - 定期重算批处理视图（如每天重算过去所有数据）
--    - 保证数据准确性和可追溯
--    - 技术：Hadoop/Spark、HDFS、Hive
-- 
-- 2. Speed Layer（速度层）：
--    - 处理实时数据流，低延迟
--    - 只处理最近的数据（批处理层还没覆盖的部分）
--    - 结果可能不精确（等批处理层重算后修正）
--    - 技术：Flink/Spark Streaming、Kafka、Redis
-- 
-- 3. Serving Layer（服务层）：
--    - 合并批处理视图和速度层视图
--    - 提供统一的查询接口
--    - 技术：HBase、DynamoDB、ClickHouse、自定义合并逻辑

-- Lambda 架构的优缺点：
-- 优点：
--   - 兼顾准确性（批处理）和低延迟（流处理）
--   - 容错性好（批处理可以重算修正错误）
--   - 技术成熟，风险低
-- 缺点：
--   - 维护两套代码（批处理和流处理逻辑重复）
--   - 架构复杂，运维成本高
--   - 数据合并逻辑复杂
--   - 批处理和流处理结果可能不一致

-- ============================================================
-- 例2：Kappa 架构（纯流处理）
-- ============================================================
-- Kappa 架构由 Jay Kreps（Kafka 作者）提出，核心思想：
--   用流处理统一处理所有数据，不需要批处理层
--   历史数据通过重放（replay）Kafka 中的数据来重新计算
--   简化架构，只维护一套代码

-- Kappa 架构：
-- 
-- 数据源 → Kafka（消息队列，保留全量历史）→ Flink（流处理）→ 实时数仓 → 查询服务
-- 
-- 关键：Kafka 保留全量历史数据（可以设置长期保留）
--   - 需要重算时：启动一个新的 Flink 作业，从 Kafka 最早的 offset 开始消费
--   - 重放数据，重新计算，结果写入新表
--   - 计算完成后，切换查询到新表

-- Kappa 架构的优缺点：
-- 优点：
--   - 架构简单，只维护一套流处理代码
--   - 没有批流合并的复杂性
--   - 实时性好
-- 缺点：
--   - 依赖 Kafka 长期保留数据（存储成本）
--   - 重放全量历史数据耗时长（数据量大时）
--   - 流处理引擎需要支持高吞吐的历史数据重放
--   - 某些复杂的批处理操作（如全量排序、全局去重）流处理实现困难

-- ============================================================
-- 例3：流批一体（Flink 为代表）
-- ============================================================
-- 流批一体是最新的架构趋势，核心思想：
--   用同一套引擎和API同时处理批和流
--   批处理是流处理的特例（有界流）
--   只写一套代码，根据数据是有界还是无界自动选择执行模式

-- 流批一体的代表：
--   - Apache Flink：原生流批一体，DataStream API 和 Table API/SQL 都支持批流
--   - Spark：从 2.0 开始支持结构化流，批流统一 DataFrame API
--   - 数据湖格式（Iceberg/Hudi/Delta）：支持流式写入和批量读取

-- 流批一体数仓分层：
-- 
-- ODS（贴源层）：
--   - 实时：Kafka Topic（原始数据流）
--   - 批量：HDFS/Iceberg（原始数据归档）
--   - 流批一体：Kafka + Iceberg（实时写入Iceberg，同时支持流读和批读）
-- 
-- DWD（明细层）：
--   - 实时：Flink 清洗后的 Kafka Topic / Iceberg 明细表
--   - 批量：Hive/Iceberg 明细表
--   - 流批一体：Flink SQL 清洗，写入 Iceberg（支持实时查询）
-- 
-- DWS（汇总层）：
--   - 实时：Flink 窗口聚合结果写入 ClickHouse/Doris
--   - 批量：Hive/Iceberg 汇总表
--   - 流批一体：Flink 聚合写入数据湖 + OLAP 引擎（实时+历史统一查询）
-- 
-- ADS（应用层）：
--   - 实时：实时大屏、实时推荐、风控
--   - 批量：T+1 报表、BI 分析
--   - 流批一体：统一查询接口（实时+历史）

-- ============================================================
-- 例4：实时数仓技术选型
-- ============================================================
-- 数据采集：
--   - 数据库 CDC：Flink CDC / Debezium / Canal
--   - 日志采集：Filebeat / Fluentd / Logstash
--   - 埋点采集：SDK → Kafka
-- 
-- 消息队列：
--   - Apache Kafka：最常用，高吞吐，生态成熟
--   - Apache Pulsar：云原生，多租户，分层存储
--   - RabbitMQ：低延迟，路由灵活（适合业务消息，不适合大数据）
-- 
-- 流处理引擎：
--   - Apache Flink：低延迟，复杂计算，流批一体（首选）
--   - Spark Structured Streaming：微批，Spark 生态
--   - Kafka Streams：轻量级，Kafka 生态（简单ETL）
-- 
-- 实时存储/OLAP：
--   - ClickHouse：查询极快，适合实时大屏和分析
--   - Apache Doris / StarRocks：实时更新+分析，MPP架构
--   - Apache Druid：时序数据，实时聚合
--   - Redis：缓存，实时查询加速
--   - Apache HBase：随机读写，宽表
-- 
-- 数据湖（流批一体存储）：
--   - Apache Iceberg：Schema 演化好，引擎支持广
--   - Apache Hudi：Upsert/删除强，流式写入好
--   - Delta Lake：ACID 强，Databricks 生态
-- 
-- 查询服务：
--   - Presto/Trino：联邦查询，多数据源
--   - ClickHouse/Doris：直接查询
--   - 自研 API 服务

-- ============================================================
-- 例5：实时数仓的关键挑战
-- ============================================================
-- 1. 数据一致性：
--    问题：实时数据可能重复、乱序、丢失
--    解决：精确一次语义（Exactly-Once）、幂等写入、Watermark 处理乱序

-- 2. 维表关联：
--    问题：流数据需要和维度表关联，维表可能变化
--    解决：广播维表（小表）、异步 IO 查询、 temporal join（版本化维表）、维表变化流

-- 3. 大状态管理：
--    问题：长时间运行后状态越来越大
--    解决：状态 TTL、RocksDB State Backend、状态压缩

-- 4. 数据回溯/重算：
--    问题：发现逻辑错误后需要重算历史数据
--    解决：Kafka 保留历史数据重放、数据湖支持时间旅行（Time Travel）

-- 5. 实时和离线一致性：
--    问题：实时指标和离线指标对不上
--    解决：统一指标定义、流批一体计算、定期对账校准

-- 6. 小文件问题：
--    问题：流式写入数据湖产生大量小文件
--    解决：定期 compaction、调整 checkpoint 间隔、写入缓冲

-- 7. 成本控制：
--    问题：实时计算资源成本高（7x24运行）
--    解决：合理设置并行度、弹性扩缩容、冷热分离（热数据实时，冷数据离线）
'''

dwh_olap_content = '''### 课前

- **场景**：需要选择合适的 OLAP 引擎支撑实时/离线分析查询，不同引擎适用场景不同，需要了解主流引擎的特点和选型。
- **目标**：掌握 ClickHouse、Doris/StarRocks、Druid、Presto/Trino 等主流 OLAP 引擎的原理、特点、适用场景和选型建议。
- **先修**：数据仓库基础、列式存储、分布式计算

### 是什么

- **一句话定义**：OLAP（Online Analytical Processing）引擎是专门为分析查询优化的数据库系统，通过列式存储、分布式计算、预聚合、向量化执行等技术，支持对海量数据的快速多维分析和聚合查询，是数据仓库和 BI 系统的核心查询引擎。
- **OLAP vs OLTP**：
  - **OLTP**：面向事务，短查询，高并发，强调一致性（MySQL/PostgreSQL）
  - **OLAP**：面向分析，复杂查询，大扫描，强调查询性能（ClickHouse/Doris）

### 怎么写

```sql
-- ============================================================
-- 例1：OLAP 引擎核心技术
-- ============================================================
-- 列式存储：
--   按列存储数据，查询只读取需要的列，压缩率高
--   几乎所有 OLAP 引擎都用列式存储

-- 分布式计算（MPP）：
--   Massively Parallel Processing，数据分片存储在多个节点
--   查询时多个节点并行计算，最后汇总结果
--   代表：ClickHouse、Doris、StarRocks、Greenplum

-- 预聚合（物化视图）：
--   预先计算好常用维度的聚合结果，查询时直接读取
--   用空间换时间，大幅提升查询性能
--   代表：Druid（Rollup）、Doris（物化视图）、Kylin（Cube）

-- 向量化执行：
--   一次处理一批数据（向量），而不是一行一行
--   利用 CPU SIMD 指令加速，减少函数调用开销
--   代表：ClickHouse、Doris、StarRocks

-- 索引技术：
--   稀疏索引（Min/Max）、Bloom Filter、位图索引、倒排索引
--   快速定位数据，减少扫描量

-- 数据压缩：
--   列式存储 + 专用压缩算法（字典编码、RLE、位打包）
--   压缩率可达 5:1 到 20:1

-- ============================================================
-- 例2：ClickHouse —— 查询最快的 OLAP 引擎
-- ============================================================
-- ClickHouse 由俄罗斯 Yandex 公司开发，以查询速度极快著称
-- 
-- 核心特点：
--   - 列式存储，向量化执行（查询极快）
--   - MPP 架构，线性扩展
--   - 支持实时写入和查询（秒级延迟）
--   - SQL 支持完善（大部分标准 SQL）
--   - 丰富的表引擎（MergeTree 系列、Replicated、Distributed）
--   - 高压缩率（10:1 以上）
--   - 开源，社区活跃
-- 
-- 优势：
--   - 查询速度极快（单表查询秒杀级）
--   - 写入吞吐高（每秒百万行）
--   - 资源利用率高
--   - 部署简单（不依赖 Hadoop 生态）
-- 
-- 劣势：
--   - 不支持事务（OLAP 不需要）
--   - 不支持高频更新/删除（批量更新可以，单行更新慢）
--   - 多表关联性能一般（不如 Doris）
--   - 不支持标准的 UPDATE/DELETE（用 ALTER TABLE 异步删除）
--   - 高并发查询能力一般（适合几十到几百并发）
-- 
-- 适用场景：
--   - 实时大屏、实时分析
--   - 日志分析、用户行为分析
--   - 时序数据分析
--   - 单表大查询（宽表模型）
--   - 中小规模团队（部署简单）
-- 
-- 不适用：
--   - 需要事务的 OLTP 场景
--   - 高频单行更新
--   - 复杂多表关联（星型模型）
--   - 高并发点查

-- ClickHouse 表引擎（MergeTree 系列）：
--   - MergeTree：基础引擎，支持分区、排序、副本
--   - ReplacingMergeTree：去重（相同排序键保留最新）
--   - SummingMergeTree：预聚合（相同排序键求和）
--   - AggregatingMergeTree：预聚合（聚合函数）
--   - Replicated*：支持副本（高可用）
--   - Distributed：分布式表（路由到各节点）

-- ============================================================
-- 例3：Apache Doris / StarRocks —— 实时更新+分析的 MPP 引擎
-- ============================================================
-- Apache Doris（原百度 Palo）：国产 MPP OLAP 引擎，支持实时更新
-- StarRocks（原 DorisDB）：Doris 的商业分支，性能更强，国际化更好
-- 两者架构相似，都是 MPP + 列式存储 + 实时更新

-- 核心特点：
--   - MPP 架构，分布式查询
--   - 列式存储，向量化执行
--   - 支持实时更新（Unique Key 模型，秒级更新）
--   - 支持多表关联（CBO 优化器，星型模型性能好）
--   - 支持物化视图（自动预聚合）
--   - 支持 MySQL 协议（用 MySQL 客户端直接连接）
--   - 兼容 MySQL 语法（学习成本低）
--   - 支持弹性扩缩容
-- 
-- 优势：
--   - 实时更新能力强（比 ClickHouse 好）
--   - 多表关联性能好（CBO 优化器）
--   - 兼容 MySQL 协议和语法（易用）
--   - 支持物化视图（自动加速）
--   - 国产，中文文档好，社区活跃
-- 
-- 劣势：
--   - 单表查询速度略逊于 ClickHouse
--   - 生态不如 ClickHouse 成熟
--   - StarRocks 部分高级功能需要企业版
-- 
-- 适用场景：
--   - 实时数仓（需要实时更新）
--   - 多维分析（星型模型，多表关联）
--   - 用户画像（标签实时更新）
--   - 统一分析平台（替代 MySQL + ES + Redis）
--   - 对 MySQL 兼容性要求高的团队

-- Doris 数据模型：
--   - Duplicate Key：明细模型（保留所有数据，不聚合）
--   - Aggregate Key：聚合模型（相同 Key 预聚合）
--   - Unique Key：唯一主键模型（相同 Key 更新，支持实时更新）

-- ============================================================
-- 例4：Apache Druid —— 时序实时 OLAP 引擎
-- ============================================================
-- Apache Druid（原 Metamarkets Druid）：专为时序数据设计的 OLAP 引擎
-- 
-- 核心特点：
--   - 时序数据优化（时间分区、时间索引）
--   - 实时摄入（支持流处理，秒级可见）
--   - 预聚合（Rollup，摄入时聚合）
--   - 列式存储 + 位图索引
--   - 分布式架构（Broker/Historical/Coordinator/Overlord/MiddleManager）
--   - 支持 Lambda 架构（实时+批处理）
-- 
-- 优势：
--   - 时序数据查询极快
--   - 实时摄入性能好
--   - 预聚合大幅提升查询性能
--   - 高并发查询支持好
--   - 适合时间序列分析
-- 
-- 劣势：
--   - 架构复杂（组件多，运维成本高）
--   - 不支持标准 SQL（Druid SQL 有限）
--   - 不支持 Join（需要预关联）
--   - 不支持更新（只能追加，重写 Segment）
--   - 学习曲线陡
-- 
-- 适用场景：
--   - 时序数据实时分析（监控指标、IoT）
--   - 实时大屏（时间序列）
--   - 网络流量分析
--   - 广告投放分析
--   - 已经用 Lambda 架构的团队

-- ============================================================
-- 例5：Presto / Trino —— 联邦查询引擎
-- ============================================================
-- Presto（现 Trino）：Facebook 开发的分布式 SQL 查询引擎
-- 注意：PrestoDB（Linux 基金会）和 Trino（原 Presto 核心团队 fork）是两个分支
-- 
-- 核心特点：
--   - 联邦查询（一个 SQL 查询多个数据源：Hive/MySQL/PostgreSQL/Kafka/...）
--   - MPP 架构，内存计算
--   - 标准 SQL 支持（ANSI SQL）
--   - 不存储数据（纯查询引擎，数据在外部存储）
--   - 可插拔 Connector（支持多种数据源）
--   - 支持多租户、资源组
-- 
-- 优势：
--   - 联邦查询（统一查询多个数据源，不需要数据搬迁）
--   - 标准 SQL 兼容好
--   - 查询性能好（内存计算，MPP）
--   - 生态丰富（Connector 多）
--   - 适合数据湖查询（Iceberg/Hudi/Delta/Hive）
-- 
-- 劣势：
--   - 不存储数据（需要外部存储）
--   - 实时写入支持弱（主要是查询引擎）
--   - 小查询延迟不如专门的 OLAP 引擎
--   - 内存消耗大（大查询可能 OOM）
-- 
-- 适用场景：
--   - 数据湖查询（Iceberg/Hudi/Delta on HDFS/S3）
--   - 联邦查询（跨数据源关联）
--   - 即席查询（Ad-hoc）
--   - 统一查询入口（多数据源）
--   - 数据科学团队（Python/Jupyter 集成）

-- ============================================================
-- 例6：Apache Kylin —— 预聚合 Cube 引擎
-- ============================================================
-- Apache Kylin（eBay 开发）：通过预计算 Cube 实现亚秒级查询
-- 
-- 核心特点：
--   - 预计算 Cube（所有维度组合的聚合结果）
--   - 查询时直接读取预计算结果（亚秒级）
--   - 支持超大数据集（PB 级）
--   - 标准 SQL 支持
--   - 与 Hadoop 生态集成（Hive/HBase）
-- 
-- 优势：
--   - 查询极快（预计算，亚秒级）
--   - 支持超大数据集
--   - 高并发支持好
-- 
-- 劣势：
--   - 维度爆炸（维度多时 Cube 体积指数增长）
--   - 预计算耗时长（构建 Cube 慢）
--   - 不支持实时（T+1 预计算）
--   - 灵活性差（只能查询预定义维度）
--   - 运维复杂
-- 
-- 适用场景：
--   - 固定维度的报表（维度少，查询模式固定）
--   - 超大数据集（PB 级）
--   - 高并发固定查询
--   - 对查询延迟要求极高（亚秒级）

-- ============================================================
-- 例7：OLAP 引擎选型对比
-- ============================================================
-- | 维度 | ClickHouse | Doris/StarRocks | Druid | Trino | Kylin |
-- |---|---|---|---|---|---|
-- | 架构 | MPP | MPP | 专用组件 | MPP | 预计算 |
-- | 存储 | 本地列存 | 本地列存 | 本地列存 | 外部存储 | HBase |
-- | 实时写入 | 好 | 很好 | 很好 | 弱 | 不支持 |
-- | 实时更新 | 一般 | 很好 | 不支持 | 不支持 | 不支持 |
-- | 查询速度 | 极快 | 快 | 快 | 较快 | 极快 |
-- | 多表关联 | 一般 | 很好 | 不支持 | 很好 | 一般 |
-- | SQL 兼容 | 较好 | 很好(MySQL) | 一般 | 很好(ANSI) | 较好 |
-- | 高并发 | 一般 | 好 | 很好 | 一般 | 很好 |
-- | 运维难度 | 简单 | 中等 | 复杂 | 中等 | 复杂 |
-- | 生态 | 丰富 | 成长中 | 成熟 | 丰富 | 成熟 |
-- | 适用场景 | 单表实时分析 | 实时数仓 | 时序实时 | 数据湖/联邦 | 固定报表 |

-- 选型决策树：
-- 1. 需要实时更新吗？
--    - 是 → Doris/StarRocks（首选）或 ClickHouse（更新不频繁）
--    - 否 → 继续
-- 
-- 2. 是时序数据吗？
--    - 是 → Druid（时序专用）或 ClickHouse
--    - 否 → 继续
-- 
-- 3. 需要多表关联吗？
--    - 是 → Doris/StarRocks（CBO 好）或 Trino（联邦）
--    - 否（单表宽表）→ ClickHouse（最快）
-- 
-- 4. 是数据湖查询吗？
--    - 是 → Trino（数据湖查询首选）
--    - 否 → 继续
-- 
-- 5. 查询模式固定吗？维度少吗？
--    - 是 → Kylin（预计算，亚秒级）
--    - 否 → ClickHouse 或 Doris

-- 常见组合：
--   - 实时数仓：Flink + Doris/StarRocks（实时写入+多维分析）
--   - 实时大屏：Flink + ClickHouse（单表查询极快）
--   - 数据湖：Iceberg/Hudi + Trino（存储计算分离）
--   - 用户画像：Doris/StarRocks（标签实时更新+多维圈人）
--   - 监控时序：Prometheus + Druid/ClickHouse
--   - 统一分析平台：Doris/StarRocks（替代 MySQL+ES+Redis）
'''

# 读取并更新数据仓库
dwh_path = r"D:\cursor\数据学习平台\kg-data\embed-dwh.js"
with open(dwh_path, "r", encoding="utf-8") as f:
    dwh_content_file = f.read()
match = re.search(r'window\.__KG_EMBEDDED\["dwh"\]\s*=\s*(\{.*\})\s*;?\s*$', dwh_content_file, re.DOTALL)
dwh_data = json.loads(match.group(1))

# 添加到数据仓库根节点
dwh_data["children"].append(make_leaf("dwh-real-time-warehouse", "实时数仓(Lambda/Kappa)", dwh_realtime_content))
dwh_data["children"].append(make_leaf("dwh-olap-engines", "OLAP引擎对比与选型", dwh_olap_content))
print(f"数据仓库新增2篇，现有 {len(dwh_data['children'])} 子节点")

# 保存数据仓库
new_json_str = json.dumps(dwh_data, ensure_ascii=False, separators=(',', ':'))
new_content = f'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {{}};\nwindow.__KG_EMBEDDED["dwh"]={new_json_str}\n'
with open(dwh_path, "w", encoding="utf-8") as f:
    f.write(new_content)
print(f"embed-dwh.js size: {len(new_content)} bytes")

print("\nDone! 实时处理与数仓内容补充完成！新增4篇：")
print("  ETL:")
print("    1. 实时流处理(Flink/Spark)")
print("    2. 数据压缩与序列化")
print("  数据仓库:")
print("    3. 实时数仓(Lambda/Kappa)")
print("    4. OLAP引擎对比与选型")
