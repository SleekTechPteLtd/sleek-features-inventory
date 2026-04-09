# Extract bank statement transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Extract bank statement transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (integrated services and jobs that call the API or publish Kafka messages); finance workflows consume structured results downstream |
| **Business Outcome** | Bank statement PDFs become structured transaction lines (and optional categorization) so accounting and reconciliation can proceed without manual re-keying. |
| **Entry Point / Surface** | Backend integration: FastAPI service with `Authorization` API key (`SLEEK_SERVICE_CLIENT_SECRET`); optional Kafka ingest when `KAFKA_ENABLE=true` (`KAFKA_CONSUME_TOPIC` → Celery → `KAFKA_PUBLISH_TOPIC`). Not a Sleek App navigation path in this repo. |
| **Short Description** | Callers upload a PDF with a `statement_id` and template or bank name, or send async work via Kafka/Celery using `statement_id` to fetch the file. The service matches JSON-driven templates or fixed routes (OpenAI, Claude, HSBC Claude, compact Claude), runs the matching `app.extractors.*` class via `extractor_module`, and returns JSON or publishes status and payload to Kafka. Celery path can enrich transactions with `get_categorized_transactions` before producing results. |
| **Variants / Markets** | SG, HK (`PLATFORM` env selects HSBC handling in `get_matched_template`: HK uses `hsbc_claude_statement`, non-HK HSBC uses `compact_claude_statement` with `HSBC_SG`); Celery uses `PLATFORM == 'hk'` to force OpenAI-style handling. Other markets: Unknown. |
| **Dependencies / Related Flows** | **Upstream:** PDF by multipart upload or `download_and_save_to_tempfile(statement_id)` (remote retrieval). **Async:** Redis + Celery (`celery_extract`), `aiokafka` consumer delegating to Celery. **Downstream:** Kafka producer with `statement_id`, `correlationId`, `status`, `result` / error messages; `get_categorized_transactions` for post-extraction tagging. **Related:** `/api/extract_statement_info` and Celery `statement_info` for metadata-only flows. **Config:** MongoDB `BankConfig` CRUD under `/prompt/database/*` for prompt/bank configuration (separate from per-request extraction routing). |
| **Service / Repository** | sleek-statement-extraction-service |
| **DB - Collections** | MongoDB: `BankConfig` document model; physical collection name from environment variable `COLLECTION_NAME` (see `app/db/db_bunnet.py`). Template JSON files used by `load_template` / `find_matching_template` in `app/helpers.py` (not a Mongo collection). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact upstream service that resolves `statement_id` to PDF bytes is outside these files (`download_and_save_to_tempfile`). Whether all deployments enable Kafka vs synchronous HTTP only is environment-dependent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **API surface & auth** — `app/main.py`: `APIKeyHeader` `Authorization`; `get_api_key` compares to `SLEEK_SERVICE_CLIENT_SECRET`. Health `GET /api/health`. Extraction routes: `POST /api/extract_transactions` (multipart: file, `statement_id`, optional `template_name`) → `get_matched_template_from_file` + `extractor_module`; `POST /api/open_ai/extract_transactions` (`open_ai_statement`); `POST /api/claude_hsbc_1/extract_transactions` (`hsbc_claude_statement`); `POST /api/claude/extract_transactions` (`claude_statement`); `POST /api/compact_claude/extract_transactions` (`compact_claude_statement`); `POST /api/extract_transactions_claude` (`get_matched_template(bank_name)` then `extractor_module`). `POST /api/extract_statement_info` uses `get_statement_info_from_file`. `POST /api/call_consumer` schedules `consumer_messages` → `extract_transactions_kafka(statement_id)` for testing async path.
- **Kafka sync extraction** — `app/main.py`: `extract_transactions_kafka` uses `get_matched_template_from_id(statement_id, template_name)`, `extractor_module`, `KafkaProducer.produce_message` with status 200/400/404/500. `startup_event`: if `KAFKA_ENABLE` true, `KafkaConsumer` with `celery_task=celery_extract` and `KAFKA_CONSUME_TOPIC`; `shutdown_event` cancels consumer task.
- **Dynamic extractors** — `app/common.py`: `extractor_module` imports `app.extractors.{module}`, instantiates `{PascalCase}Extractor` with `filepath`, `matched_template`, `bank_name`, calls `.extract()`. Helpers: `get_matched_template_from_file`, `get_file`, `get_matched_template_from_id` (download by id + `find_matching_template`), `get_matched_template(bank_name)` branching HSBC / `MAJOR_BANKS_DONE` / `MINOR_BANKS_DONE` / default compact Claude.
- **Celery worker** — `app/worker.py`: `celery_extract` task; `statement_extraction` downloads PDF, `get_template` → `get_matched_template`, `perform_extraction` → `extractor_module`, optional `get_categorized_transactions`, `process_extraction_result` → Kafka producer; `statement_info` for `type == "statement_info"` using `get_statement_info_from_remote_path`. Platform/bank toggles OpenAI path for HK. Redis broker/backend with `REDIS_PREFIX` on transport options.
- **Kafka I/O** — `app/kafka/kafka_consumer.py`: `AIOKafkaConsumer`, SASL/SSL from env, `celery_task.delay(msg)` per message, manual commit. `app/kafka/kafka_producer.py`: Confluent `Producer`, `produce_message` JSON-serializes value and flushes.
