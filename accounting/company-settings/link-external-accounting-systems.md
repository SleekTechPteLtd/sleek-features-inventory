# Link external accounting systems

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Link external accounting systems |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | The company record carries stable identifiers for Xero, ERPNext, Dext, and Hubdoc so downstream bookkeeping and document flows can resolve the correct external accounts and match inbound events to the right Sleek company. |
| **Entry Point / Surface** | Sleek Receipts HTTP API: `GET /company-settings/:companyId` (read settings including third-party id arrays); `PUT /company-settings/:companyId/accounting-third-party` (append third-party ids). All routes use `validateDocumentEventAuth()` — `Authorization` header must equal `SLEEK_RECEIPTS_TOKEN` (service-to-service; calling UI or gateway is not defined in this repo). |
| **Short Description** | Persists per-company arrays of external system identifiers (`xero_id`, `erpnext_id`, `dext_id`, `hubdoc_id` in the request body). On update, existing documents use MongoDB `$addToSet` to append unique values; new company settings documents are created with initial arrays when none exist. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Dext matching** — `dext-event-service.matchDextEvents` loads `CompanySetting.dext_ids` to filter Dext events by `account_crn`. Other integrations (Xero, ERPNext, Hubdoc) are stored for matching; consumers outside these files are not enumerated here. Related: `updateAccountingTools` on the same model (separate capability). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `companysettings` (Mongoose model `CompanySetting`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which product surface calls Sleek Receipts with `SLEEK_RECEIPTS_TOKEN` for these routes? There is no HTTP path in this repo to remove or replace third-party ids (only `$addToSet` append). Whether duplicate semantics across multiple ids per tool are intentional for multi-entity companies. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/routes/company-setting.js`

- **GET** `/company-settings/:companyId` → `getCompanySettingByCompanyId` — middleware `validateDocumentEventAuth()`.
- **PUT** `/company-settings/:companyId/accounting-third-party` → `updateAccountingThirdPartyIds` — same auth.

### `src/middleware/document-event-middleware.js`

- **`validateDocumentEventAuth`**: compares `req.headers.authorization` to `process.env.SLEEK_RECEIPTS_TOKEN`; returns 401-style error from `ERRORS.AUTH_ERROR` when mismatched.

### `src/controllers/company-setting-controller.js`

- **`updateAccountingThirdPartyIds`**: reads `params.companyId`, `body` as `accountingThirdPartyIds`; delegates to `companySettingService.updateAccountingThirdPartyIds`.

### `src/services/company-setting-service.js`

- **`updateAccountingThirdPartyIds(companyId, accountingThirdPartyIds)`**: validates `companyId` as ObjectId; requires at least one key in `accountingThirdPartyIds`; maps `xero_id`, `erpnext_id`, `dext_id`, `hubdoc_id` to schema fields `xero_ids`, `erpnext_ids`, `dext_ids`, `hubdoc_ids`.
- **Existing doc**: `CompanySetting.updateOne` with `$addToSet` per provided id field.
- **New doc**: `CompanySetting.create` with company ObjectId and initial single-element arrays for provided ids.

### `src/schemas/company-setting.js`

- **Model** `CompanySetting`: `company` (ObjectId, required), `dext_ids`, `hubdoc_ids`, `xero_ids`, `erpnext_ids` as `[String]`, plus `accounting_tools`, `whitelisted`, timestamps.

### `src/services/dext-event-service.js` (downstream consumer)

- **`matchDextEvents`**: `CompanySetting.findOne({ company })`, reads `dext_ids` as `dextAccountCrn`, uses `{ account_crn: { $in: dextAccountCrn } }` when matching Dext events to document events.
