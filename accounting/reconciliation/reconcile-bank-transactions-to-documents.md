# Reconcile bank transactions to documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reconcile bank transactions to documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper; Finance User; System (ML auto-reconciliation and script-flagged runs via `reconcileBankTransactionWithFlag`); Customer (accept/reject ML match on separate endpoint) |
| **Business Outcome** | Bank lines are matched to the right accounting documents in SleekBooks so the ledger and document records reflect intentional reconciliation—including manual, forced sync-from-ledger, and backlog/script runs. |
| **Entry Point / Surface** | Coding Engine REST API under `/reconciliation` — e.g. `POST /reconciliation/document/:documentId/reconcile` (standard), `POST /reconciliation/document/:documentId/force-reconcile`, `POST /reconciliation/reconcile-with-flag` (optional `from_script`); plus status reads `GET .../get-bank-transaction-status-in-sb`, `GET .../:documentId/detailed-status`. Exact Sleek App navigation not defined in these files. |
| **Short Description** | Loads published documents and reconciliation state, prepares reconcile entries (including cash-coded vs document paths), and calls SleekBooks to perform the bank–document link. Standard flow uses authenticated user context or system user for auto-ML. Force reconciliation updates from SleekBooks when the bank line is already reconciled upstream. Script-flagged reconciliation reuses the same reconcile path then sets `reconciled_from_script` on the reconciliation record for traceability. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **SleekBooks** (`SleekbooksService`: `getBankTransactionById`, `getPaymentEntryByInvoiceID`, `reconcileBankTransaction`, `unreconcileBankTransaction`); **MongoDB** documents (`documentdetailevents`) and reconciliations; **ML** suggestions via `ml_reconciliation_results.bank_transactions`; **Kafka/events** (`CodingEngineEventType.DOCUMENT_RECONCILED`, `EventUtils.publishEvent`, `DataStreamerService` for ML); **Sleek Auditor** audit logs; **Ledger** (`LedgerTransactionDbService`) for related flows; company master (`Company`) for UEN and ledger type. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (Coding Engine — `Reconciliation` model: `bank_transaction`, `reconcile_entries`, `ml_reconciliation_results`, `reconciled_from_script`, `status`); `documentdetailevents` (Sleek Receipts — document load and status updates in linked flows); `companies` (Coding Engine — company lookup by `company_id`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which Sleek App screens call each route; whether all markets use the same reconciliation rules; confirm product naming for “force” vs operator-facing copy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`src/reconciliation/reconciliation.controller.ts`)

- **`POST document/:documentId/reconcile`** — `AuthGuard`; `reconciliationService.reconcileBankTransaction(documentId, transaction, userDetails)` — standard user-driven reconciliation with user identity for audit.
- **`POST document/:documentId/force-reconcile`** — `AuthGuard`; `forceReconcileBankTransaction` — when SB already shows bank line reconciled, syncs document side from payment entry.
- **`GET document/:documentId/get-bank-transaction-status-in-sb`** — `AuthGuard`; `@ApiOperation` describes SB status and flags for journal (cash coded) vs document reconciliation; `getBankTransactionStatusInSB`.
- **`POST reconcile-with-flag`** — `AuthGuard`; `@ApiOperation` “Reconcile document with script flag tracking”; body `ReconcileWithFlagDto` (`document_id`, `bank_transaction_name`, `from_script`); `reconcileBankTransactionWithFlag`.
- **`GET :documentId/detailed-status`** — returns `reconciled_from_script`, `reconcile_entries`, `bank_transaction`, etc.; `getDetailedReconciliationStatus`.

### Service (`src/reconciliation/reconciliation.service.ts`)

- **`reconcileBankTransaction`** — Resolves document via aggregation (published to SleekBooks, last publish entry done); `checkInvoiceStatus`; loads `Company` (requires UEN); distinguishes manual vs ML auto via presence of `bank_transaction` in request (`findReconciliationForProcessing`); `prepareReconciliationForUpdate`; `createInitialReconcileEntry` with optional cash-coded flag from `checkIfBankTransactionIsCashCoded` (Journal Entry payment document); `unreconcileCashCodedTransactionIfNeeded` for manual path; **`sleekbooksService.reconcileBankTransaction(reconciliation, company, { reconcile_entry_id, auto_reconcile })`**.
- **`forceReconcileBankTransaction`** — `sleekbooksService.getBankTransactionById`; if status already `RECONCILED`, loads payment entry and **`updateReconciledDocumentFromSBPaymentEntry`** → `processReconciledDocuments` → `createReconciliationEntryDocumentReconciledFromSB`, document `reconciliation_id` + reconciled status, `DOCUMENT_RECONCILED` event, Sleek Auditor.
- **`reconcileBankTransactionWithFlag`** — Optionally hydrates bank line from `ml_reconciliation_results.bank_transactions` by id; short-circuits if document already reconciled; calls **`reconcileBankTransaction(..., SYSTEM_USER)`**; if `from_script`, **`reconciliationModel.updateOne` sets `reconciled_from_script: true`**.
- **`getBankTransactionStatusInSB`** — Per ML bank line, SB status and `checkBankTransactionReconciliationLinks` → `reconciliation_type`, `is_cash_coded`, `is_document_reconciled`.
- **`getDetailedReconciliationStatus`** — Exposes `reconciled_from_script` and reconcile entry list for UI/API consumers.

### Schema (`src/reconciliation/models/reconciliation.schema.ts`)

- **`reconciled_from_script`** — Boolean, default false; documents backlog/script reconciliation.
- **`reconcile_entries`**, **`bank_transaction`**, **`ml_reconciliation_results`** — Core state for matches and ML suggestions.

### Interfaces (`src/reconciliation/interface/reconciliation.interface.ts`)

- Comments map SleekBooks `transaction_id` / ML `id` to ledger identifiers for consistent matching.

### Enums (`src/reconciliation/enum/reconciliation.enum.ts`)

- **`ReconciliationType`** — `cash_coded`, `document_reconciled`, etc., used when interpreting SB links.
- **`PaymentDocumentType.JOURNAL_ENTRY`** — Used in cash-coded detection.
