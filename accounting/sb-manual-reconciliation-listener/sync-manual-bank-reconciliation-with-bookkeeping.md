# Sync manual bank reconciliation with bookkeeping

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync manual bank reconciliation with bookkeeping |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When someone reconciles or unreconciles a bank transaction against published invoices in Sleek Bank / SleekBooks, the Coding Engine mirrors that state so document status, reconciliation records, and downstream events stay consistent with the books. |
| **Entry Point / Surface** | Event-driven integration: Kafka-style domain events `SleekErpnextServiceReconciledFromSbEvent` and `SleekErpnextServiceUnreconciledFromSbEvent` consumed by `SbManualReconciliationListener` (no end-user app screen). |
| **Short Description** | On **reconciled**: resolves documents by payment-entry references to published SleekBooks invoices, creates or updates a reconciliation row marked as reconciled from SleekBooks, links it on the document, publishes `DOCUMENT_RECONCILED`, and writes Sleek Auditor logs. On **unreconciled**: finds matching manual SB reconciliations, sets documents back to in-books, clears `reconciliation_id`, publishes `DOCUMENT_UNRECONCILED`, and runs local unreconcile logic (including optional SleekBooks API unreconcile). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: Sleek Bank / ERPNext emitting reconciliation events; SleekBooks payment entries and bank transaction payloads. Depends on documents published to SleekBooks (`publish_entries` with `SLEEKBOOKS` and `DONE`, `IN_BOOKS` status). Related: CE auto-reconciliation (`hasAutoReconciliationInProgress` skips concurrent manual SB events); `SleekbooksService` (e.g. `unreconcileBankTransaction`); `SleekAuditorService.insertLogsToSleekAuditor`; internal `CodingEngineEventType.DOCUMENT_RECONCILED` / `DOCUMENT_UNRECONCILED`. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | documentdetailevents, reconciliations |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all production payloads include `payment_entry_detail.data.references` as required; confirm event ordering guarantees vs. auto-reconcile to avoid skipped manual reconciliations in edge races. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Listener** — `src/kafka/listeners/sb-manual-reconciliation.listener.ts`: Nest `@Controller('sb-manual-reconciliation-listener')`; `@SubscribeEvent(SleekErpnextServiceReconciledFromSbEvent.name)` → `reconciliationService.updateReconciledDocumentFromSBPaymentEntry(message?.data?.bank_transaction, message?.data?.payment_entry_detail)`; `@SubscribeEvent(SleekErpnextServiceUnreconciledFromSbEvent.name)` → `documentService.updateUnreconciledDocumentFromSB(message?.data?.bank_transaction)`.
- **Events** — `src/kafka/events/sleek-erpnext-service.reconciled-from-sb.event.ts` (`bank_transaction`, `payment_entry_detail`); `sleek-erpnext-service.unreconciled-from-sb.event.ts` (`bank_transaction`).
- **Reconcile path** — `src/reconciliation/reconciliation.service.ts`:
  - `updateReconciledDocumentFromSBPaymentEntry` → validates `payment_entry_detail?.data?.references` (else `NotFoundException`) → `processReconciledDocuments`.
  - `processReconciledDocuments`: for each reference, `documentModel.findOne` on `publish_entries.invoice_id` = `reference_name`, `publish_to` = `DocumentPublishPreferenceType.SLEEKBOOKS`, `status` = `PublishStatus.DONE`, `status` = `DocumentStatus.IN_BOOKS`; skips if `hasAutoReconciliationInProgress`; `createReconciliationEntryDocumentReconciledFromSB`; `findOneAndUpdate` document with `reconciliation_id` and `ReconciliationStatus.RECONCILED`; `eventUtils.publishEvent(CodingEngineEventType.DOCUMENT_RECONCILED, ...)`; `sleekAuditorService.insertLogsToSleekAuditor` (“Document has been successfully reconciled to SleekBooks”).
  - `createReconciliationEntryDocumentReconciledFromSB`: `reconciliationModel.findOneAndUpdate` upsert with `reconcile_entries` (`reconciled_from`: `SLEEKBOOKS`), `bank_transaction` snapshot, `status` reconciled; updates `ml_reconciliation_results.bank_transactions.$.status` when applicable; `fetchAndPublishReconciliationEvent` for `DOCUMENT_RECONCILED`.
- **Unreconcile path** — `src/document/document.service.ts` `updateUnreconciledDocumentFromSB`: `reconciliationService.getReconciliationsFromSbByBankTransactionInvoiceId` (filter `bank_transaction.id` = `bank_transaction['name']`, `auto_reconcile: false`, reconciled status, `reconcile_entries.reconciled_from` = `SLEEKBOOKS`); per match, `documentModel.updateOne` `$set` `DocumentStatus.IN_BOOKS`, `$unset` `reconciliation_id`; `eventUtils.publishEvent(CodingEngineEventType.DOCUMENT_UNRECONCILED, ...)`; `reconciliationService.unreconcileManuallyReconciledStatusById` (may call `sleekbooksService.unreconcileBankTransaction`, sets reconciliation `PENDING`, etc.).
- **Schemas** — `src/document/models/document.schema.ts`: collection `documentdetailevents`. `src/reconciliation/models/reconciliation.schema.ts`: `Reconciliation` model (default Mongoose collection name `reconciliations`).
