# Sync Sleekbooks document status to Coding Engine

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Sleekbooks document status to Coding Engine |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System; Operations User (manual CLI runs) |
| **Business Outcome** | Keeps published Sleekbooks-linked receipts in Coding Engine aligned with invoice truth in Sleekbooks (and BigQuery mirror) so reconciliation, archive, removal, and compliance audit trails stay accurate when invoices are paid, cancelled, or missing upstream. |
| **Entry Point / Surface** | Coding Engine CLI: `sb-document-status-sync.command` (Nest Commander; description references weekly sync); typically scheduled jobs or operators with `--batchSize` (default 100, max 200), `--dryRun` |
| **Short Description** | Finds documents in books with a completed Sleekbooks publish entry and invoice id matching `ACC-PINV-*` / `ACC-SINV-*`. For each document, resolves invoice status via BigQuery (with retry/fallback) then Sleekbooks API if needed. Maps `Paid`, `Cancelled`, and `NOT_FOUND` (absent in both sources) to Coding Engine updates: reconcile, archive, or soft-delete with `script_action`, and bulk-inserts Sleek Auditor audit logs when not in dry run. Other SB statuses are skipped unless they require no change. |
| **Variants / Markets** | SG, HK (BigQuery production table selection via `COUNTRY_CODE`; non-production uses shared non-prod table names) |
| **Dependencies / Related Flows** | BigQuery (`GOOGLE_BQ_CREDENTIALS`, `BQPROJECTID`, `sleekextraction` / `hevo_test`); Sleekbooks (`getPurchaseInvoiceDetails`, `getSalesInvoiceDetails`); `SleekAuditorService.bulkInsertLogsToSleekAuditor`; upstream document publish to Sleekbooks; same service class also implements Xero document status sync (separate command path) |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (Sleek Receipts connection — `Document` model updates: `status`, `is_archived`, `is_deleted`, `is_duplicated`, `script_action`, `$unset` on `duplicated_documents` where applicable) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `COUNTRY_CODE` / env matrix covers all deployed regions beyond SG and HK; exact production schedule and alerting for failed batches are not defined in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Command (`src/commands/sb-document-status-sync/sb-document-status-sync.command.ts`)

- **`SBDocumentStatusSyncCommand`:** `@Command({ name: 'sb-document-status-sync.command', description: 'Sync document status from Sleekbooks to Coding Engine weekly' })` → `run()` calls `documentStatusSyncService.syncSBDocumentStatus(batchSize, isDryRun)`.
- **Options:** `--batchSize` (validated `MIN_BATCH_SIZE`–`MAX_BATCH_SIZE` from enum), `--dryRun` (no DB or audit writes).

### Enum (`src/commands/sb-document-status-sync/enum/sb-document-status-sync.enum.ts`)

- **`DEFAULT_BATCH_SIZE` 100, `MAX_BATCH_SIZE` 200, `MIN_BATCH_SIZE` 1.**
- **`SBInvoiceStatus`:** includes `PAID`, `CANCELLED`, `NOT_FOUND`, and other SB string statuses.
- **`SB_STATUS_MAPPINGS` / `SB_SCRIPT_ACTION_MAPPINGS` / `SB_AUDIT_LOG_MAPPINGS`:** actionable only for `CANCELLED` (archive + `ARCHIVE` / auditor), `PAID` (reconciled + `RECONCILE` / auditor), `NOT_FOUND` (delete flags + `DELETE` / auditor); other statuses omitted intentionally.
- **`SB_TABLE_MAPPINGS`:** production SG/HK purchase and sales BigQuery tables; non-production shared purchase/sales table names.
- **`BIGQUERY_CONFIG.location`:** `asia-southeast1`.

### Service (`src/document/document-status-sync.service.ts`)

- **Model:** `@InjectModel(Document.name, DBConnectionName.SLEEK_RECEIPTS)` → `documentdetailevents`.
- **`syncSBDocumentStatus`:** chunks candidates with `lodash.chunk`, per-batch `processDocumentBatch` with `CompanyLedgerType.SLEEKBOOKS`, then `processAuditLogsBatch` unless dry run.
- **`findDocumentsForSync`:** `$match` in-books, not deleted/archived/duplicated; latest `publish_entries` by `published_on`; for SB: `publish_to` Sleekbooks, `PublishStatus.DONE`, `invoice_id` exists and matches `/^ACC-(PINV|SINV)-/`.
- **`processSingleSBDocument` → `validateAndGetInvoiceType`:** `PINV` → purchase, `SINV` → sales; skips on bad id.
- **`querySBInvoiceData`:** `executeBigQueryQueryWithRetry` then `querySleekbooksWithRetry` if empty; returns `null` only when missing in both (true NOT_FOUND).
- **`updateDocumentBasedOnSBStatus`:** maps status via `getStatusMappings`; destructive path for `NOT_FOUND` + delete mapping logs warnings; `executeDocumentUpdate` / `simulateDocumentUpdate`; `trackCEAction` for summary counts.
- **`processAuditLogsBatch`:** maps to `BasicAuditLogDto`, tags `CES_${documentId}`, `sleekAuditorService.bulkInsertLogsToSleekAuditor`.
- **API errors:** `SB data query operation failed` → skip document to avoid accidental deletion.

### Related (same file, not this CLI)

- **`syncXeroDocumentStatus`**, **`queryXeroInvoiceData`**, BigQuery Xero path — separate Xero document status sync; not invoked by `sb-document-status-sync.command`.
