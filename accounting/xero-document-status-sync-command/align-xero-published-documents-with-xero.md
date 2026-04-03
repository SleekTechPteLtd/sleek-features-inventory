# Align Xero-published documents with Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Align Xero-published documents with Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System; Operations User (manual CLI runs) |
| **Business Outcome** | Keeps in-books Coding Engine documents that were published to Xero consistent with current Xero invoice status (paid, voided, deleted) so internal records, script actions, and auditor logs reflect reality in Xero. |
| **Entry Point / Surface** | Coding Engine CLI: `xero-document-status-sync.command` (Nest Commander; description references weekly sync); Kubernetes CronJob `xero-document-status-sync` (e.g. production schedule `0 14 * * 6` — Saturday 14:00 UTC); operators may run with `--batchSize` (default 100, max 200), `--dryRun` |
| **Short Description** | Selects documents that are in books, not deleted/archived/duplicated, with a completed Xero publish entry and invoice id. For each document, reads `InvoiceID` and `Status` from BigQuery table `xero_invoices` (entity scoped via `COUNTRY` → `SLEEK_<REGION>`). When status is PAID, VOIDED, or DELETED, applies MongoDB updates (reconcile, archive, or soft-delete plus `script_action`) via `getUpdateQueryByXeroInvoiceStatus`, and bulk-inserts Sleek Auditor audit logs from `getAuditLogsDataForXeroInvoiceStatus` when not in dry run. Other Xero statuses do not produce updates. |
| **Variants / Markets** | SG, HK (CronJobs and env-specific deployments; BigQuery `entity_code` uses `COUNTRY` defaulting to `SG` when unset) |
| **Dependencies / Related Flows** | Google BigQuery Xero pipeline (`GOOGLE_BQ_XERO_CREDENTIALS`, `BQ_XERO_PROJECTID`, `BQ_XERO_DATASET`, `xero_invoices`, `asia-southeast1`); `SleekAuditorService.bulkInsertLogsToSleekAuditor`; upstream publish of documents to Xero; same `DocumentStatusSyncService` also implements Sleekbooks document status sync (`sb-document-status-sync.command`) |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (Sleek Receipts connection — `Document` model: `status`, `is_archived`, `is_deleted`, `is_duplicated`, `script_action`, `$unset` on `duplicated_documents` for deleted path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all live regions beyond SG/HK use the same BigQuery Xero dataset contract; exact alerting/ownership for failed batches is not defined in application code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Command (`src/commands/xero-document-status-sync/xero-document-status-sync.command.ts`)

- **`XeroDocumentStatusSyncCommand`:** `@Command({ name: 'xero-document-status-sync.command', description: 'Sync document status from Xero to Coding Engine weekly' })` → `run()` calls `documentStatusSyncService.syncXeroDocumentStatus(batchSize, isDryRun)`.
- **Options:** `--batchSize` (`MIN_BATCH_SIZE`–`MAX_BATCH_SIZE` from enum), `--dryRun` (no DB updates or audit logs).

### Enum (`src/commands/xero-document-status-sync/enums/xero-document-status-sync.enum.ts`)

- **`DEFAULT_BATCH_SIZE` 100, `MAX_BATCH_SIZE` 200, `MIN_BATCH_SIZE` 1.**
- **`XeroInvoiceStatus`:** `PAID`, `DRAFT`, `DELETED`, `VOIDED`, `AUTHORISED`, `SUBMITTED` — the sync path only maps actionable updates for PAID, DELETED, VOIDED (see util).

### Xero mapping helpers (`src/document/util.ts`)

- **`getUpdateQueryByXeroInvoiceStatus`:** `PAID` → `DocumentStatus.RECONCILED` + `DocumentScriptActionEnum.RECONCILE` / `xero_paid_invoice`; `DELETED` → `is_deleted: true`, `is_duplicated: false`, `DELETE` / `xero_deleted_invoice`, `$unset` `duplicated_documents`; `VOIDED` → `is_archived: true`, `ARCHIVE` / `xero_voided_invoice`; default no query.
- **`getAuditLogsDataForXeroInvoiceStatus`:** paired user-facing action/message strings for PAID, DELETED, VOIDED.

### Service (`src/document/document-status-sync.service.ts`)

- **Model:** `@InjectModel(Document.name, DBConnectionName.SLEEK_RECEIPTS)` → collection `documentdetailevents`.
- **`syncXeroDocumentStatus`:** loads Xero candidates via `findDocumentsForSync(CompanyLedgerType.XERO)`, chunks batches, `processDocumentBatch` → `processSingleXeroDocument`; on success, `processAuditLogsBatch` unless dry run.
- **`findDocumentsForSync` (Xero branch):** in-books, not deleted/archived/duplicated; latest publish entry with `publish_to` Xero, `PublishStatus.DONE`, non-null `invoice_id`.
- **`queryXeroInvoiceData` / `buildInvoiceQueryOptions`:** `SELECT InvoiceID, Status FROM \`${project}.${dataset}.xero_invoices\` WHERE entity_code = @entityCode AND InvoiceID = @invoiceId`; `entityCode` = `SLEEK_${COUNTRY upper}`; credentials `GOOGLE_BQ_XERO_CREDENTIALS`, project `BQ_XERO_PROJECTID`, dataset `BQ_XERO_DATASET`.
- **`processSingleXeroDocument`:** skips without invoice id or BigQuery row; applies `getUpdateQueryByXeroInvoiceStatus` / `getAuditLogsDataForXeroInvoiceStatus`; `executeXeroDocumentUpdate` uses `updateOne` and checks `modifiedCount`; `trackXeroCEAction` counts reconciled / deleted / archived by status.
- **`processAuditLogsBatch`:** maps to `BasicAuditLogDto`, tags `CES_${documentId}`, `sleekAuditorService.bulkInsertLogsToSleekAuditor`.

### Operations

- **Kubernetes:** `kubernetes/*/CronJob.yaml` — job name `xero-document-status-sync` (or env-suffixed in non-prod); container args run `npx nest start --entryFile app.command -- xero-document-status-sync.command`.

### Related (same service, different command)

- **`syncSBDocumentStatus`** — Sleekbooks path; not invoked by `xero-document-status-sync.command`.
