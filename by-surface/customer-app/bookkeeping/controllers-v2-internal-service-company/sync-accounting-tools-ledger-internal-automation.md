# Sync accounting tools ledger from internal automation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync accounting tools ledger from internal automation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (internal automation / script runner calling internal-service API) |
| **Business Outcome** | When internal scripts or ops tooling change which accounting ledger a company uses or how document submission is configured, those changes are stored on the company record and pushed to Sleek Receipts, Kafka, and the coding engine so downstream bookkeeping and receipt flows stay aligned. |
| **Entry Point / Surface** | **Internal service API only** (not Sleek App): **`POST`** `…/companies/:companyId/update-accounting-tools-ledger-from-script-runner` on the **controllers-v2 internal-service** router, guarded by **`internalServicesMiddleware`** (Basic auth against configured internal secret; optional bypass in non-prod). |
| **Short Description** | Accepts **`accountingLedger`** (string) and optional **`documentSubmission`** (string) and **`updateDocumentSubmissionOnly`** (boolean). Merges into **`company.accounting_tools`** (preserving other keys when only document submission is updated), persists with **`Company.updateOne`**, then calls **`updateAccountingTools`**, which emits **`sleek-back.accounting-tools-had-updated`**, triggers **`triggerCompanyDataUpdateTopic`** for **`accounting_tool_update`**, **`syncCodingEngineCompanyData`**, and **`PUT`** Sleek Receipts **`/api/company-settings/{companyId}/accounting-tools`**. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Downstream** — **Sleek Receipts** (`SLEEK_RECEIPTS_URL`, `SLEEK_RECEIPTS_AUTHORIZATION`); **Kafka** via **`SleekBackKafkaService`** (`COMPANY_ACCOUNTING_TOOLS_HAD_UPDATED`, company data update topic, coding engine sync). **Upstream** — whichever internal job or script invokes this internal route (not identified in these files). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | **`companies`** (Mongoose **`Company`**: reads by **`_id`**, **`$set`** on **`accounting_tools`** object; subfields used here include **`accountingLedger`**, **`documentSubmission`** nested under **`accounting_tools`**) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which named internal job or service calls this route in production; whether market-specific behaviour is enforced elsewhere (payload is generic strings). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/internal-service/company.js`

- **`router.route("/companies/:companyId/update-accounting-tools-ledger-from-script-runner").post(internalServicesMiddleware(), updateAccountingToolsLedgerFromScriptRunner)`** — registers the handler behind internal-services auth.

### `controllers-v2/handlers/accounting-ledger/update-accounting-tools-ledger-from-script-runner.js`

- **`updateAccountingToolsLedgerFromScriptRunner`** — **`validationUtils.validateOrReject`** on **`accountingLedger`** (required string), **`updateDocumentSubmissionOnly`** (optional boolean), **`documentSubmission`** (optional string); **`Company.findById(companyId)`**; builds **`dataTobeUpdated`** from existing **`company.accounting_tools`**; skips **`accountingLedger`** when **`updateDocumentSubmissionOnly`** is true; sets **`documentSubmission`** when provided; **`Company.updateOne({ _id }, { $set: { accounting_tools: dataTobeUpdated } })`**; **`updateAccountingTools(companyId, dataTobeUpdated)`**; **`successResponseHandler`** / **`errorResponseHandler`**.

### `services/external-receipts-service.js`

- **`updateAccountingTools(companyId, payload)`** — if Kafka streamer available: **`send(SLEEK_BACK_KAFKA_TOPICS.COMPANY_ACCOUNTING_TOOLS_HAD_UPDATED, …)`** with **`company_id`** and **`accounting-tools`** payload; **`triggerCompanyDataUpdateTopic(..., "accounting_tool_update", { company_id, accounting_tools })`**; **`syncCodingEngineCompanyData(..., { company_id, accounting_tools })`**; HTTP **`PUT`** **`${SLEEK_RECEIPTS_URL}/api/company-settings/${companyId}/accounting-tools`** with **`Authorization: SLEEK_RECEIPTS_AUTHORIZATION`**.

### `schemas/company.js`

- **`accounting_tools: Object`** — flexible object backing **`accountingLedger`** / **`documentSubmission`** updates.
