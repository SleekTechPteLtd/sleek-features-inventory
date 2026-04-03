# Clean stale SleekBooks reconciliation matches

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Clean stale SleekBooks reconciliation matches |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (scheduled batch); Operations User (manual CLI with `--dryRun`) |
| **Business Outcome** | In-books documents no longer show misleading “open” ML bank matches or inflated reconcilable counts after those bank lines are already reconciled in the ledger. |
| **Entry Point / Surface** | Coding Engine CLI: `nest start --entryFile app.command -- cleanup-stale-matches.command` with optional `--dryRun true`; Kubernetes CronJobs in staging/SIT/production (e.g. SG/HK) run the same command with Kafka producers/consumers disabled |
| **Short Description** | For SleekBooks companies only, scans `IN_BOOKS` documents that still report `total_reconcilable_match_count > 0`, loads reconciliation rows with non-empty `ml_reconciliation_results.bank_transactions`, and cross-checks bank transaction IDs against `ledger_transactions` where `document_upload_status` is `IN_BOOKS` and `accounting_tool` is SleekBooks. Removes stale (already-reconciled-in-ledger) entries from the ML result array and resets `total_reconcilable_match_count` to the count of remaining `NEW` matches. Batches documents (50) and aggregates ledger lookups per company. Xero is explicitly out of scope per service comments. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `LedgerTransactionDbService.findReconciledTransactionIds` (read `ledger_transactions`); company filter `accounting_tools.accountingLedger` matching ERP (SleekBooks scope); same service’s `excludeReconciledBankTransactions` (pre-ML exclusion, complementary); upstream reconciliation and ML match persistence; manual/batch reconciliation flows that mark ledger transactions `IN_BOOKS` |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (Sleek Receipts — `total_reconcilable_match_count`); `reconciliations` (Coding Engine — `ml_reconciliation_results.bank_transactions`); `ledger_transactions` (read — reconciled id set via `ledger_transaction_id`, `document_upload_status`, `accounting_tool`); companies (Coding Engine — SleekBooks company list) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Public name `cleanStaleMatchesAndRetrigger` suggests a retrigger step; implementation only cleans stored ML results and counts — confirm whether ML retrigger is obsolete naming or planned elsewhere. Exact schedule and alerting for CronJobs are in cluster config outside this note. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Command (`src/commands/cleanup-stale-matches/cleanup-stale-matches.command.ts`)

- **`CleanupStaleMatchesCommand`:** `@Command({ name: 'cleanup-stale-matches.command', description: 'Clean stale reconciliation matches and fix affected document counts' })`.
- **`run`:** calls `reconciliationService.cleanStaleMatchesAndRetrigger(dryRun ?? false)`; logs start and JSON completion; `process.exit(0)`.
- **Option:** `--dryRun <boolean>` via `parseDryRun` (only `'true'` is true).

### Service (`src/reconciliation/reconciliation.service.ts`)

- **`cleanStaleMatchesAndRetrigger(dryRun)`:** Returns `{ totalProcessed, totalCleaned }`. Loads SleekBooks company IDs via `getSleekBooksCompanyIds`, then cursor-batches stale docs with `fetchStaleDocumentBatch` (`status: IN_BOOKS`, `total_reconcilable_match_count > 0`, company in SB set, batch 50, `_id` ascending). For each batch, `processStaleDocumentBatch` loads reconciliations with non-empty `ml_reconciliation_results.bank_transactions`, builds per-company bank txn id sets, calls `findAllReconciledTransactionIds` → `ledgerTransactionDbService.findReconciledTransactionIds` per company, then `cleanSingleReconciliation` per row: filter out txn ids present in reconciled set, recompute `newMatchCount` from `ReconciliationBankTransactionStatus.NEW`, `updateOne` on reconciliation then document when not dry run. JSDoc describes intended daily cron behaviour and SleekBooks-only scope.

- **`cleanSingleReconciliation`:** Updates `ml_reconciliation_results.bank_transactions` and `total_reconcilable_match_count` in lockstep when not dry run.

### Ledger helper (`src/ledger-transaction/ledger-transaction-db.service.ts`)

- **`findReconciledTransactionIds`:** Queries `ledger_transaction_id` in provided list with `document_upload_status: IN_BOOKS` and `accounting_tool: SLEEKBOOKS`.

### Tests

- `src/commands/cleanup-stale-matches/cleanup-stale-matches.command.spec.ts` — CLI wiring and `dryRun` defaults.
- `test/reconciliation/service/cleanupStaleMatches.spec.ts` — service behaviour including dry-run without writes.

### Operations

- `kubernetes/*/Cronjob.yaml` — `cleanup-stale-matches.command` with `KAFKA_ENABLED_PRODUCER=false` and `KAFKA_ENABLED_CONSUMER=false` in multiple environments.
