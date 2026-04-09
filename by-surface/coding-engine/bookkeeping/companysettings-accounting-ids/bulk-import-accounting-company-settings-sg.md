# Bulk import accounting integration company settings

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk import accounting integration company settings |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Singapore entities get Xero, Dext, and Hubdoc identifiers plus accounting ledger and document-submission preferences stored on company settings in one spreadsheet-driven pass, so downstream receipt and bookkeeping flows can resolve the correct integrations and policies. |
| **Entry Point / Surface** | **CLI / ops script** — run `companysettings-accounting-ids.js` with first argument `development`, `staging`, or `production`; reads `src/scripts/company-settings/company-settings-{env}.xlsx`, worksheet `results`. Not an app UI. |
| **Short Description** | Reads each spreadsheet row and, only when `entity_code` is `SLEEK_SG`, builds a `bulkWrite` upsert that adds Xero, Dext, and Hubdoc IDs via `$addToSet` and applies `accounting_tools` using human-readable ledger and document-submission labels mapped to stored values through `company-setting-service`. The `erpnext_id` column is read but not written by this script. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **`company-setting-service`**: `getAccountingLedgerValue`, `getDocumentSubmissionValue` (labels from `constants/accounting-tools`). **Runtime**: `exceljs`, `dotenv-flow`, Mongo via `database/server`. Related API paths on same service: `updateAccountingTools`, `updateAccountingThirdPartyIds` for non-bulk updates. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `companysettings` (Mongoose model `CompanySetting`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether the `updateOne` payload mixing `$addToSet` with a top-level `accounting_tools` object is valid for the MongoDB server version in use (normally nested fields require `$set`). Confirm operational ownership of the Excel files and who may run the script per environment. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/scripts/company-settings/companysettings-accounting-ids.js`

- **Input**: Excel path from `ENV_FILE_PATH[env]` (`company-settings-development.xlsx`, `company-settings-staging.xlsx`, `company-settings-production.xlsx` beside the script).
- **Worksheet**: `results`; row columns (by position): unused, `entity_code`, `companyid`, `erpnext_id` (unused in updates), `accounting_ledger`, `xero_id`, `document_submission`, `dext_id`, `hubdoc_id`.
- **Filter**: Only rows with `entity_code === "SLEEK_SG"` and at least one of `xero_id`, `dext_id`, `hubdoc_id` produce a write operation.
- **Write**: `CompanySetting.bulkWrite` with `updateOne`: `filter: { company: ObjectId(companyid) }`, `upsert: true`, `update` with `$addToSet` for present ID fields and `accounting_tools` built from `companySettingService.getAccountingLedgerValue(accounting_ledger)` and `getDocumentSubmissionValue(document_submission)`.
- **Bootstrap**: `databaseServer.connect()`, logs start/end and bulk write result.

### `src/services/company-setting-service.js`

- **`getAccountingLedgerValue` / `getDocumentSubmissionValue`**: Match spreadsheet labels to `ACCOUNTING_LEDGERS` / `DOCUMENT_SUMBMISSION_TYPES` values; default to `NONE` when no label matches.
- **`updateAccountingTools`**: Validates ledger and document-submission types; sets full `accounting_tools` including `document_submission_client_own` (not used by the bulk script).
- **`updateAccountingThirdPartyIds`**: API-oriented `$addToSet` / create for Xero, ERPNext, Dext, Hubdoc IDs — parallel pattern to the script’s ID handling.

### `src/schemas/company-setting.js`

- **Model**: `CompanySetting` with `company` (ObjectId, required), `dext_ids`, `hubdoc_ids`, `xero_ids`, `erpnext_ids` (string arrays), `accounting_tools` (Object), `whitelisted`, timestamps.
