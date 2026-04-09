# Remediate sleek-match bank link overwrites

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Remediate sleek-match bank link overwrites |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (platform operators running the Nest CLI command) |
| **Business Outcome** | Reconciliation bank-transaction links on IN_BOOKS sleek-match documents align with the ledger-posted bank transaction so bookkeeping reconciliation reflects ledger intent after automated rematch overwrote ML results. |
| **Entry Point / Surface** | Operations: Nest Commander CLI `revert-sleek-match-rematch.command` in acct-coding-engine (`--dryRun` default true, `--startDate` / `--endDate` optional `YYYY-MM-DD` filters on `document_date`). |
| **Short Description** | Scans sleek-match documents in books with at least one reconcilable match, compares reconciliation `ml_reconciliation_results.bank_transactions` to the SleekBooks ledger transaction’s `ledger_transaction_id`, and classifies each document: already correct, trim extraneous matches to the ledger-linked bank transaction, or clear and requeue ML matching. Default run is dry-run (logs only); `--dryRun=false` applies DB updates and triggers downstream reconciliation/ML flows. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `ReconciliationService.removeBankTransactions`, `ReconciliationService.requestMatchByDocId` (ML auto-reconciliation / Kafka publish path); sleek-match document and reconciliation pipelines; cron or jobs that rematch and overwrite `bank_transactions` (referenced in command description) |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (SLEEK_RECEIPTS connection — document query and `total_reconcilable_match_count` updates); `reconciliations` (CODING_ENGINE — `ml_reconciliation_results.bank_transactions`, status, `has_pending_refresh_match`); `ledger_transactions` (CODING_ENGINE — `ledger_transaction_id` as source of truth per document) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | Exact name/schedule of the cronjob that overwrites bank transactions is not defined in these files; whether regional or tenant policies restrict fix-mode runs; desired operational cadence vs one-off remediation. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **CLI — `revert-sleek-match-rematch.command.ts`:** `@Command` name `revert-sleek-match-rematch.command`; description identifies sleek-match documents whose reconciliation `bank_transactions` were overwritten by a cronjob; default dry-run (no DB changes), `--dryRun=false` for fix mode. Parses `--dryRun`, `--startDate`, `--endDate` (`YYYY-MM-DD`). Dry-run calls `RevertSleekMatchRematchService.runDryRun` and logs per-document status (`ALREADY_CORRECT`, `CAN_TRIM`, `NEEDS_ML_REQUEUE`) with `documentId`, `companyId`, counts, current bank tx ids, expected id. Fix mode calls `runFix`, logs trimmed/requeued summaries, and waits **5000ms** after publishes so the Kafka producer can flush. Exits `0`/`1`.

- **Service — `revert-sleek-match-rematch.service.ts`:**
  - **Query scope:** Documents where `source === DocumentSource.SLEEK_MATCH`, `status === DocumentStatus.IN_BOOKS`, `total_reconcilable_match_count >= 1`, optional `document_date` range via `applyDocumentDateFilter`.
  - **Truth source:** For each document, loads `LedgerTransaction` with `accounting_tool: CompanyLedgerType.SLEEKBOOKS` and uses `ledger_transaction_id` as the expected bank transaction id; loads `Reconciliation` by `document_id` and reads `ml_reconciliation_results.bank_transactions` (normalized from array or single object).
  - **Classification:** `isAlreadyCorrect` — count 1 and id matches ledger; `canTrimToCorrect` — count &gt; 1 and one entry matches (trim to that entry); `needsMLRequeue` — no id matches. Documents without a linked ledger tx are counted in `noLedgerTxCount` and skipped from fixes.
  - **Trim fix:** `reconciliationModel.updateOne` sets `ml_reconciliation_results.bank_transactions` to a one-element array; `documentModel.updateOne` sets `total_reconcilable_match_count` to 1.
  - **Requeue fix:** `rerunMLForDocument` — `reconciliationService.removeBankTransactions`, `reconciliationModel.updateOne` with `status: ReconciliationStatus.PENDING` and `has_pending_refresh_match: true`, then `reconciliationService.requestMatchByDocId` with `RequestMatchDTO` `{ has_pending_refresh_match: true, is_delete_match: false }`. Fix path processes trim and requeue candidates in batches of **100** (`REQUEUE_BATCH_SIZE`).

- **Types — `revert-sleek-match-rematch.types.ts`:** `RevertSleekMatchRematchOptions`, `BankTransactionDetail`, `AffectedDocumentStatus`, `AffectedDocumentDryRun`, dry-run and fix result interfaces (`RevertSleekMatchRematchDryRunResult`, `RevertSleekMatchRematchFixResult`, `TrimmedDocumentResult`, `RequeuedDocumentResult`).

- **Module — `revert-sleek-match-rematch.module.ts`:** Registers Mongoose models on `DBConnectionName.SLEEK_RECEIPTS` (documents) and `DBConnectionName.CODING_ENGINE` (reconciliation, ledger transactions); imports `ReconciliationModule` for `ReconciliationService`.

- **Tests (behavior contract):** `revert-sleek-match-rematch.command.spec.ts`, `revert-sleek-match-rematch.service.spec.ts`.
