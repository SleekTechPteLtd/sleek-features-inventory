# Process bank statement extractions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process bank statement extractions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Bank statement PDFs become structured, categorized transactions and reliable success or failure signals for downstream accounting and bookkeeping workflows. |
| **Entry Point / Surface** | Asynchronous pipeline: Celery worker task `celery_extract` (Redis queue `extraction`), invoked when upstream services enqueue jobs with statement metadata; not an end-user screen. |
| **Short Description** | The worker downloads each statement by ID from the bank-statement service, selects a bank-specific extraction template, runs the matching extractor to parse transactions, optionally enriches rows via a categorization HTTP API, and publishes JSON results (including correlation IDs) to a Kafka topic for downstream consumers. A separate `statement_info` path resolves statement metadata from a remote file path and publishes template or query-based info to Kafka. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Redis (Celery broker and results); Kafka (`KAFKA_PUBLISH_TOPIC`); Sleek Bank Statement Management API (`SLEEK_BSM_API_URL`) for download by `statement_id`; Sleek Files internal download (`SLEEK_FILES_API_URL`) for `statement_info` remote paths; categorization service (`CATEGORIZED_TRANSACTIONS_URL`); dynamic extractors under `app.extractors.*`; AWS Textract and PDF tooling used by shared helpers for template matching and OCR paths in `common`/`helpers`. |
| **Service / Repository** | sleek-statement-extraction-service |
| **DB - Collections** | MongoDB: database `DB_NAME`, collection `COLLECTION_NAME` (Bunnet `BankConfig` model)—connection initialized on worker startup via `init_db()`; no direct read/write in the `celery_extract` / `statement_extraction` / `statement_info` paths in the reviewed files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which regions beyond `PLATFORM` env (e.g. HK-specific OpenAI path) are in active use for production traffic; whether `BankConfig` is queried elsewhere in the same worker process outside the reviewed task body. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`app/worker.py`**: Celery app name `extraction`; broker/backend Redis with `REDIS_PREFIX`; `ExtractTask` lazy-instantiates `KafkaProducer` for `KAFKA_PUBLISH_TOPIC`. Task `celery_extract` routes by `data.type`: `statement_info` → `statement_info`, else `statement_extraction`. HK platform always uses `open_ai=True` for extraction; non-HK uses `open_ai=False` when `bank_name` is in `BANK_NAMES`. `statement_extraction`: `download_and_save_to_tempfile(statement_id)`, `get_template` → `get_matched_template(bank_name)`, `perform_extraction` → `extractor_module`, then `get_categorized_transactions` when transactions exist, then `process_extraction_result` (status 200) or Kafka 400 unsupported / 500 error payloads with `statement_id`, `correlationId`, `status`, `result` or `message`.
- **`app/helpers.py`**: `download_and_save_to_tempfile` GET `{SLEEK_BSM_API_URL}/api/bank-statement/download/{statement_id}`; `get_categorized_transactions` POST `{CATEGORIZED_TRANSACTIONS_URL}/categorize` with bearer auth and statement/company/region payload.
- **`app/common.py`**: `extractor_module` loads `app.extractors.{module}` and `{PascalCase}Extractor.extract()`; `get_matched_template` maps bank names to extractor modules (`claude_statement`, `compact_claude_statement`, `hsbc_claude_statement`, etc.); `get_statement_info_from_remote_path` downloads via `download_file_and_save_to_tempfile`, `find_matching_template`, optional Textract query fallback.
- **`app/kafka/kafka_producer.py`**: Confluent `Producer` with `KAFKA_BROKER_URL`, SASL, `produce_message(key, value)` JSON-serializing `value` and flushing.
