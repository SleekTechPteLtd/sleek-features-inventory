# Unreconcile matched ledger transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Unreconcile matched ledger transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User |
| **Business Outcome** | Users can undo a wrong match from the ledger-transaction context: the bank line returns to pending, the document link is cleared, and full reconciliation rollback runs so books and downstream state stay consistent. |
| **Entry Point / Surface** | Coding Engine HTTP API: `POST /ledger-transactions/:ledger_transaction_id/unreconcile` with JSON body `{ document_id }`. Requires `AuthGuard` and `CompanyAccessGuard`. Consumed by apps that surface Sleek Match / ledger transaction UIs; exact Sleek App path is not defined in these files. |
| **Short Description** | Validates the ledger row is `under_review` and that the body `document_id` matches the linked document, then sets `document_upload_status` to `pending` and clears `document_id`. Calls `revertReconciliationByDocumentId` so SleekBooks links are undone, the document returns to `in_books` with `reconciliation_id` cleared, ML bank-transaction rows reset, reconciliation goes to `PENDING`, and events/auditor run. If reconciliation revert fails, the ledger transaction is restored to its prior state. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Downstream**: same `revertReconciliation` / `revertReconciliationByDocumentId` stack as [Revert reconciliation](../reconciliation/revert-reconciliation.md) — SleekBooks `revert-ce-reconciliation`, `DOCUMENT_UNRECONCILED` events, Sleek Auditor, `bank_transactions` ML status reset. **Related**: customer match accept/reject (`customerUpdateMatchStatus`) moves transactions to `under_review`; this flow reverses that slice for the ledger row plus full reconciliation revert. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `ledger_transactions` (`document_upload_status`, `document_id` unset); `reconciliations`; `documentdetailevents` (documents: status, `reconciliation_id`); ML reconciliation bank transaction statuses updated via reconciliation update |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `revertReconciliation` audit fields use `user?.first_name` / `last_name`; this route builds `UserDetails` with `name` and `email` but not `first_name`/`last_name` — confirm whether auditor name fields are intentionally partial. ApiOperation text mentions “background” revert; implementation is synchronous `await`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/ledger-transaction/ledger-transaction.controller.ts`**
  - `POST :ledger_transaction_id/unreconcile` — `@UseGuards(AuthGuard, CompanyAccessGuard)`; body `UnreconcileLedgerTransactionDto` (`document_id`); builds `UserDetails` from `request.user`; calls `ledgerTransactionService.unreconcileLedgerTransaction(ledger_transaction_id, document_id)` then `reconciliationService.revertReconciliationByDocumentId(document_id, userDetails)`; on error, `restoreLedgerTransactionState(ledger_transaction_id, previousState)` and rethrows.

- **`src/ledger-transaction/ledger-transaction.service.ts`**
  - `unreconcileLedgerTransaction`: loads by `ledger_transaction_id`; `NotFoundException` if missing; `BadRequestException` unless `document_upload_status === UNDER_REVIEW`; `BadRequestException` if body `document_id` does not match `transaction.document_id`; `updateOne` with `$set` `document_upload_status: PENDING`, `$unset` `document_id`; returns `previousState` for rollback.
  - `restoreLedgerTransactionState`: `$set` prior `document_upload_status` and `document_id`.

- **`src/ledger-transaction/dto/ledger-transaction.dto.ts`**
  - `UnreconcileLedgerTransactionDto`: required string `document_id`.

- **`src/ledger-transaction/models/ledger-transaction.schema.ts`**
  - Collection `ledger_transactions`.

- **`src/reconciliation/reconciliation.service.ts`**
  - `revertReconciliationByDocumentId(document_id, user?)`: finds latest `RECONCILED` reconciliation for document; delegates to `revertReconciliation` (SleekBooks revert when `payment_entry_id`, document update, events, ML statuses, reconciliation `PENDING`, auditor). See existing revert-reconciliation inventory for full method list.

- **Tests**: search `unreconcileLedgerTransaction` / `unreconcile` in `src/ledger-transaction/*.spec.ts` if present for contract coverage.
