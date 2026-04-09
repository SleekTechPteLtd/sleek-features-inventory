# Resolve statement configuration from remote file

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resolve statement configuration from remote file |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Upstream services learn which bank-statement template and metadata (bank, currency, account number, period) apply to a file referenced by remote path, so they can validate configuration or drive workflows before full extraction. |
| **Entry Point / Surface** | Celery worker `extraction`: task `celery_extract` when the inbound payload has `data.type == "statement_info"` (queue-driven; not an end-user screen). Message carries `extraction_id`, `correlationId`, `data.remote_path`, and `data.template_name`. |
| **Short Description** | The worker downloads the PDF from the internal Files API using `remote_path`, loads template definitions from local JSON (`app/config/{template_name}.json`), matches a template from the first page via regex-driven parsing (with optional Textract-style queries), or falls back to structured questions over the first page when no regex matches. It publishes a Kafka message with type `statement_info`, status `200` and the resolved template/metadata, or `404` when no configuration matches, or `500` on failure. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Callers enqueue `celery_extract` with `statement_info` (e.g. bank statement / configuration services). **Files:** `POST` to `${SLEEK_FILES_API_URL}/api/internal/download` with `remote_path` (basic auth). **Templates:** `app/config/*.json` statement templates. **Downstream:** Kafka topic `${KAFKA_PUBLISH_TOPIC}` (same producer as full `statement_extraction`). **Related:** Full extraction path uses BSM download by `statement_id` and different Kafka payload shape; `get_statement_info_from_file` mirrors this flow for uploaded files. |
| **Service / Repository** | sleek-statement-extraction-service |
| **DB - Collections** | none in this flow — `statement_info` does not read or write MongoDB; the worker still runs `init_db()` for other task types that may use Bunnet (`COLLECTION_NAME` / `BankConfig`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `produce_message` only accepts `(key, value)`; the 404 branch passes `detail=...` instead of `value=...`, which would raise at runtime unless another wrapper exists — verify production behavior. `get_statement_info_from_remote_path` returns `[]` on exception while callers unpack two values; confirm error paths in integration tests. Which services publish `statement_info` jobs and which consumers read the Kafka topic. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app/worker.py`

- `celery_extract`: If `details["data"].get("type") == "statement_info"`, calls `statement_info(details, celery_extract)` (non–Hong Kong branch still routes by `statement_type`; HK platform runs extraction only).
- `statement_info`: Reads `extraction_id`, `correlationId`, `template_name`, `remote_path` from `details`. Wraps `template_name` in `ExtractionData`. Calls `get_statement_info_from_remote_path(remote_path=..., template_name=...)`.
- On success (`matched_template` not `None`): `produce_message(key=extraction_id, value={..., 'type': 'statement_info', 'status': 200, 'result': matched_template})`.
- On `matched_template is None`: intended 404 publish (see Open Questions for keyword argument).
- Exception path: `produce_message` with `status` 500 and error text; then raises `TypeError(NOT_ABLE_TO_PROCESS_STATEMENT)`.

### `app/common.py`

- `get_statement_info_from_remote_path(remote_path, template_name)`: Defines standard metadata queries (bank, currency, account number, start/end dates). `load_template(template_name)` → `app/config/{template_name.template_name}.json`. `download_file_and_save_to_tempfile(remote_path)` for the PDF. `find_matching_template(filepath, templates)`; if `None`, `extract_query_from_pdf(filepath, queries)` for LLM/vision-style extraction. Returns `(matched_template, filepath)` or `[]` on error.

### `app/helpers.py`

- `download_file_and_save_to_tempfile`: `requests.post` to `${SLEEK_FILES_API_URL}/api/internal/download` with JSON `{"remote_path": remote_path}`, decodes base64 `data.content` into a temp file.
- `find_matching_template`: First-page text via `extract_text_from_pdf`; regex match against each template’s `statement_type_extraction_regex`; optional `use_textract_query` path with `entity_queries`; else currency/date/account extraction from regex config.
- `load_template`: Loads `config["template"]` from `app/config/{name}.json`.

### `app/kafka/kafka_producer.py`

- `KafkaProducer.produce_message(self, key, value)` — serializes `value` to JSON for the configured topic.
