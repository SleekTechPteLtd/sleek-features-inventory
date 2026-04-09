# Manage bank prompt and template configuration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage bank prompt and template configuration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin; internal services and tooling authenticated with the extraction service client secret (`SLEEK_SERVICE_CLIENT_SECRET`) |
| **Business Outcome** | Per-bank records in MongoDB map institutions and optional platforms to Felic prompt aliases and keyword-driven template variants so bank statement extraction picks the right prompts and layouts. |
| **Entry Point / Surface** | Extraction service HTTP API under `/prompt/database/*` (not an end-user Sleek app route in this repo); callers are typically operations or automation that maintain configs. |
| **Short Description** | Authenticated CRUD APIs create, list, fetch, update, and delete `BankConfig` documents keyed by `bank_name`, `template_name`, and optional `platform`. Stored fields include `prompt_name` (Felic alias), `search_keywords` (template disambiguation), and timestamps. `ClaudeStatementExtractor` loads configs by bank, filters by `PLATFORM` environment, and resolves prompt files and multi-template keyword matching at extraction time. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | **Upstream:** Felic AI prompt registry (`get_prompts_ai` / `helpers.py` by `prompt_name` alias). **Runtime:** `DbOperations.get_bank_config` → `BankConfig` MongoDB queries; `app/extractors/claude_statement.py` `get_prompt_file` / `detect_template`. **Related:** JSON seed `app/config/prompt_name.json` and `read_prompt_name_json` exist alongside DB-backed config; Kafka and REST extraction paths that invoke Claude modules. **Downstream:** Successful extraction depends on correct `BankConfig` rows for each bank and platform. |
| **Service / Repository** | sleek-statement-extraction-service |
| **DB - Collections** | MongoDB: collection name from environment variable `COLLECTION_NAME` (Bunnet `BankConfig` document model; database `DB_NAME`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether bank config is edited only via this API or also via separate admin UIs or migration jobs outside this repo. Exact production collection name not fixed in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Model** — `app/db/db_bunnet.py`: `BankConfig` (`bank_name`, `template_name`, `prompt_name`, `search_keywords`, optional `platform`, `created_at`, `updated_at`); Bunnet `Settings.name = COLLECTION_NAME`; indexes on `bank_name`, `platform`, `template_name`. `init_db()` registers the model on application startup (`main.py` `startup_event`).
- **API surface** — `app/main.py` (all `dependencies=[Depends(get_api_key)]`): `POST /prompt/database/create`, `GET /prompt/database/get_all`, `GET /prompt/database/get/{bank_name}` (optional `platform` query), `PUT /prompt/database/update/{bank_name}/{template_name}` (optional `platform`), `DELETE /prompt/database/delete/{bank_name}/{template_name}` (optional `platform`), `POST /prompt/database/create_multiple`. Create paths enforce uniqueness on `bank_name` + `template_name` (+ `platform` when set). Update mutates `prompt_name`, `search_keywords`, `platform`, `updated_at`.
- **DB access helper** — `app/config/db_operations.py`: `DbOperations.get_bank_config(bank_name)` → `BankConfig.find({"bank_name": bank_name})`.
- **Extraction consumption** — `app/extractors/claude_statement.py`: `ClaudeStatementExtractor.get_prompt_file` loads configs, keeps rows where `platform` is null or matches `os.getenv("PLATFORM")`, single-template vs multi-template branches using `prompt_name` and `(template_name, search_keywords)` tuples; `detect_template` uses keyword lists from configuration.
- **Auth** — `app/main.py`: `APIKeyHeader` `Authorization` must equal `SLEEK_SERVICE_CLIENT_SECRET` (`get_api_key`).
