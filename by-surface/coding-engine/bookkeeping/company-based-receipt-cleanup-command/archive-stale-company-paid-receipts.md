# Archive stale company-paid receipts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Archive stale company-paid receipts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Removes outdated company-paid and related in-books documents from active bookkeeping by archiving them, cancelling linked SleekBooks invoices where applicable, and leaving an auditable trail so ledger and receipt views stay aligned with fiscal year cutoffs, company lifecycle, and Xero migration. |
| **Entry Point / Surface** | Kubernetes CronJob (`company-based-receipt-cleanup` in SG/HK/AU/UK staging and production); local/ops: `npx nest start --entryFile app.command -- company-based-receipt-cleanup.command` with `IS_COMPANY_BASED_RECEIPT_CLEANUP_ENABLED=true` and `KAFKA_ENABLED_CONSUMER=false` (per README pattern) |
| **Short Description** | Batch job loads eligible `IN_BOOKS` documents that were published to SleekBooks with a completed invoice, are company/corporate/sales-invoice paid, and have no positive reconcilable match count. It tags candidates for archive by three rules: document date more than three months before the FYE cutoff derived from last filed FY end (via Sleek FYE service), company in a non-live status from SleekBack, or company ledger is Xero while the document still reflects a SleekBooks publish. After deduplication, it sets `is_archived`, bulk-cancels SleekBooks transactions by invoice type in batches of 100, and writes per-document audit logs to Sleek Auditor (batched, with retry). Gated globally by `IS_COMPANY_BASED_RECEIPT_CLEANUP_ENABLED`. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | `SleekFyeService.findCompaniesFyInfoByCompanyIds` (FYE windows); `SleekBackService.getAllCompanies` (non-live status); `company` records `ledger_type` for Xero vs SleekBooks; `SleekbooksService.bulkCancelTransactions`; `SleekAuditorService.bulkInsertLogsToSleekAuditor`; document publish/archive flows (`updateDocuments`, `DocumentActionTypeVariable.ARCHIVE`); related webhook handlers for SB cancel/delete (separate code paths) |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (read/update — archive); `companies` (read — `ledger_type` for Xero companies) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `setSleekbooksTransactionToCancelled` has no explicit `return []` when there are no transactions to cancel (implicit `undefined`); confirm whether any callers rely on `cancelledInvoices` always being an array. Exact Cron schedules and alerting live in cluster manifests outside this repo path. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Command (`src/commands/company-based-receipt-cleanup/company-based-receipt-cleanup.command.ts`)

- **`CompanyBasedReceiptCleanupCommand`:** `@Command({ name: 'company-based-receipt-cleanup.command', description: 'Company based receipt cleanup' })`.
- **`run`:** If `IS_COMPANY_BASED_RECEIPT_CLEANUP_ENABLED === 'true'`, calls `documentService.companyBasedReceiptCleanup()`; otherwise logs skip. Always `process.exit(0)` on completion.

### Orchestration (`src/document/document.service.ts`)

- **`companyBasedReceiptCleanup`:** Logs timing; calls `archiveCompanyDocuments(false)` (dry run flag exists in code but fixed `false` here).
- **`archiveCompanyDocuments(isDryRun)`:** Builds Mongo query for `status: IN_BOOKS`, not deleted/archived/duplicated, `paid_by` in `PAID_BY_COMPANY`, `CORPORATE`, `SALES_INVOICE`, `publish_entries` with SleekBooks `DONE` and `invoice_id`, and `total_reconcilable_match_count` absent or `<= 0`. Loads companies’ FYE via `findCompaniesWithFYE` → `sleekFyeService.findCompaniesFyInfoByCompanyIds` (batches of 100); applies `findDocumentsDatedMoreThan3MonthsBeforeFYE` / `isDateBeforeFYE` (cutoff = FYE minus 3 months). Non-live path: `findNonLiveCompanies` → `sleekBackService.getAllCompanies` filtered by `NON_LIVE_COMPANY_STATUSES`. Xero path: `findCompaniesOnLedgerType(..., XERO)` on `companyModel`. Merges three `ArchivableDocument` lists with `ArchiveReason` (`FYE`, `NON_LIVE`, `XERO`), `deduplicateDocumentsById` (`uniqBy` on `_id`). Then `setDocumentToArchived` → `updateDocuments` with `is_archived: true` and archive action type; `setSleekbooksTransactionToCancelled` → `getSleekbooksTransactionIdsWithType` + `processBulkCancelByType` → `sleekbooksService.bulkCancelTransactions` per invoice type in batches of 100; `createAuditLogsForDocumentsFromScript` groups by reason text and calls `createManyAuditLogsForDocumentsFromScript` → `prepareAuditLogs` + `processAuditLogsByBatch` → `sleekAuditorService.bulkInsertLogsToSleekAuditor` (50 per batch, retry loop). Logs a multi-line summary counts.

### Supporting methods (same file)

- **`prepareAuditLogs`:** Message combines archive reason, “Corresponding SB invoice”, and cancel outcome from `CANCELLED_INVOICE_STATUS_MESSAGE`; action string documents auto-archive by system script; tags `CES_{documentId}`.

### Schema

- **`src/document/models/document.schema.ts`:** Collection `documentdetailevents`.

### Config / operations

- **`src/config.ts`:** `IS_COMPANY_BASED_RECEIPT_CLEANUP_ENABLED`.
- **`src/app.module.ts`:** Conditionally loads `CompanyBasedReceiptCleanupModule` when env flag is `true`.
- **`kubernetes/*/Cronjob.yaml` & `configMap.yaml`:** CronJob runs the command with Kafka consumer disabled; flag varies by environment (e.g. some SIT UK `false`).

### Tests

- `test/document/service/companyBasedReceiptCleanup.spec.ts` — behaviour of `companyBasedReceiptCleanup` / `archiveCompanyDocuments` and helpers.
- `src/commands/company-based-receipt-cleanup/company-based-receipt-cleanup.command.spec.ts` — command wiring and flag gating.
