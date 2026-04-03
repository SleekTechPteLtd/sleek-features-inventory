# Multi-bank accounting questionnaire coverage across companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Multi-bank accounting questionnaire coverage across companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Internal teams can find companies whose accounting onboarding questionnaire lists more than one bank so they can review banking and accounting coverage in bulk without opening each company manually. |
| **Entry Point / Surface** | Internal HTTP API on sleek-back: `GET /internal/get-all-banks-in-accounting-questionnaire` (mounted on the internal-services router). Guard: `internalServicesMiddleware()` — shared-secret internal auth; not for browser or public clients. Optional query: `skip`, `limit`, `company_id` (restricts to one company when a valid ObjectId). |
| **Short Description** | Returns a paginated list of accounting questionnaires that have at least two bank entries (MongoDB filter `banks.1` exists). Each item is shaped as company id, name, UEN, address, and the full `banks` array from the questionnaire. Companies are populated from the questionnaire’s `company` reference. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Related internal routes** on the same controller: `GET /internal/findAllCompanies?include_accounting_questionnaire=true` (joins questionnaire onto companies without the multi-bank filter); `GET /internal/companies/:companyId/accounting-questionnaire-answers` (single-company questionnaire read); `PUT /internal/companies/:companyId/accounting-questionnaire/other-currency` (updates `other_currency` using bank currencies). **Data model**: `AccountingQuestionnaire` schema (`banks` array, `company_functional_currency`, `other_currency`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `accountingquestionnaires` (read with `find`, optional `company` match; query requires second element in `banks`); `companies` (read via `populate('company')`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which internal tools or jobs call this route is not named in these files. Whether “multi-bank” was intended to mean two or more banks only via `banks.1` (at least two entries) matches the implementation; edge cases with sparse arrays are not covered in the tests shown. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/internal-service/company-controller.js`

- **`GET /internal/get-all-banks-in-accounting-questionnaire`** — `internalServicesMiddleware()`. Validates query with `Validator.object`: optional `skip`, `limit`, `company_id`.
- **Query** — Base filter `{ "banks.1": { $exists: true } }` so only questionnaires with at least two `banks` array elements are returned. If `company_id` is a valid ObjectId, adds `company` to the filter.
- **Data load** — `AccountingQuestionnaire.find(query).populate("company").skip(skip).limit(limit).exec()`.
- **Response** — JSON `{ status_code: 200, message: null, data: [...] }` where each element maps to `company_id`, `company_name`, `company_uen`, `company_address` (from populated company via `lodash/get`), and `banks` from the questionnaire document.

### `schemas/accounting-questionnaire.js`

- **Model** — `mongoose.model("AccountingQuestionnaire", accountingQuestionnaire)`; collection name defaults to **`accountingquestionnaires`**.
- **`banks`** — Array of subdocuments: `name`, `bankName`, `accountNumber`, `currency`, `bsbNumber`, `bankStatementSource` (enum including client send, mailroom, accountant, SBA, SleekBooks bank feed, Sleek bot, Xero bank feed).

### `tests/controllers/internal-service/company-controller/get-all-banks-in-accounting-questionnaire.js`

- Covers `GET /internal/get-all-banks-in-accounting-questionnaire` with invalid `company_id`, valid `company_id`, and empty query (expects HTTP 200 in each case).
