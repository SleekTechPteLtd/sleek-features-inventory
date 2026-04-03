# Daily ML auto-reconciliation batch

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Daily ML auto-reconciliation batch |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (scheduled Kubernetes cron); Operations / support (manual HTTP trigger of the same batch) |
| **Business Outcome** | Keeps receipts and invoices that are already in the books aligned with unreconciled SleekBooks bank activity by fanning out ML matching on a schedule, without users clicking “request match” on each document. |
| **Entry Point / Surface** | Infra: Kubernetes `CronJob` runs Coding Engine in command mode (`nest start --entryFile app.command -- daily-reconciliation.command`) with `IS_AUTO_RECONCILE_ENABLED=true` (see repo `kubernetes/*/Cronjob.yaml`, `README.md`). Optional API: `POST …/reconciliation/trigger-daily-reconciliation-cronjob-manually` invokes the same service method. Not a Sleek App screen. |
| **Short Description** | When auto-reconcile is enabled, the command loads eligible **in_books** documents (published to SleekBooks with a completed publish entry and invoice id), skips Sleek Match–sourced docs, pulls **unreconciled** and **pending** bank lines around each document’s date, filters by ledger, clears empty ML bank rows, checks ledger invoice status, then publishes **`MLReconciliationEvent`** to the data streamer so downstream ML can propose matches. Work is done in batches of 5000 documents with cursor pagination, pauses between batches, and updates each company’s last reconciliation refresh timestamp. |
| **Variants / Markets** | SG, HK (cron manifests exist per region; core logic is not market-specific in code) |
| **Dependencies / Related Flows** | **Upstream:** Document publish to SleekBooks (`publish_entries`), company must be SleekBooks ledger. **SleekBooks:** `getBankTransactions`, `filterBankTransactionsResponse`; `checkLedgerInvoiceStatus` for valid invoice state. **Downstream:** `MLReconciliationEvent` → ML reconciliation pipeline and `reconciliation-listener` (process ML results). Overlaps with company-scoped `requestToMLAutoReconciliationByCompany` and per-document `requestMatchByDocId` but uses a **different document query** (`getDocumentsForReconciliationMatchBatched`). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (batched query and per-document processing), `companies` (`last_reconciliation_match_refresh`), `reconciliations` (via `deleteEmptyBankTransactions` clearing ML bank transaction placeholders) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | The daily batch path does not attach `extracted_text` / feedback map (unlike `requestToMLAutoReconciliationByCompany` → `publishMLReconciliationEvent`); confirm whether ML should receive OCR/feedback for parity. `POST trigger-daily-reconciliation-cronjob-manually` has no auth guard in controller — confirm exposure (internal-only vs oversight). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/commands/daily-reconciliation/daily-reconciliation.command.ts`**
  - Command `daily-reconciliation.command`; reads `IS_AUTO_RECONCILE_ENABLED === 'true'`; calls `reconciliationService.requestToMLAutoReconciliationBasedOnDocStatus()`, then `process.exit(0)`.

- **`src/reconciliation/reconciliation.service.ts`**
  - `requestToMLAutoReconciliationBasedOnDocStatus`: batch loop `BATCH_SIZE` 5000, `getDocumentsForReconciliationMatchBatched(undefined, cursor, BATCH_SIZE)`, filters out `DocumentSource.SLEEK_MATCH`, `validateCompanyAndGet` (requires `uen`, `CompanyLedgerType.SLEEKBOOKS`), `calculateBankTransactionDateRange`, `sleekbooksService.getBankTransactions` with statuses `UNRECONCILED` + `PENDING`, receipt bank account name when applicable, `filterBankTransactionsResponse`, `deleteEmptyBankTransactions`, `checkLedgerInvoiceStatus`, builds message with `document_id`, `company_id`, amounts, parties, dates, `ledger`, `currency`, `bank_transactions`, publishes via `dataStreamerService.publish(MLReconciliationEvent.name, new MLReconciliationEvent(message))`, `logAutoReconcileMatchRequestMatrix`, `updateCompanyReconciliationRefreshDate`; summary logging and optional `globalThis.gc()` between batches.
  - `getDocumentsForReconciliationMatchBatched`: Mongo query on documents — `status: IN_BOOKS`, `source != SLEEK_MATCH`, not deleted/archived/duplicated, `is_auto_reconcile_reviewed` false/null, `paid_by` in company/corporate/sales-invoice receipt types, `publish_entries` `$elemMatch` for `publish_to: SLEEKBOOKS`, `status: DONE`, `invoice_id` present; cursor `_id > last batch last id`; sort `_id` ascending, `limit` batch size.

- **`src/kafka/events/reconciliation/ml-reconciliation.event.ts`**
  - `MLReconciliationEvent` domain event payload shape (document id, amounts, parties, dates, `bank_transactions`, optional `extracted_text` / `source`).

- **`src/reconciliation/reconciliation.controller.ts`**
  - `POST trigger-daily-reconciliation-cronjob-manually` → `requestToMLAutoReconciliationBasedOnDocStatus()`.

- **`test/commands/daily-reconciliation/daily-reconciliation.command.spec.ts`**
  - Asserts service runs when config is `true` and is skipped when `false`.

- **`kubernetes/production-sg/Cronjob.yaml`**, **`kubernetes/production-hk/Cronjob.yaml`** (and staging/sit variants)
  - Cron invokes `daily-reconciliation.command` with `KAFKA_ENABLED_CONSUMER=false`.
