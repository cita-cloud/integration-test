# 创建数据库
CREATE DATABASE citacloud;
# 使用数据库
USE citacloud;
# 创建各种表
CREATE TABLE IF NOT EXISTS citacloud.blocks(
    height BIGINT,
    block_hash VARCHAR(64),
    prev_hash VARCHAR(64),
    proof VARCHAR,
    proposer VARCHAR(40),
    state_root VARCHAR(64),
    timestamp BIGINT,
    transaction_root VARCHAR(64),
    tx_count INT,
    version INT)
DISTRIBUTED BY HASH(`height`) BUCKETS 1
PROPERTIES (
    "replication_allocation" = "tag.location.default: 1"
);

CREATE TABLE IF NOT EXISTS citacloud.txs
(
  `height` BIGINT,
  `index` INT,
  `tx_hash` VARCHAR(64),
  `data` VARCHAR,
  `nonce` VARCHAR(128),
  `quota` BIGINT,
  `to` VARCHAR(40),
  `valid_until_block` BIGINT,
  `value` VARCHAR(64),
  `version` INT,
  -- witness begin
  `sender` VARCHAR(40),
  `signature` VARCHAR(256),
  -- witness end
  INDEX idx_height(height) USING INVERTED,
  INDEX idx_tx_hash(tx_hash) USING INVERTED
)
DISTRIBUTED BY HASH(`tx_hash`) BUCKETS 1
PROPERTIES (
    "replication_allocation" = "tag.location.default: 1"
);

CREATE TABLE IF NOT EXISTS citacloud.utxos
(
  `height` BIGINT,
  `index` INT,
  `tx_hash` VARCHAR(64),
  `lock_id` INT,
  `output` VARCHAR,
  `pre_tx_hash` VARCHAR(66),
  `version` INT,
  -- witness begin
  `sender` VARCHAR(40),
  `signature` VARCHAR(256),
  -- witness end
  INDEX idx_height(height) USING INVERTED,
  INDEX idx_tx_hash(tx_hash) USING INVERTED
)
DISTRIBUTED BY HASH(`tx_hash`) BUCKETS 1
PROPERTIES (
    "replication_allocation" = "tag.location.default: 1"
);

CREATE TABLE IF NOT EXISTS citacloud.receipts
(
  `height` BIGINT,
  `index` INT,
  `contract_addr` VARCHAR(40),
  `cumulative_quota_used` VARCHAR(64),
  `quota_used` VARCHAR(64),
  `error_msg` VARCHAR,
  `logs_bloom` VARCHAR(512),
  `tx_hash` VARCHAR(64),
  INDEX idx_height(height) USING INVERTED,
  INDEX idx_tx_hash(tx_hash) USING INVERTED
)
DISTRIBUTED BY HASH(`tx_hash`) BUCKETS 1
PROPERTIES (
    "replication_allocation" = "tag.location.default: 1"
);

CREATE TABLE IF NOT EXISTS citacloud.logs
(
  `address` VARCHAR(40),
  -- at most 4 topic: 256 + 32
  `topics` VARCHAR(288),
  `data` VARCHAR,
  `height` BIGINT,
  `log_index` INT,
  `tx_log_index` INT,
  `tx_hash` VARCHAR(64),
)
DISTRIBUTED BY HASH(`tx_hash`) BUCKETS 1
PROPERTIES (
    "replication_allocation" = "tag.location.default: 1"
);

CREATE TABLE IF NOT EXISTS citacloud.systemconfig
(
  `height` BIGINT,
  `admin` VARCHAR(40),
  `block_interval` INT,
  `block_limit` INT,
  `chain_id` VARCHAR(64),
  `emergency_brake` BOOLEAN,
  `quota_limit` BIGINT,
  `validators` VARCHAR,
  `version` INT,
  INDEX idx_height(height) USING INVERTED
)
DISTRIBUTED BY HASH(`height`) BUCKETS 1
PROPERTIES (
    "replication_allocation" = "tag.location.default: 1"
);

# 创建导出任务
CREATE ROUTINE LOAD citacloud.example_routine_load_blocks_json ON blocks
PROPERTIES
(
    "desired_concurrent_number"="1",
    "format" = "json",
    "strict_mode" = "false"
)
FROM KAFKA(
    "kafka_broker_list" = "my-cluster-kafka-bootstrap:9092",
    "kafka_topic" = "cita-cloud.xxxxxx.blocks",
    "kafka_partitions" = "0",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);

CREATE ROUTINE LOAD citacloud.example_routine_load_txs_json ON txs
PROPERTIES
(
    "desired_concurrent_number"="1",
    "format" = "json",
    "strict_mode" = "false"
)
FROM KAFKA(
    "kafka_broker_list" = "my-cluster-kafka-bootstrap:9092",
    "kafka_topic" = "cita-cloud.xxxxxx.txs",
    "kafka_partitions" = "0",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);

CREATE ROUTINE LOAD citacloud.example_routine_load_utxos_json ON utxos
PROPERTIES
(
    "desired_concurrent_number"="1",
    "format" = "json",
    "strict_mode" = "false"
)
FROM KAFKA(
    "kafka_broker_list" = "my-cluster-kafka-bootstrap:9092",
    "kafka_topic" = "cita-cloud.xxxxxx.utxos",
    "kafka_partitions" = "0",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);

CREATE ROUTINE LOAD citacloud.example_routine_load_receipts_json ON receipts
PROPERTIES
(
    "desired_concurrent_number"="1",
    "format" = "json",
    "strict_mode" = "false"
)
FROM KAFKA(
    "kafka_broker_list" = "my-cluster-kafka-bootstrap:9092",
    "kafka_topic" = "cita-cloud.xxxxxx.receipts",
    "kafka_partitions" = "0",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);

CREATE ROUTINE LOAD citacloud.example_routine_load_logs_json ON logs
PROPERTIES
(
    "desired_concurrent_number"="1",
    "format" = "json",
    "strict_mode" = "false"
)
FROM KAFKA(
    "kafka_broker_list" = "my-cluster-kafka-bootstrap:9092",
    "kafka_topic" = "cita-cloud.xxxxxx.logs",
    "kafka_partitions" = "0",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);

CREATE ROUTINE LOAD citacloud.example_routine_load_systemconfig_json ON systemconfig
PROPERTIES
(
    "desired_concurrent_number"="1",
    "format" = "json",
    "strict_mode" = "false"
)
FROM KAFKA(
    "kafka_broker_list" = "my-cluster-kafka-bootstrap:9092",
    "kafka_topic" = "cita-cloud.xxxxxx.system-config",
    "kafka_partitions" = "0",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);