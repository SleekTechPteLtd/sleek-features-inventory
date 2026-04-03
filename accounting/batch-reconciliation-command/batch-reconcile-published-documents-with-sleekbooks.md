# Batch reconcile published documents with Sleekbooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Batch reconcile published documents with Sleekbooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System; Operations User (manual CLI runs) |
| **Business Outcome** | Keeps in-books documents aligned with Sleekbooks so receipt and bank-side reconciliation state matches the ledger after bulk publish, including marking reconciled, clearing stale ML matches, and retiring documents that no longer exist or are cancelled upstream. |
| **Entry Point / Surface** | Coding Engine CLI: `script:batch-reconciliation` (Nest Commander `batch-reconciliation.command`); typically scheduled jobs or operators running the batch with `--batchSize`, `--dryRun`, `--lastProcessedId` |
| **Short Description** | Selects documents that are in books, published to Sleekbooks with a completed publish entry and invoice id, then pulls bulk invoice/payment/bank state from Sleekbooks in chunks. Applies rules to set reconciled status via `DocumentService`, soft-delete when both sides are missing in SB, archive when the invoice is cancelled, clear ML bank-transaction matches when the invoice is gone but the bank doc is in a clearable state, or skip/draft/submitted paths when drafts or pending states apply. Emits reconciliation/document events and Sleek Auditor logs when not in dry run. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleekbooks (`getBulkInvoiceWithPaymentEntryAndBankTransaction`); `DocumentService.processReconciledDocumentsFromBatchProcess` → `ReconciliationService` (create/update reconciliation, document status `RECONCILED`); `DOCUMENT_RECONCILED` / `DOCUMENT_UNRECONCILED` via `eventUtils`; `SleekAuditorService`; `DocumentUtilService` for invoice type and document events; publish alignment and in-books lifecycle (upstream: documents published to SB) |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (Sleek Receipts connection — document updates: status, reconciliation_id, flags, match counts); `reconciliations` (Coding Engine — `ml_reconciliation_results.bank_transactions` unset on clear) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether production schedules and batch sizes are documented outside the repo; confirm expected operator workflow when `dryRun` defaults to `true` in the command (easy to run without writes if options omitted). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Command (`src/scripts/reconciliation-manual/command/reconciliation-manual.command.ts`)

- **`ReconciliationCommand`:** `@Command({ name: 'batch-reconciliation.command', description: 'Run batch reconciliation' })` → `run()` calls `reconciliationManualService.reconcileDocuments(batchSize, dryRun, lastProcessedId)`.
- **Options:** `--batchSize`, `--dryRun` (parsed string `'true'`), `--lastProcessedId` for cursor pagination; `dryRun` defaults to **true** when omitted.

### Service (`src/scripts/reconciliation-manual/services/reconciliation-manual.service.ts`)

- **Query:** `status: 'in_books'`, not deleted/archived/duplicated; `publish_entries` contains entry with `publish_to` Sleekbooks, `status: DONE`, `invoice_id` present; optional `_id: { $gt: lastProcessedId }`; sorted by `_id`, limit `batchSize` (constructor default batch path uses `BATCH_SIZE` from arg or internal default).
- **`batchReconcileDocuments`:** Groups by invoice type from `documentUtilService.getInvoiceTypeFromId`; calls `sleekbooksService.getBulkInvoiceWithPaymentEntryAndBankTransaction` in batches of 100; `getBulkRelatedLinkedTransactions` normalizes invoice/bank presence and errors.
- **`processBatchReconcileDocuments`:** Per document: `handleReconciledStatus` → `updateDocumentStatusToReconciled` / `updateDocumentStatusToReconciledForInvoice` → **`documentService.processReconciledDocumentsFromBatchProcess`** on success path; else `handleNotFoundAndErrorCases` (`tagAsDeleted` when both not found, `clearMatchEntries` when invoice missing and bank status allows); `handleInvoiceFound` (`tagAsArchived` for cancelled, `submittedMock` for draft invoice, `handleNonDraftInvoice` → skip/draft-bank mocks).
- **`clearMatchEntries`:** `reconciliationModel.findOneAndUpdate` unsets `ml_reconciliation_results.bank_transactions`; `documentModel.updateOne` sets `total_reconcilable_match_count: 0`; `documentUtilService.fetchAndPublishDocumentEvent`; `DOCUMENT_UNRECONCILED` event; auditor log.
- **`tagAsDeleted` / `tagAsArchived`:** `documentModel.updateOne` sets `is_deleted` or `is_archived`; `DOCUMENT_UNRECONCILED`; auditor logs.
- **Models:** `@InjectModel(Reconciliation, DBConnectionName.CODING_ENGINE)`, `@InjectModel(Document, DBConnectionName.SLEEK_RECEIPTS)`.

### Document service (`src/document/document.service.ts`)

- **`processReconciledDocumentsFromBatchProcess`:** If bank transaction has `name`, `reconciliationService.createReconciliationEntryDocumentReconciledFromSB`; else `updateOrCreateReconciliation` with `status: 'reconciled'` and empty bank_transactions array. Updates document with `reconciliation_id` and `status: ReconciliationStatus.RECONCILED`; publishes `CodingEngineEventType.DOCUMENT_RECONCILED`; Sleek Auditor success log.

### Interface (`src/scripts/reconciliation-manual/interface/reconciliation-manual.interface.ts`)

- Bulk invoice shapes: `IBulkInvoiceTransactionDetails`, `IInvoiceTransactionDetails`, `IFormattedRelatedLinkedTransaction`, `IProcessedDocumentResult` — used for batch mapping and logging.
