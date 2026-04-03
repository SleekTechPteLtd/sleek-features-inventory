# Apply Core Engine bank reconciliation to ERPNext

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply Core Engine bank reconciliation to ERPNext |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When Core Engine decides a bank line matches a voucher, SleekBooks (ERPNext) reflects that match: payment documents are created or linked, the bank transaction is reconciled in the bank reconciliation tool, and other systems learn whether reconciliation succeeded so they can continue workflows. |
| **Entry Point / Surface** | Event-driven: Kafka subscriber on `ReconciliationCreatedEvent` (`ReconciliationListener`). Not an end-user screen; triggered by Core Engine publishing reconciliation intent. |
| **Short Description** | The listener forwards payload data to `ErpnextService.reconcileBankTransactionFromCE`. The service creates or resolves a payment entry (including an FX journal path for supported receipt-style document types), calls ERPNext’s `reconcile_vouchers` for the bank transaction, assigns `auto-match` or `auto-reconciled` tags on the bank line (and on new payment entries when created), and publishes `ReconciliationDoneEvent` or `ReconciliationFailedEvent` for downstream consumers. |
| **Variants / Markets** | HK (partial): `createPaymentEntryFromCE` applies HK-only same-currency bank-fees threshold behaviour when creating payment entries from sales/purchase invoices; other markets Unknown |
| **Dependencies / Related Flows** | **Upstream**: Core Engine reconciliation pipeline producing `ReconciliationCreatedEvent`. **ERPNext/Frappe**: `bank_reconciliation_tool.reconcile_vouchers`, `savedocs` for payment entries and journal entries, `tag.add_tag`. **Downstream**: Consumers of `ReconciliationDoneEvent` and `ReconciliationFailedEvent` (via `dataStreamerService.publish`). Related: manual unreconcile (`unreconcileBankTransaction`), Xero reconciliation path (`reconcileBankTransFromXero`). |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in this flow — state is read and written through ERPNext/SleekBooks HTTP APIs; events are published to Kafka. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact Kafka topic and consumer group configuration for `ReconciliationCreatedEvent` live in shared SDK/bootstrap; whether all markets use the same `auto_reconcile` semantics beyond HK-specific payment entry logic. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/kafka/listeners/reconciliation.listener.ts`**: `@SubscribeEvent(ReconciliationCreatedEvent.name)` → `onCEReconciliationCreated` logs the message and awaits `erpnextService.reconcileBankTransactionFromCE(message.data)`.
- **`src/kafka/events/reconciliation/reconciliation-created.event.ts`**: Payload shape includes `uen`, `transaction.id`, `reconcile_entry_id`, `invoice_id`, `invoice_type`, `bank_transaction`, `payment_entry_id`, `auto_reconcile`.
- **`src/erpnext/erpnext.service.ts` — `reconcileBankTransactionFromCE`**:
  - For `SUPPORTED_DOC_TYPES_FOR_BANK_TRANSACTION` (`direct_transaction`, `receipt`, `atm_withdrawal`, `deposit`): treats voucher as `Journal Entry`, may call `createJournalEntryFXDifference` (FX gain/loss journal); if a JE is created, reconciliation passes two journal vouchers (`invoice_id` and FX JE name); otherwise falls through with payment entry id.
  - For purchase/sales invoices without `payment_entry_id`: loads bank transaction → bank account → company account → `createPaymentEntryFromCE` (draft PE, submit via `savedocs`), reusing existing submitted PE when present.
  - Builds `payments` for `reconcileVouchers` (single PE or FX pair).
  - **`reconcileVouchers`**: POST `erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.reconcile_vouchers` with `bank_transaction_name` and stringified `vouchers`.
  - **`assignTagToSB`**: POST `frappe.desk.doctype.tag.tag.add_tag` on Bank Transaction with `RECONCILE_TAGS.autoReconciled` or `autoMatch` from `src/erpnext/erpnext.constants.ts`.
  - Success: `dataStreamerService.publish(ReconciliationDoneEvent, { id, reconcile_entry_id, payment_entry_id })`. Failure: `ReconciliationFailedEvent` with `error.message`.
- **`src/erpnext/erpnext.service.ts` — `createPaymentEntryFromCE`**: Also tags the new Payment Entry document with the same auto-match / auto-reconciled tags; includes HK-only `applySameCurrencyBankFeesThreshold` and optional bank-fees payment entry creation.
- **`src/kafka/events/reconciliation/reconciliation-done.event.ts`**, **`reconciliation-failed.event.ts`**: Outbound event payloads for success and failure.
