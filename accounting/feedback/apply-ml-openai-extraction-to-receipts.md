# Apply ML and OpenAI extraction to receipts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply ML and OpenAI extraction to receipts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Receipts get structured fields, categories, and tax treatment from ML/OpenAI pipelines so bookkeeping stays consistent without manual re-keying. |
| **Entry Point / Surface** | Coding Engine HTTP callbacks (`POST /feedback/extraction`, `POST /feedback/openai-extraction`); OpenAI completion handlers (`handleOAIExtractionDoneEvent`, `handleOpenAICategoryDone`); internal test hook `POST /feedback/openai-category-extraction-done`; authenticated users via `PUT /feedback/:documentId` and `GET /feedback/document/:documentId` (Sleek App flows that hit these APIs). |
| **Short Description** | Ingests ML bookkeeping payloads and OpenAI extraction payloads, resolves supplier and chart-of-accounts rules, updates receipt documents (line items, GST, duplicates), writes audit logs, and optionally auto-publishes to the ledger or routes expense-claim receipts into the claim report. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Supplier rules service (HTTP: smart rules, specific rules, combination lists); COA service (`getCompanyCoa`); bank service for auto-publish bank mapping; claim report service for expense claim rows; Sleek Auditor for activity logs; DataStreamer / `MLCategoryEvent` when category must be resolved via ML; document events (`documentUtilService.fetchAndPublishDocumentEvent`, `eventUtils.publishEvent`); downstream `DocumentService.publishDocument` (Xero/SleekBooks per company ledger). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `mlfeedbackschemas`, `documentdetailevents` (SleekReceipts connection); `Company` model on CODING_ENGINE connection (company master including `accounting_settings`, `receipt_system_status`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact production collection name for `Company` if not default `companies`; whether non-SG deployments use the same GST branches (code is GST-aware via `accounting_settings` and env). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface (`feedback.controller.ts`)

- `POST feedback/extraction` — `receiveExtractionData` — `@ApiOperation` “Receive extraction data from ML”; no `AuthGuard` (system callback).
- `POST feedback/openai-extraction` — `handleOpenAIExtraction` — “Process document extraction using OpenAI”.
- `PUT feedback/:documentId` — `updateFeedbackById` — `AuthGuard`.
- `GET feedback/document/:documentId` — `getFeedbackByDocumentId` — `AuthGuard`.
- `POST feedback/openai-category-extraction-done` — `handleOpenAICategoryDone` — test path when Kafka is unavailable.

### Core orchestration (`feedback.service.ts`)

- `receiveExtractionData` — parses ML payload (`formatMLBK`), branches `ML_FEEDBACK` vs `DOCUMENT_EVENT`; optional similar-supplier resolution (`receiveExtractionDataFindSimilarSupplier`); parent supplier via `supplierService`; `DOCUMENT_EVENT` path calls `receiveExtractionDataHandleDocumentEventCase` → `receiveExtractionDataHandleDocumentEventCaseProcessDocumentUpdate`.
- Supplier and COA: `getSpecificOrSmartRulesMapping` (specific rules via `supplierService.getSpecificRules`, smart rules via HTTP to `VITE_APP_SUPPLIER_RULES_API`, `inheritRules`, `handleChartOfAccounts`, `matchInChartOfAccounts`); OpenAI category fallback `handleCategoryNotFoundInCustomRules` (publishes `MLCategoryEvent` when enabled).
- Document enrichment: `getDocumentTypeMapping` (publish_as / paid_by / extracted type); `findDuplicatedDocuments` / `handleDuplicatedDocuments` (links `duplicated_documents`, publishes events); `handleDefaultLineItems` → `documentService.getLineItems`, `getDocumentNetAmount`; GST path `initialGstCalculationForExtractionData` when default line items disabled.
- Persistence: `documentService.updateDocumentById` with `isFromExtraction=true`; `updateFeedBackCategory`; `documentService.autoAssignDocuments`.
- Auto-publish: gated by `IS_AUTO_PUBLISH_ENABLED`, `validateDocumentToPublish`, `isEligibleForAutoPublish`, company `receipt_system_status`; `determineAutoPublish` (ML + supplier rules vs OpenAI category); `documentService.publishDocument` or `claimReportService.addSingleReportItemRow` for expense claim / personal paid_by; `publishToLedgerForAutoPublish` / `handleExpenseClaimAutoPublish` for OpenAI path; `DocumentPublishViaType` (SMART_RULE, CUSTOM_RULE, AI).
- `handleOpenAIExtraction` — `prepareAIData`, `processSupplierRules`, `processCategory` (COA match with `CoaPopulatedBy.AI`), `prepareDocumentEventDetails`, `updateDocumentById`, optional auto-publish.
- `handleOAIExtractionDoneEvent` / `handleOpenAICategoryDone` — build `extractedDataFromOAI`, delegate to `receiveExtractionDataHandleDocumentEventCaseProcessDocumentUpdate`.
- Audit: `sleekAuditorService.insertLogsToSleekAuditor`, `addAuditLogForCategoryAllocation`, `addOAIExtractionAuditLogs`, `monitorDocumentDifferenceAuditLog`, `addDefaultLineItemsAuditLog`.

### Document updates and publishing (`document.service.ts`)

- `updateDocumentById` — central merge of extraction fields; status transition from `EXTRACTING` to `PROCESSING`; currency/GST handling hooks.
- `getLineItems` — default line item from category, amounts, tax, ledger type.
- `publishDocument` — publish pipeline (line validation, company/ledger, conversion rates, `publishedVia` including AI).
- `autoAssignDocuments` — assigns unassigned documents for active companies (also cron-driven).

### Schemas

- `feedback.schema.ts` — collection `mlfeedbackschemas`; `document_event` links to receipt document.
- `document.schema.ts` — collection `documentdetailevents`; holds receipt fields updated by extraction.
