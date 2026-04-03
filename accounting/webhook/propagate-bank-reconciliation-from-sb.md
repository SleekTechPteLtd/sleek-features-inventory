# Propagate bank reconciliation from SleekBooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Propagate bank reconciliation from SleekBooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When SleekBooks (ERPNext) reconciles or unreconciles a bank line against payment documents, downstream accounting and integrations receive rich events so ledgers, coding engine, and other consumers stay aligned with reconciliation state without polling ERPNext. |
| **Entry Point / Surface** | Server-to-server: `POST /webhook/document/reconcile-from-sb` on sleek-erpnext-service. Secured with `ERPNextAuthGuard` (`x-frappe-webhook-signature` must match `FRAPPE_WEBHOOK_SECRET`). Not an end-user screen; invoked when SB emits the bank-transaction reconciliation webhook payload. |
| **Short Description** | Accepts a `BankTransaction` payload. For **Reconciled**, requires `payment_entries`; for each entry, resolves **Payment Entry** documents via ERPNext `GET api/resource/Payment Entry/{id}` or builds a minimal reference payload for sales invoice, purchase invoice, or legacy manual journal types, then publishes `SleekErpnextServiceReconciledFromSbEvent` (bank transaction plus payment entry detail) via `DataStreamerService`. For **Unreconciled**, publishes `SleekErpnextServiceUnreconciledFromSbEvent` with the bank transaction. Other statuses or unsupported payment document types are skipped. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: SleekBooks / Frappe webhook caller supplying signed requests and `BankTransaction` body. **ERPNext HTTP API**: `ErpnextService.getPaymentEntryByID` for full Payment Entry documents. **Downstream**: Streamer/Kafka consumers of `SleekErpnextServiceReconciledFromSbEvent` and `SleekErpnextServiceUnreconciledFromSbEvent`. Related: Core Engine → ERPNext reconciliation (`reconcileBankTransactionFromCE`) flows the opposite direction; this path propagates SB-originated reconcile/unreconcile outward. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in this flow — state is read from ERPNext over HTTP; events are published via `DataStreamerService`; no MongoDB access in the webhook handlers reviewed. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which product component invokes this webhook in each environment (SB server action vs Frappe server script); exact Kafka topic names and consumer applications for the two SleekErpnextService events live outside this repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/webhook/webhook.controller.ts`**: `@Post('/document/reconcile-from-sb')`, `@ApiOperation({ summary: 'Webhook for document reconciliation in SB' })`, `@UseGuards(new ERPNextAuthGuard())`, `@ApiSecurity('basic')`, `@ApiHeader` for `x-frappe-webhook-signature`, body typed as `BankTransaction` → `webhookService.reconcileFromSB`.
- **`src/guard/erpnext-auth.guard.ts`**: Rejects missing signature; compares header to `process.env.FRAPPE_WEBHOOK_SECRET`.
- **`src/webhook/webhook.service.ts` — `reconcileFromSB`**:
  - Validates body; only processes `BankTransactionStatus.RECONCILED` or `UNRECONCILED`; otherwise returns `'skipped'`.
  - **Reconciled**: requires `payment_entries.length`; iterates `payment_entry` + `payment_document`. For `TRANSACTION_TYPES.payment_entry` calls `erpnextService.getPaymentEntryByID(paymentEntryId)`. For sales, purchase, or `manualjournal`, builds synthetic `{ data: { name, references: [{ reference_name, reference_doctype }] } }`. Unsupported `payment_document` → `'skipped'`. Publishes `SleekErpnextServiceReconciledFromSbEvent` with `bank_transaction: { id: bankTransaction.name, ...bankTransaction }` and `payment_entry_detail: paymentEntryDetails`.
  - **Unreconciled**: publishes `SleekErpnextServiceUnreconciledFromSbEvent` with `{ bank_transaction: bankTransaction }`.
  - Imports: `DataStreamerService` from `@sleek-sdk/common`.
- **`src/erpnext/erpnext.service.ts` — `getPaymentEntryByID`**: `GET ${baseURL}/api/resource/Payment Entry/${id}` with `Authorization` token; returns `response.data`.
- **`src/kafka/events/sleek-erpnext-service.reconciled-from-sb.event.ts`**: `DomainEvent<{ bank_transaction: object; payment_entry_detail: object }>`.
- **`src/kafka/events/sleek-erpnext-service.unreconciled-from-sb.event.ts`**: `DomainEvent<{ bank_transaction: object }>`.
- **`src/webhook/interface/bank-transaction.interface.ts`**: `BankTransaction` and `BankTransactionPayment` shapes including `status`, `payment_entries`, `payment_document`, `payment_entry`.
