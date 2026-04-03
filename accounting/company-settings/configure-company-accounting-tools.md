# Configure company accounting tools

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Configure company accounting tools |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | Each company’s bookkeeping and document intake follow the intended ledger (e.g. Xero Sleek vs client, ERPNext) and submission channel (Sleek, Dext, client-owned), including when the client owns submission. |
| **Entry Point / Surface** | Sleek Receipts HTTP API: `GET /company-settings/:companyId`, `PUT /company-settings/:companyId/accounting-tools` (and related `PUT .../accounting-third-party` for integration IDs). Routes require `Authorization` header equal to `SLEEK_RECEIPTS_TOKEN` (service-to-service); end-user UI or gateway that calls this API is not defined in this repo. |
| **Short Description** | Reads and updates per-company `accounting_tools`: accounting ledger label (mapped to stored enum values), document submission type (Sleek / Dext / client own / none), and `document_submission_client_own`. Creates or updates a `CompanySetting` document keyed by `company`. Optional third-party identifier arrays (Xero, ERPNext, Dext, Hubdoc) are updated on a separate route. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Downstream in this repo**: `company-setting-utils` (`getCompanyAccountingLedger`, `checkCompanyByLedger`) used by PDF and Dext flows; `dext-event-service` and `email-forwarder` read `CompanySetting`. **Cross-system**: Ledger/submission labels align with Xero, ERPNext, Dext, Hubdoc as named in constants and third-party ID fields. Related: company document-submission updates in Coding Engine (`acct-coding-engine` inventory) may overlap conceptually but use a different service and data model. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `companysettings` (Mongoose model `CompanySetting`; default collection name for model `CompanySetting`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `getCompanySettingByCompanyId` is called with `(companyId, query)` from the controller but the service only accepts `companyId` — confirm whether query projection/filter was intended. No schema validation on `document_submission_client_own` type beyond persistence. Exact product UI path and which upstream service holds `SLEEK_RECEIPTS_TOKEN` for production callers. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/routes/company-setting.js`

- **GET** `/company-settings/:companyId` → `validateDocumentEventAuth()`, `getCompanySettingByCompanyId`.
- **PUT** `/company-settings/:companyId/accounting-tools` → `updateAccountingTools`.
- **PUT** `/company-settings/:companyId/accounting-third-party` → `updateAccountingThirdPartyIds`.

### `src/middleware/document-event-middleware.js`

- **`validateDocumentEventAuth`**: Allows request only if `headers.authorization === process.env.SLEEK_RECEIPTS_TOKEN`.

### `src/controllers/company-setting-controller.js`

- **`getCompanySettingByCompanyId`**: Reads `params.companyId`, passes `query` from request to service (see open question).
- **`updateAccountingTools`**: Body → `updateAccountingTools(companyId, accountingTools)`.
- **`updateAccountingThirdPartyIds`**: Body → `updateAccountingThirdPartyIds`.

### `src/constants/accounting-tools.js`

- **`ACCOUNTING_LEDGERS`**: Labels → values `xero_sleek`, `xero_client`, `erp_next`, `none`.
- **`DOCUMENT_SUMBMISSION_TYPES`**: Labels → values `sleek`, `dext`, `client_own`, `none`.
- **`VALID_ACCOUNTING_LEDGERS` / `VALID_DOCUMENT_SUBMISSION_TYPES`**: Whitelists for incoming **labels** (not stored values).

### `src/services/company-setting-service.js`

- **`getAccountingLedgerValue` / `getDocumentSubmissionValue`**: Map human-readable labels from the request to stored enum strings; default to `NONE` values when no match.
- **`getCompanySettingByCompanyId`**: `CompanySetting.findOne({ company: ObjectId(companyId) })`; invalid id → `INVALID_QUERY`.
- **`updateAccountingTools`**: Validates `accountingLedger` and `documentSubmission` against whitelist when non-empty; sets `accounting_tools.accounting_ledger`, `document_submission`, `document_submission_client_own` via `updateOne` or `create`.
- **`updateAccountingThirdPartyIds`**: `$addToSet` into `xero_ids`, `erpnext_ids`, `dext_ids`, `hubdoc_ids` (or `create` with arrays).

### `src/schemas/company-setting.js`

- **Fields**: `company` (ObjectId, required), `dext_ids`, `hubdoc_ids`, `xero_ids`, `erpnext_ids` (string arrays), `accounting_tools` (untyped `Object`), `whitelisted`, timestamps.

### `src/utils/company-setting-utils.js`

- **`getCompanyAccountingLedger`**: Reads `accounting_tools.accounting_ledger` from company settings.
- **`checkCompanyByLedger`**: Compares stored ledger to a passed-in ledger string — used by Dext/PDF utilities for ledger-specific behavior.
