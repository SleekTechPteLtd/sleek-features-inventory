# Process ML reconciliation results

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process ML reconciliation results |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps bank-document reconciliation state accurate after ML scoring: pending reconciliations, refreshed match counts, and optional automatic bank matching when policies and signals agree—so finance teams spend less time on repetitive matching. |
| **Entry Point / Surface** | System only — Kafka subscribers on the Coding Engine reconciliation listener (`MLReconciliationResultEvent`, `ReconciliationDoneEvent`, `ReconciliationFailedEvent`); internal `POST …/reconciliation-listener/process-message` for targeted testing. Not an end-user screen. |
| **Short Description** | On each ML result event, the service deduplicates work (Redis), may skip when supporting-doc rules or prior terminal state apply, strips bank lines already reconciled in ledger data, then upserts a pending reconciliation and updates the document’s total reconciliable match count. It optionally auto-reconciles via Sleek-match (single candidate, CMS flag), full ML path (CMS ML flag, accept, AI auto-reconcile, recommended transaction id), or a fallback when company auto-reconciliation publishing is on. Completion and failure from downstream reconciliation are applied via separate events. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: ML reconciliation pipeline (emits `MLReconciliationResultEvent`). Downstream: SleekBooks bank reconciliation APIs via `ReconciliationService.reconcileBankTransaction`; company reconciliation settings (`auto_reconciliation_publishing`). CMS/AppFeature toggles: ML auto-reconciliation per company, Sleek-match auto-reconciliation global, supporting documents. Redis (`CommonCacheService`) for short-lived idempotency. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (Reconciliation model, default Mongoose collection name), `documentdetailevents` (documents — `total_reconcilable_match_count`, `is_auto_reconcile_reviewed`), `ledger_transactions` (filter already-reconciled bank transaction ids; linked ledger tx for supporting-documents skip path), `companies` (embedded `reconciliation_settings` read via document → company) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none — market-specific rules not visible in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`kafka/listeners/reconciliation.listener.ts`**
  - `@Controller('reconciliation-listener')`; `@SubscribeEvent(MLReconciliationResultEvent.name)` → `onMLReconciliationResultEvent`; `@Post('process-message')` for tests.
  - Idempotency: `commonCacheService.setCacheIfNotExists` per `document_id` (or event id for done/failed), TTL 30s.
  - Skips: duplicate cache; `isSkippingReconciliationEntryGeneration` (supporting documents + linked SleekBooks ledger transaction); existing `ReconciliationStatus.RECONCILED`; `is_auto_reconcile_reviewed` on document.
  - `filterReconciledFromMLResults`: `ledgerTransactionDbService.findReconciledTransactionIds` removes transactions already `IN_BOOKS` for SleekBooks.
  - `prepareInitialReconciliation`: `reconciliationService.createInitialReconciliation` (pending, ML payload); `countTotalReconciliableMatchesByDocumentId`; `documentForReconciliationModuleService.updateDocumentTotalReconcilableMatchCountById`.
  - Auto paths: `shouldExecuteSleekMatchAutoReconciliation` → `executeSleekMatchAutoReconciliation`; `shouldExecuteMLAutoReconciliation` → `executeMLAutoReconciliation`; else `executeFallbackAutoReconciliation` if `auto_reconciliation_publishing`; else `logAutoReconciliationSkipped` / `logAutoReconcileMatrix`.
  - `reconciliationService.reconcileBankTransaction` for auto flows; `checkRecommendedTransactionStatus` before ML/sleek-match reconcile.
  - `@SubscribeEvent(ReconciliationDoneEvent.name)` → `reconciliationService.updateReconciliationDoneEvent`; `@SubscribeEvent(ReconciliationFailedEvent.name)` → `updateReconciliationFailedEvent`.

- **`reconciliation/reconciliation.service.ts`**
  - `createInitialReconciliation` → `updateOrCreateReconciliation`.
  - `countTotalReconciliableMatchesByDocumentId`: counts `NEW` bank transactions in latest reconciliation’s `ml_reconciliation_results.bank_transactions`.
  - `getReconciliationSettingsByDocumentId`: loads document and company `reconciliation_settings`.
  - `reconcileBankTransaction`, `checkRecommendedTransactionStatus`, `logAutoReconcileMatrix`, done/failed event updaters as invoked by listener.

- **`document/document.for_reconciliation_module.service.ts`**
  - `Document` model on `SLEEK_RECEIPTS` / collection `documentdetailevents`; `updateDocumentTotalReconcilableMatchCountById` sets `total_reconcilable_match_count`; `getDocumentById` for gating and company resolution.

- **`ledger-transaction/ledger-transaction-db.service.ts`**
  - `LedgerTransaction` on `CODING_ENGINE` / collection `ledger_transactions`; `findReconciledTransactionIds` (`document_upload_status` `IN_BOOKS`, `SLEEKBOOKS`); `findLinkedLedgerTransaction` for supporting-documents skip logic.

- **Schemas**: `reconciliation/models/reconciliation.schema.ts` (`Reconciliation`, embedded ML result and bank transaction shapes); `document/models/document.schema.ts` (`documentdetailevents`); `ledger-transaction/models/ledger-transaction.schema.ts` (`ledger_transactions`).
