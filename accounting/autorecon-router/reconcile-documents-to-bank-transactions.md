# Reconcile documents to bank transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reconcile documents to bank transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User, Operations User, System (callers submit document and bank-line payloads to the service API) |
| **Business Outcome** | Accounting can propose which bank lines belong to a given document so books and bank activity stay aligned with minimal manual pairing. |
| **Entry Point / Surface** | `ml-autorecon-service` FastAPI: `POST /reconcile` (request body: reconcile payload with `data` containing document fields, `bank_transactions`, optional `source`, `submission_date`, `ml_reconciliation_results`). Typically invoked from bookkeeping / operations flows that orchestrate auto-reconciliation. |
| **Short Description** | Accepts extracted document metadata plus candidate bank transactions and returns proposed matches: exact and loose amount/date matching in document currency, optional fuzzy reference matching, cross-currency matching via FX-normalized amounts when same-currency rules find nothing, pass-through of pre-matched **sleek-match** payloads, and optional AI scoring and ranking (Claude via LangChain) with auto-accept when confidence clears thresholds. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream document extraction and bank feed ingestion; optional `ml_reconciliation_results` (can skip AI when ML IDs align with rule matches); **sleek-match** as `source` bypasses rule matching; RapidAPI historical FX API; MongoDB `exchange_rates` cache; Redis for FelicAI prompt cache; FelicAI for managed prompts; Anthropic API for adjudication. |
| **Service / Repository** | ml-autorecon-service |
| **DB - Collections** | `sleek_ml.exchange_rates` (read/write: FX rate cache for cross-currency matching) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `POST /reconcile` is authenticated or network-restricted at gateway (not visible in router file); production markets and rollout of AI adjudication vs submission-date gate (`AI_ADJUDICATOR_START_DATE`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`app/autorecon/endpoints.py` (FastAPI `APIRouter`):**
  - `POST /reconcile` → `autoreconcile_input` → `match_transaction(reconcile_input)`.
  - **`match_transaction`:** If `data.source == 'sleek-match'`, uses `_format_sleek_match_result` (maps pre-shaped bank lines including `fx_rate`, `confidence`) and may run `_should_run_ai_adjudication` / `_apply_ai_adjudication`. Otherwise runs `simple_match_transactions` (rule pipeline: `match_amount_date` with exact match, then `loose_condition_matching` / `loose_date_matching`, then `loose_amount_matching` with configurable variance and date tolerance from settings; falls back to amount+currency without date). If no matches, calls `fx_matching` from `fx_matching.py`. When matches exist, AI adjudication gated by submission date vs `AI_ADJUDICATOR_START_DATE` and ML result ID alignment (`ml_reconciliation_results.bank_transactions`).
  - **`simple_match_transactions`:** Builds response with `document_id`, `autoreconcile`, `bank_transactions` list entries (`id`, `reference`, `date`, `amount`, `description`, `currency`, `fx_rate`, `confidence`).
  - **`match_references`:** `fuzz.partial_ratio` on document vs bank reference (threshold 95) — present in module but not wired in the shown `simple_match_transactions` path (potential extension or alternate entry).

- **`app/autorecon/fx_matching.py`:**
  - `fx_matching(transactions)`: Loads bank rows into pandas; normalizes dates; computes per-row FX via `get_exchange_rate` (Mongo cache `check_mongo_exchange_rate` on `sleek_ml.exchange_rates`, else RapidAPI `currency-converter5.p.rapidapi.com` historical endpoint, then `add_currency_to_mongo`). Derives `normalized_amount`; filters by configurable amount variance and `DATE_TOLERANCE_DAYS`, excluding trivial `fx_rate == 1` rows from the FX candidate set; returns matched bank lines with `fx_rate` and `confidence: "high"`.

- **`app/autorecon/ai_adjudicator.py`:**
  - `score_and_rank_matches`: Optional LangChain + Anthropic Claude; `PromptTemplateManager.fetch_prompt_template` (FelicAI HTTP + Redis cache); `AdjudicatorAgent.score_matches` fills prompt with document fields, OCR `extracted_text`, and formatted bank lines; parses JSON scores; `_enhance_transactions_with_scores` adds `ai_confidence_score`, `ai_reasoning`, `ai_recommended` vs `AI_CONFIDENCE_THRESHOLD`; `_determine_auto_accept` sets `accept` for single match or clear winner gap; `validate_extracted_text` cross-checks amount/supplier/reference vs OCR when present.
  - Environment toggles: `AI_ADJUDICATOR_ENABLED`, `ANTHROPIC_API_KEY`, model and timeout settings.

- **`app/settings.py` (cross-cutting):** `mongo_client`, `redis_cache_client` (db=1 for prompts), Kafka topic names for reconciliation events (not exercised in the three listed feature files but part of service config).
