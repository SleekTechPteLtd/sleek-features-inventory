# Backfill receipt totals in functional currency

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Backfill receipt totals in functional currency |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Receipt document events carry a `converted_total_amount` in each company’s functional currency so downstream accounting and reporting show consistent amounts even when historical rows were missing or invalid conversion values. |
| **Entry Point / Surface** | Operational / maintenance: run `node src/scripts/update-conversion-amount.js` (after `databaseServer.connect()` via dotenv); no HTTP surface or in-app navigation — one-off or scheduled batch outside the main API process. |
| **Short Description** | Selects `DocumentDetailEvent` rows with positive `total_amount` but missing or non-positive `converted_total_amount`, loads each company’s functional currency from SleekBack, converts `total_amount` from document currency to functional currency using exchangerate.host (or copies amount when currencies match), and bulk-updates `converted_total_amount` to two decimal places. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SleekBack HTTP API `POST external-receipts/functional-currency` (`getFunctionalCurrencyByCompanyIds`); public FX API `https://api.exchangerate.host/convert`; MongoDB `DocumentDetailEvent` documents; upstream receipt ingestion flows that populate `total_amount`, `currency`, `document_date` |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (read query; bulk update `converted_total_amount`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether this script is run on a schedule or only ad hoc is not defined in-repo. Rate limits or reliability of exchangerate.host for large backfills are not handled in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Script (`src/scripts/update-conversion-amount.js`)

- **`getDocumentEvents`:** `DocumentDetailEvent.find` with `total_amount > 0` and (`converted_total_amount` missing or `<= 0`). Throws if none.
- **`getCompaniesFunctionalCurrency`:** Dedupes `company` ids from events; `sleekBackApi.getFunctionalCurrencyByCompanyIds`; expects `response.data.data` map of company id → functional currency code.
- **`getConversionAmount`:** GET `api.exchangerate.host/convert` with `from`, `to`, `date` (clamped to today if future), `amount` (floored at 0); returns `data.result`.
- **`updateConvertedTotalAmount`:** Unordered bulk op per event; skips rows missing `_id`, `company`, `document_date`, `total_amount`, `currency`, or functional currency for company. If functional currency equals document `currency`, sets conversion to `total_amount`; else awaits `getConversionAmount`. `$set: { converted_total_amount: Number(conversionAmt.toFixed(2)) }`.
- **`main`:** Chains `getDocumentEvents` → `getCompaniesFunctionalCurrency` → `updateConvertedTotalAmount`. On error, logs and `process.exit()` without code.
- **Bootstrap:** `dotenv-flow`, `databaseServer.connect()`, then async IIFE; logs duration and bulk result via `flatted` `stringify`.

### SleekBack client (`src/external-api/sleek-back.js`)

- **`getFunctionalCurrencyByCompanyIds(companyIds)`:** `POST` to `external-receipts/functional-currency` with body `{ companyIds }`, via shared `AXIOS_DEFAULTS.createDefaultAxiosObject`.

### Schema (`src/schemas/document-detail-event.js`)

- **Model:** `DocumentDetailEvent`; fields include `currency`, `total_amount`, `converted_total_amount`, `document_date`, `company` (ObjectId), plus `converted_total_tax_amount` and related amount fields. Pre-hooks on `validate`, `updateOne`, `updateMany` for `currency_rate` only — not specific to this backfill.
