# Run ML-assisted reconciliation via HTTP API

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Run ML-assisted reconciliation via HTTP API |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (integration clients calling the service) |
| **Business Outcome** | Lets operators and upstream integrations trigger document-to-bank matching and optional AI scoring through a documented HTTP surface, so reconciliation proposals can be produced without bespoke wiring per client. |
| **Entry Point / Surface** | Service root (`GET /`, `GET /info`) and health (`GET /ping`); OpenAPI at `/docs` and ReDoc at `/redoc`; primary workflow `POST /autorecon/reconcile` with JSON body. Not a Sleek App screen — HTTP/API integration surface. |
| **Short Description** | The FastAPI app mounts autorecon routes under `/autorecon`. The reconcile endpoint runs rule-based matching (amount, date, currency, fuzzy reference, FX fallback), optional AI adjudication for scored acceptance, and returns structured bank transaction candidates for a document. Startup also wires a Kafka consumer for reconciliation query events via Celery, separate from the synchronous HTTP path. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Callers that POST reconciliation payloads (e.g. flows publishing `MLReconciliationEvent` / results pipelines in other services). **In-process:** `simple_match_transactions`, `fx_matching`, `match_transaction`; optional `autorecon.ai_adjudicator.score_and_rank_matches` (Anthropic/LangChain, FelicAI prompt cache via Redis). **Infra:** Celery (`celery_worker.celery_autorecon`), Kafka topics `MLReconciliationEvent` / `MLReconciliationResultEvent` (settings), consumer started on app startup. |
| **Service / Repository** | ml-autorecon-service |
| **DB - Collections** | None in the HTTP reconcile handler (in-memory pandas matching on the request body; Mongo client exists in `settings` for other service components not shown in these files). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `POST /autorecon/reconcile` has no visible auth dependency in code — confirm network posture (internal mesh, API gateway, mTLS). Whether markets/regions are enforced at deploy time only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`app/main.py`**
  - `FastAPI()`; `app.include_router(autorecon.endpoints.router, prefix="/autorecon")`.
  - `GET /`, `GET /info` point users to `/docs` and `/redoc`; `GET /ping` liveness.
  - `startup_event`: `KafkaWrapper` with `celery_task=celery_autorecon`, consumer topic `reconcilitation_queries_topic` from `settings`, `initialize_consumer()` and `consume()`; `shutdown_event` cancels consumer task.

- **`app/autorecon/endpoints.py`**
  - `APIRouter`; `POST /reconcile` → `autoreconcile_input(reconcile_input: dict = Body(...))` → `match_transaction(reconcile_input)`.
  - `match_transaction`: branches for `source == 'sleek-match'` (`_format_sleek_match_result`, AI adjudication gating via `_should_run_ai_adjudication` / `_apply_ai_adjudication`); else `simple_match_transactions` then `fx_matching` if no matches; AI adjudication when configured and date rules pass.
  - Helpers: `match_amount_date`, `loose_*` matching, `match_references` (fuzzywuzzy `partial_ratio`), `simple_match_transactions` building extraction payload with matched bank rows.

- **`app/settings.py`**
  - Kafka topic names, Redis, Mongo client URI pattern, AI adjudicator and FelicAI-related env (referenced by workers/adjudicator; not directly by the route handlers above).
