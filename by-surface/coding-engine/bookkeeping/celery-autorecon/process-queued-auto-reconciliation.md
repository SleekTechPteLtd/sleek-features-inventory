# Process queued auto-reconciliation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process queued auto-reconciliation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Supporting documents are matched to bank transactions (same-currency, FX-normalized, or pre-matched from sleek-match) with optional AI scoring so downstream accounting systems can consume trusted reconciliation outcomes over Kafka. |
| **Entry Point / Surface** | Asynchronous pipeline: Celery task `celery_autorecon` on the `autorecon` app (Redis broker/backend); optional Kafka-driven path where `KafkaWrapper` consumes a reconciliation-queries topic and `delay`s the same task. Direct HTTP: FastAPI `POST /reconcile` on the service router. Not an end-user app screen. |
| **Short Description** | Workers pull reconciliation payloads (document plus candidate bank rows), run rule-based matching (`simple_match_transactions`: amount/date/currency, loose tolerance, optional reference fuzzy match), fall back to FX-aware matching when no same-currency hit (`fx_matching` using cached or API exchange rates in Mongo), optionally run AI adjudication (Claude via LangChain, prompts from FelicAI with Redis cache) when configured and eligible, then publish JSON results to the reconciliation results Kafka topic. Sleek-match source skips rule matching and only formats plus adjudicates. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Redis (Celery broker `redis_broker`, result backend `redis_result_backend`, prompt template cache `redis_cache_client` db 1); Kafka Confluent producer to `RECONCILIATION_RESULTS_TOPIC` (default `MLReconciliationResultEvent`); optional aiokafka consumer on `RECONCILIATION_QUERIES_TOPIC` (default `MLReconciliationEvent`) dispatching to Celery; MongoDB Atlas `sleek_ml.exchange_rates` for FX cache; RapidAPI historical currency API; FelicAI HTTP API for prompt templates; Anthropic API for AI adjudication; upstream publishers of reconciliation job messages. |
| **Service / Repository** | ml-autorecon-service |
| **DB - Collections** | MongoDB: database `sleek_ml`, collection `exchange_rates` (read/write for FX rate cache in `fx_matching`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether production traffic primarily enters via Kafka consumer, Celery enqueue only, or HTTP `/reconcile`; whether `match_references` (fuzzy) is used on any active code path (defined but not wired into `simple_match_transactions` in reviewed files). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`app/celery_worker.py`**: Celery app `autorecon`; `worker_process_init` creates a fork-safe `KafkaWrapper` producer for `reconcilitation_results_topic` (settings env `RECONCILIATION_RESULTS_TOPIC`). Task `celery_autorecon` calls `match_transaction(details)` then `produce_msg(result)` JSON to Kafka, or skips send if producer init failed.
- **`app/kafka_utils.py`**: `KafkaWrapper` — Confluent producer with `read_ccloud_config()`, `produce_msg` JSON encode, flush/retry; async `AIOKafkaConsumer` path `send_consumer_message` loads JSON and `self.celery_task.delay(msg)` for queue handoff.
- **`app/autorecon/endpoints.py`**: `match_transaction` orchestrates: `sleek-match` → `_format_sleek_match_result` + optional `_should_run_ai_adjudication` / `_apply_ai_adjudication`; else `simple_match_transactions` then `fx_matching` if no matches; AI path uses `AI_ADJUDICATOR_START_DATE` and ML reconciliation idempotency skip. `POST /reconcile` exposes `match_transaction`. Core matchers: `match_amount_date`, `loose_*`, `simple_match_transactions` (pandas), settings `DATE_TOLERANCE_DAYS`, `LOOSE_AMOUNT_VARIANCE_PERCENT`, `MAX_MATCHES_RETURNED`.
- **`app/autorecon/fx_matching.py`**: `get_rates_collection()` → `mongo_client["sleek_ml"]["exchange_rates"]`; `get_exchange_rate` RapidAPI + Mongo cache; `fx_matching` normalizes amounts with per-row FX, filters by `AMOUNT_VARIANCE_PERCENT` and date window, emits matches with `fx_rate` and `confidence`.
- **`app/autorecon/ai_adjudicator.py`**: `score_and_rank_matches` → `AdjudicatorAgent.score_matches` (LangChain + `ChatAnthropic`), `PromptTemplateManager.fetch_prompt_template` (FelicAI + Redis), `validate_extracted_text`, `_determine_auto_accept` vs `AI_CONFIDENCE_THRESHOLD`; env `AI_ADJUDICATOR_ENABLED`, `ANTHROPIC_API_KEY`.
