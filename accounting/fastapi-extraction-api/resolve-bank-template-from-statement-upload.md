# Resolve bank template from a statement upload

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resolve bank template from a statement upload |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Callers can determine which configured bank extraction template applies to a PDF statement and obtain statement metadata (template match or inferred bank, currency, account, period fields) without running full line-item extraction. |
| **Entry Point / Surface** | Sleek statement extraction service HTTP API: `POST /api/extract_statement_info` (multipart: PDF `file`, optional `template_name` form field, default `default`). Requires `Authorization` header equal to `SLEEK_SERVICE_CLIENT_SECRET` (same pattern as other extraction routes). No end-user app navigation is defined in this repo. |
| **Short Description** | Accepts an uploaded bank statement PDF, loads regex-driven template definitions from JSON (`app/config/{template_name}.json`), and matches the first page text against each template’s `statement_type_extraction_regex`. On match, enriches the template dict with currency, statement dates, and account number via regex or optional Textract-style entity queries. If no template matches, falls back to vision-backed `extract_query_from_pdf` with fixed questions (bank name, currency, account number, statement start/end dates) and returns that structured result instead. Responds with JSON `{ "result": <matched_template_or_fallback> }`. Does not invoke `extractor_module` or persist to MongoDB. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** PDF upload from any authorized backend client. **Template config:** JSON files under `app/config/` via `load_template`. **Matching:** `find_matching_template` → `extract_text_from_pdf` (first page) + regex; optional `extract_query_from_pdf` / `extract_query` when `use_textract_query` is true on a template, or when no regex match (fallback queries in `get_statement_info_from_file`). **Related:** Full extraction path `POST /api/extract_transactions` uses `get_matched_template_from_file` and then `extractor_module`; Kafka path uses `get_matched_template_from_id` + BSM download. **Separate:** MongoDB `BankConfig` and `/prompt/database/*` routes manage prompt metadata for banks but are not used by `extract_statement_info`. |
| **Service / Repository** | sleek-statement-extraction-service |
| **DB - Collections** | None for this route — templates are loaded from on-disk JSON; `BankConfig` (MongoDB, Bunnet) is used elsewhere in the same service for bank prompt CRUD, not by `get_statement_info_from_file`. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which upstream product or service calls `/api/extract_statement_info` in production and whether volume justifies Medium criticality. Whether markets (SG/HK/UK/AU) differ by template JSON only. `main.py` registers two different route handlers both named `extract_transactions_api` (duplicate Python name) — confirm intentional. `get_statement_info_from_file` returns `[]` on some exceptions while the route expects a dict or 404; error-handling consistency. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app/main.py`

- `POST /api/extract_statement_info` — `Depends(get_api_key)`; multipart `UploadFile`, optional `template_name` (default `"default"`).
- Wraps `template_name` in `ExtractionData`; calls `get_statement_info_from_file(file=file, template_name=template_name)`.
- `matched_template is None` → `HTTPException` 404 with `UNSUPPORTED_BANK_CONFIGURATION_MESSAGE`.
- Success → `JSONResponse({'result': matched_template})`.
- `get_api_key`: `Authorization` must equal `os.environ.get('SLEEK_SERVICE_CLIENT_SECRET')`.

### `app/common.py`

- **`get_statement_info_from_file`:** Loads templates via `load_template(template_name)`; validates extension with `allowed_file`; writes upload to temp PDF; `find_matching_template(filepath, templates)`; if `None`, `extract_query_from_pdf(filepath, queries)` with fixed keys `bank`, `currency`, `account_number`, `start_date`, `end_date`; logs and returns `(matched_template, filepath)`.

### `app/helpers.py`

- **`load_template`:** Reads `app/config/{template_name.template_name}.json`, returns `config["template"]` (list of template dicts).
- **`find_matching_template`:** First-page PDF text via `extract_text_from_pdf`; for each template, regex `statement_type_extraction_regex`; on match, optionally `extract_query_from_pdf` when `use_textract_query == "true"`, else regex helpers for currency, dates, account number; mutates template dict with `account_number`, `statement_date`, `currency`, balances when applicable; returns first match or `None`.
- **`extract_query_from_pdf`:** Renders first page to image, `extract_query` + `extract_query_preprocess` for fallback metadata when regex routing fails.

### Contrast: full extraction (not this capability)

- `get_matched_template_from_file` in the same module returns template + path for `extractor_module`; `extract_statement_info` stops at metadata and never calls `extractor_module`.
