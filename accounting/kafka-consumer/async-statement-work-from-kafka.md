# Process statement work from Kafka

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process statement work from Kafka |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Bank statement extraction and statement-info requests that arrive as Kafka events are processed without blocking producers; structured results and status codes are published to Kafka so bookkeeping and downstream accounting systems can continue workflows asynchronously. |
| **Entry Point / Surface** | Event-driven: when `KAFKA_ENABLE` is `true`, the API process starts an `aiokafka` consumer on `KAFKA_CONSUME_TOPIC` at FastAPI startup; messages are handed to Celery (`celery_extract`). For manual testing, `POST /api/call_consumer` (API key) simulates a message and runs extraction via a background task. Not an end-user screen. |
| **Short Description** | The consumer reads JSON payloads from the configured Kafka topic, commits offsets after enqueueing each message to the Celery task `celery_extract` on Redis. Workers then perform statement extraction or `statement_info` handling (see worker routing) and publish outcomes to `KAFKA_PUBLISH_TOPIC`. A separate in-process path `extract_transactions_kafka` can publish extraction results directly from the API process when driven by the test hook. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Kafka**: `KAFKA_BROKER_URL`, SASL/SSL, `KAFKA_CONSUME_TOPIC`, `KAFKA_CONSUMER_GROUP_ID`, `KAFKA_CLIENT_ID`, `KAFKA_PUBLISH_TOPIC`. **Celery/Redis**: same queue as `accounting/celery-extract/process-bank-statement-extraction-jobs.md` (`celery_extract`, broker `REDIS_HOST`, `REDIS_PREFIX`). Downstream accounting consumers of the publish topic; upstream services that produce to the consume topic. |
| **Service / Repository** | sleek-statement-extraction-service |
| **DB - Collections** | MongoDB (Bunnet `BankConfig` and shared DB init): not read in `kafka_consumer.py`; worker and `extract_transactions_kafka` paths resolve templates and files via `app.common` and may touch configured collections—see Celery feature doc for worker-side detail. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `extract_transactions_kafka` (template-from-ID path) is used in production beyond `/api/call_consumer`; alignment of message schema between upstream producers and `celery_extract` expectations (`data.statement_id`, `data.type`, `correlationId`, etc.). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`app/kafka/kafka_consumer.py`**: `KafkaConsumer` builds `AIOKafkaConsumer` with `KAFKA_BROKER_URL`, SASL, SSL (`certifi`), `group_id`, `enable_auto_commit=False`, `auto_offset_reset`; `send_consumer_message` parses JSON, calls `self.celery_task.delay(msg)`, then commits. `consume()` starts `send_consumer_message` as an asyncio task; `configure_consumer` starts the consumer.
- **`app/main.py`**: On startup, if `KAFKA_ENABLE` is `true`, initializes `KafkaConsumer(loop, celery_task=celery_extract, topic=KAFKA_CONSUME_TOPIC)`, `configure_consumer()`, `consume()`. Shutdown cancels `extraction_kafka.consumer_task`. `consumer_messages` → `extract_transactions_kafka(statement_id)` (async extraction + `KafkaProducer` to publish topic—used from `call_consumer_api`, not from `KafkaConsumer`). `extract_transactions_kafka` uses `get_matched_template_from_id`, `extractor_module`, `KafkaProducer.produce_message` with status/result or error payloads.
- **`app/worker.py`**: `@celery_worker.task` `celery_extract(details)` routes by `PLATFORM`, `bank_name`, and `data.type` (`statement_info` vs default) into `statement_info` or `statement_extraction`; results published via `KafkaProducer` / `process_extraction_result` (`KAFKA_PUBLISH_TOPIC`).
- **`app/kafka/kafka_producer.py`**: Confluent `Producer.produce_message(key, value)` JSON to publish topic (shared by API and worker paths).
