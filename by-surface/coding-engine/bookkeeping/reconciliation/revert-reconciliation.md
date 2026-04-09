# Revert reconciliation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Revert reconciliation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Lets operators roll back a bank–document match when it was wrong or must be undone, restoring the document and reconciliation record to a state where matching can be redone without leaving incorrect SleekBooks links. |
| **Entry Point / Surface** | Coding Engine HTTP API under `reconciliation` — `POST /reconciliation/:reconciliationId/revert` (authenticated user context for audit) and `POST /reconciliation/document/:documentId/revert` (revert latest reconciled row for that document). Consumed by internal tooling / apps that call the Coding Engine; exact Sleek App navigation is not defined in these files. |
| **Short Description** | By reconciliation id, loads the reconciliation, optionally calls SleekBooks to undo the ledger link (`revert-ce-reconciliation`), resets the document to `in_books`, clears `reconciliation_id`, republishes unreconciled events, resets ML bank-transaction statuses to `NEW`, and sets the reconciliation back to `PENDING`. By document id, finds the latest `RECONCILED` reconciliation for that document and delegates to the same path. Success and failure are written to Sleek Auditor. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **SleekBooks**: HTTP `POST …/erpnext/revert-ce-reconciliation` with bank transaction, payment entry, invoice, voucher type (journal vs payment entry for receipts). **Events**: `DOCUMENT_UNRECONCILED` published for document and reconciliation payloads via `EventUtils`. **Sleek Auditor**: `insertLogsToSleekAuditor` on success and failure. **Related**: `ledger-transaction` controller also invokes `revertReconciliationByDocumentId` for flows that unlink documents from ledger context. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (Mongoose default for `Reconciliation` model), `documentdetailevents` (documents: status `in_books`, `$unset` `reconciliation_id`, optional `is_auto_reconcile_reviewed` when prior method was auto) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST …/document/:documentId/revert` does not pass the authenticated user into `revertReconciliationByDocumentId`, so the service falls back to `SYSTEM_USER` for the nested `revertReconciliation` audit fields — confirm whether operator attribution is intentional for that route. Market-specific rules not visible in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/reconciliation/reconciliation.controller.ts`**
  - `POST :reconciliationId/revert` — `@UseGuards(AuthGuard)`; builds `userDetails` from `request.user`; `reconciliationService.revertReconciliation(reconciliationId, userDetails)`; success code `SUCCESS_CODES.RECONCILIATION.REVERT_RECONCILIATION`.
  - `POST document/:documentId/revert` — `@UseGuards(AuthGuard)`; `@ApiOperation({ summary: 'Revert reconciliation by document ID' })`; `revertReconciliationByDocumentId(documentId)` only (no user object passed).

- **`src/reconciliation/reconciliation.service.ts`**
  - `revertReconciliation(reconciliationId, user?)`: `findById` reconciliation; validates `document_id`, `bank_transaction.id`; maps receipt → `VoucherType.JOURNAL_ENTRY`, else payment entry; if `payment_entry_id`, `sleekbooksService.revertReconciliation(bankTransactionId, paymentEntryId, invoiceId, voucherType)`; updates document `$set` status `DocumentStatus.IN_BOOKS`, `$unset` `reconciliation_id`, may set `is_auto_reconcile_reviewed` when `reconciliation_method === ReconciliationMethod.AUTO`; `fetchAndPublishDocumentEvent` / `fetchAndPublishReconciliationEvent` with `CodingEngineEventType.DOCUMENT_UNRECONCILED`, caller `EventCaller.RECONCILIATION_SERVICE.revertReconciliation`; resets ML `bank_transactions` to `ReconciliationBankTransactionStatus.NEW`; `reconciliationModel.updateOne` clears `bank_transaction`, `payment_entry_id`, sets `status` `ReconciliationStatus.PENDING`, `reconciled_from_script: false`; `sleekAuditorService.insertLogsToSleekAuditor` success/error.
  - `revertReconciliationByDocumentId(document_id, user?)`: `findOne` `{ document_id, status: RECONCILED }` sort `updatedAt: -1`; if missing, handles already-`PENDING` as no-op; else error; calls `revertReconciliation(reconciliation._id.toString(), userDetails)` with `userDetails = user || SYSTEM_USER`.

- **`src/sleekbooks/sleekbooks.service.ts`**
  - `revertReconciliation`: `POST ${SLEEKBOOKS_BASE_URL}/erpnext/revert-ce-reconciliation` with `bankTransactionId`, `paymentEntryId`, `invoiceId`, `voucherType`.

- **`src/reconciliation/models/reconciliation.schema.ts`**
  - `Reconciliation` fields used: `document_id`, `company_id`, `invoice_id`, `invoice_type`, `payment_entry_id`, `bank_transaction`, `ml_reconciliation_results`, `reconciled_from_script`, timestamps (`updatedAt` for latest reconciled lookup).

- **Tests**: `test/reconciliation/service/revertReconciliation.spec.ts`, `test/reconciliation/controller/reconciliation.controller.spec.ts`, `test/sleekbooks/service/revertReconciliation.spec.ts`.
