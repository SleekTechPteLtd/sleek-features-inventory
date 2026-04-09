# Process reconciliation queries from Kafka

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process reconciliation queries from Kafka |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ingest ML reconciliation work from a shared event stream and run matching asynchronously so upstream services can publish requests without waiting for ML processing. |
| **Entry Point / Surface** | System — ML Autorecon API process on startup (FastAPI lifespan); not a user-facing screen. |
| **Short Description** | On startup, the API subscribes to the configured reconciliation-queries Kafka topic, parses JSON payloads, and enqueues each message to Celery (`celery_autorecon`) for background execution. Shutdown cancels the consumer task. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Upstream: publishers to reconciliation queries topic (default `MLReconciliationEvent` via `RECONCILIATION_QUERIES_TOPIC`). Kafka cluster (Confluent Cloud config). Celery broker/backend (Redis). Downstream: Celery task runs `match_transaction` and may publish results to the reconciliation results topic (see `celery_worker`). |
| **Service / Repository** | ml-autorecon-service |
| **DB - Collections** | None in the Kafka→Celery ingress path in the listed files; downstream matching may use MongoDB elsewhere in the service (e.g. FX cache in `sleek_ml.exchange_rates` during `match_transaction`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`app/main.py`**: `startup_event` builds `KafkaWrapper` with `celery_task=celery_autorecon`, `consumer=reconcilitation_queries_topic`, and the event loop; awaits `initialize_consumer()` and `consume()`. `shutdown_event` cancels `autorecon_kafka.consumer_task`.
- **`app/settings.py`** (referenced): `reconcilitation_queries_topic = os.getenv("RECONCILIATION_QUERIES_TOPIC", "MLReconciliationEvent")`.
- **`app/kafka_utils.py`**: `KafkaWrapper` wires `AIOKafkaConsumer` to `consumer_topic`, SASL/SSL from `read_ccloud_config()`. `consume()` starts `send_consumer_message` as an asyncio task. `send_consumer_message` loops `async for msg in self.consumer`, `json.loads(msg.value)`, then `self.celery_task.delay(msg)`.
- **`app/celery_worker.py`**: `@celery_worker.task` `celery_autorecon(details)` calls `match_transaction(details)` and publishes results via a process-local `KafkaWrapper` producer (results topic) — separate from the API consumer but part of the async pipeline. `worker_process_init` initializes the results Kafka producer post-fork for Celery workers.
