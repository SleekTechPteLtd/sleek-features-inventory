# Operate bank activity and reconciliation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Operate bank activity and reconciliation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (HTTP integrations and M2M-guarded routes) |
| **Business Outcome** | Bank lines from Coding Engine, Xero, and SleekBooks land in SleekBooks (ERPNext), can be reconciled or unreconciled, including multi-currency and cash-coding paths, so the ledger matches bank reality. |
| **Entry Point / Surface** | Backend **sleek-erpnext-service** under `POST`/`GET /erpnext/*` (consumed by integrations and internal tools—not a single Sleek App screen in this repo). |
| **Short Description** | Creates and submits **Bank Transaction** documents in ERPNext from generic saves, CE (Coding Engine) document payloads, Xero bank lines, and SleekBooks-native payloads; lists and inspects transactions by company, date, status, invoice, or `transaction_id`; runs CE-driven reconciliation via Frappe `reconcile_vouchers` (with optional FX journal paths and payment entry creation from CE), Xero reconciliation, programmatic **revert** of CE reconciliation (unlink PEs, cancel/delete entries, HK-specific cleanup of remaining PEs), multi-currency reconciliation checks, **cash coding** via custom Frappe API, and **unreconcile** via `sleek.api.unreconcile_bank_transaction`. Publishes CE invoice and reconciliation outcome events to Kafka (`DataStreamerService`). |
| **Variants / Markets** | SG (default timezone handling for prior-day bank pull), HK (`PLATFORM` branch for extra payment-entry cleanup on revert); UK, AU — Unknown |
| **Dependencies / Related Flows** | **ERPNext/Frappe** (`ERPNEXTBASEURL`, `ERPNEXTOKEN`): `Bank Transaction`, `Company`, `Payment Entry`, `Journal Entry`, bank reconciliation tool methods, `sleek.api.cash_coding_bank_transactions`, `sleek.api.unreconcile_bank_transaction`; **Kafka** via `DataStreamerService` (`CESleekBooksInvoiceDoneEvent`, `CESleekBooksInvoiceFailedEvent`, `ReconciliationDoneEvent`, `ReconciliationFailedEvent`); **SleekAuditor** for unrelated COA audit paths in the same service. Upstream: CE publish pipeline, Xero migration/sync, SleekBooks operators. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None for these controller/service paths — bank and company resolution use ERPNext REST APIs; a `Companies` Mongoose schema exists on the module but is not used by `ErpnextService` for these flows. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `ErpnextController` registers **two** `@Post('/check-multi-currency-reconcile')` handlers (second shadows the first—likely unintended). Several `@ApiOperation` summaries duplicate unrelated Xero invoice text. Whether end-user-facing UI maps 1:1 to these routes is out of scope for this repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/erpnext/erpnext.controller.ts` (`@Controller('erpnext')`):**
  - **Create / ingest bank transactions:** `POST /create-bank-transactions` → `createBankTransactions`; `POST /create-ce-bank-transactions` → `createBankTransactionsFromCE`; `POST /create-xero-bank-transaction` → `createBankTransactionFromXero`; `POST /submit-xero-bank-transaction` → `submitBankTransactionFromXero`; `POST /create-bank-transaction-sb` (`M2MAuthGuard`) → `createBankTransactionForSB`.
  - **CE reconciliation / payment:** `POST /create-ce-payment-entry` → `createPaymentEntryFromCE`; `POST /reconcile-ce-bank-transactions` → `reconcileBankTransactionFromCE`; `POST /revert-ce-reconciliation` → `revertReconciliation`.
  - **Xero reconciliation / FX:** `GET /reconcile-xero-bank-transaction` → `reconcileBankTransFromXero`; `POST /check-multi-currency-reconcile` → `checkMulticurrencyReconcillation` and (duplicate route) `createTransferFromXero`.
  - **Inspect state:** `GET /get-bank-transactions/:companyUEN`, `GET /get-previous-day-bank-transactions`, `GET /get-bank-transactions-by-invoice`, `GET /check-bank-transaction`, `GET /check-bank-transaction-full`, `GET /get-transaction/:type`, `GET /get-bank-transactions-count/:type` (M2M), `POST /delete-doc` (uses `getTransactionsById` by `transaction_id`), etc.
  - **Cash coding / unreconcile:** `POST /cash-coding` (`M2MAuthGuard`) → `cashCodingSBBankTransactions`; `POST /unreconcile-bank-transaction` (`M2MAuthGuard`) → `unreconcileBankTransaction`.

- **`src/erpnext/erpnext.service.ts`:**
  - **ERPNext HTTP:** `frappe.desk.form.save.savedocs`, `api/resource/Bank Transaction`, `frappe.desk.form.load.getdoc` (`checkBankTransactionFULL`), `erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.reconcile_vouchers` (`reconcileVouchers`, `reconcileBankTransFromXero`).
  - **CE:** `createBankTransactionsFromCE` builds draft Bank Transaction, optional attachment processing, publishes `CESleekBooksInvoiceDoneEvent` / `CESleekBooksInvoiceFailedEvent`; `reconcileBankTransactionFromCE` handles FX journal branch (`createJournalEntryFXDifference`), `createPaymentEntryFromCE` when needed, `reconcileVouchers`, `assignTagToSB`, publishes `ReconciliationDoneEvent` / `ReconciliationFailedEvent`; `revertReconciliation` unlinks payment entries, updates bank transaction, cancels/deletes PEs, `cancelAndDeleteRemainingPaymentEntriesForRevert` when `PLATFORM === HK`.
  - **Xero:** `createBankTransactionFromXero` (SPEND/RECEIVE mapping, `transaction_id`), `submitBankTransactionFromXero`, `checkMulticurrencyReconcillation` (splits allocated/unallocated across payment_entries), `createTransferFromXero`, `reconcileBankTransFromXero`.
  - **SleekBooks:** `createBankTransactionForSB` then `submitBankTransactionFromXero` for submit; `getTransactionsById` filters ERPNext `Bank Transaction` by `transaction_id`.
  - **Cash coding / unreconcile:** `cashCodingSBBankTransactions` → `api/method/sleek.api.cash_coding_bank_transactions`; `unreconcileBankTransaction` → `sleek.api.unreconcile_bank_transaction`.
  - **Company resolution:** `getCompaniesByFilter` uses ERPNext `Company` API (registration filter), not MongoDB in this service.

- **`src/guard/erpnext-auth.guard.ts`:** Webhook signature guard (`FRAPPE_WEBHOOK_SECRET`) — not applied on the listed `erpnext` controller routes in the read scope; bank routes use default or `M2MAuthGuard` where annotated.

- **`src/erpnext/erpnext.module.ts`:** Registers `Companies` Mongoose schema and Kafka listeners (`InvoiceListener`, `ReconciliationListener`); bank flows in `ErpnextService` are primarily ERPNext + `DataStreamerService`.
