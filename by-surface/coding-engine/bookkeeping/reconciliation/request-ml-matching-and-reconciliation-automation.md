# Request ML matching and reconciliation automation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Request ML matching and reconciliation automation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper / Finance User (per-document refresh); System (scheduled batch, company-wide sweep); Operations / automation (manual daily batch trigger, API-key maintenance jobs) |
| **Business Outcome** | Keeps ML-driven bank–document matching flowing: users can refresh matches per document, batches can fan out requests after bank activity or on a schedule, and background jobs align stored ML bank lines with SleekBooks/Xero truth when reconciliation is already reflected in the ledger. |
| **Entry Point / Surface** | Coding Engine HTTP API under `reconciliation` — `POST …/request-match-by-doc-id/:documentId` (authenticated); `POST …/request-match/company/:companyId` (company-scoped batch); `POST …/trigger-daily-reconciliation-cronjob-manually` (manual daily batch); `POST …/clean-up-auto-match-receipt` and `POST …/clean-up-auto-match-xero-published-reconciliation-documents` (API key). Not a single end-user screen; consumed by app, ops, or integrations. |
| **Short Description** | On demand, requests ML matching for one document (with optional pending-refresh flags and delete-match behaviour) or for all eligible documents in a company after bank exports, publishing `MLReconciliationEvent` via the data streamer when SleekBooks bank lines and ledger checks pass. A separate batched job walks eligible documents in chunks to send the same ML pipeline (daily cron analogue). API-key endpoints run background cleanup: align receipt documents with journal reconciliation state and strip ML bank transactions when Xero-published documents are reconciled. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: SleekBooks (`getBankTransactions`, `filterBankTransactionsResponse`, `getJournalEntry`, ledger invoice checks), company validation, optional feedback/OCR text for company batch. Downstream: `MLReconciliationEvent` → ML reconciliation pipeline and `reconciliation.listener` (process ML results). Related: `requestToMLAutoReconciliation` / `requestToMLAutoReconciliationForSleekMatch` for Sleek-match + AI adjudicator path. Document events (`DOCUMENT_RECONCILED`), Sleek Auditor logs on receipt cleanup. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (e.g. `has_pending_refresh_match`, match updates), `documentdetailevents` (documents queried and patched in cleanup), `companies` (validation, reconciliation refresh date) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST …/request-match/company/:companyId` has no `AuthGuard` in code — confirm whether this is intentional (internal network only) or should be gated. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/reconciliation/reconciliation.controller.ts`**
  - `POST request-match-by-doc-id/:documentId` + `AuthGuard` → `reconciliationService.requestMatchByDocId(documentId, data)`.
  - `POST request-match/company/:companyId` → `requestToMLAutoReconciliationByCompany(companyId)` (no auth guard on this route in file).
  - `POST trigger-daily-reconciliation-cronjob-manually` → `requestToMLAutoReconciliationBasedOnDocStatus()` (no guard).
  - `POST clean-up-auto-match-receipt` + `ApiKeyGuard` + query `getAffectedDocs` → `cleanUpAutoMatchReceipt`.
  - `POST clean-up-auto-match-xero-published-reconciliation-documents` + `ApiKeyGuard` + query `dryRun` → `cleanUpAutoMatchXeroPublishedReconciliationDocuments`.

- **`src/reconciliation/reconciliation.service.ts`**
  - `requestMatchByDocId`: loads document; `shouldSkipReconciliationRequest`; Sleek-match branch with `requestToMLAutoReconciliationForSleekMatch` or skip; else updates `has_pending_refresh_match`, optional `removeBankTransactions`, then `requestToMLAutoReconciliation` when `isAutoReconcileEnabled` and `has_pending_refresh_match`.
  - `requestToMLAutoReconciliationByCompany`: validates company, `getDocumentsForReconciliationMatch`, excludes `SLEEK_MATCH` source, `fetchFeedbackMapForDocuments`, per document `processDocumentForMLReconciliation` → SleekBooks bank tx, `deleteEmptyBankTransactions`, `checkLedgerInvoiceStatus`, `publishMLReconciliationEvent` via `dataStreamerService.publish(MLReconciliationEvent.name, …)`.
  - `requestToMLAutoReconciliationBasedOnDocStatus`: batched cursor (`BATCH_SIZE` 5000), `getDocumentsForReconciliationMatchBatched`, excludes sleek-match, per document fetches bank transactions, `deleteEmptyBankTransactions`, publishes `MLReconciliationEvent`, `updateCompanyReconciliationRefreshDate`, summary logging.
  - `cleanUpAutoMatchXeroPublishedReconciliationDocuments`: aggregate documents `publish_entries` last `DONE` to Xero; `removeBankTransactions(documentId, dryRun)`.
  - `cleanUpAutoMatchReceipt`: `IN_BOOKS` + supported doc types, non–sleek-match; `getJournalEntry` for reconciled status → may set `RECONCILED`, publish `DOCUMENT_RECONCILED`, `deleteEmptyBankTransactions`, auditor logs.

- **`src/reconciliation/models/reconciliation.schema.ts`**
  - `Reconciliation` schema: `has_pending_refresh_match`, `ml_reconciliation_results`, indexes on ML bank transaction fields.

- **`src/reconciliation/interface/reconciliation.interface.ts`**
  - `RequestMatchDTO`: `has_pending_refresh_match`, `is_delete_match`.
