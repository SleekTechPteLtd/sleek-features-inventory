# Update bank transaction match status during reconciliation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Update bank transaction match status during reconciliation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (bookkeeping / reconciliation operators via authenticated session) |
| **Business Outcome** | Operators can set each ML-suggested bank line’s reconciliation status (including rejection) and optional rejection semantics so match state, audit trail, and downstream events stay aligned with the real reconciliation decision. |
| **Entry Point / Surface** | Sleek bookkeeping / Coding Engine client — authenticated `PUT /reconciliation/update-status` (exact in-app menu path not defined in these backend files). |
| **Short Description** | Accepts one or more bank transaction ids for a document, updates embedded `ml_reconciliation_results.bank_transactions` status in the reconciliation record, optionally records manual rejection source and Sleek Auditor logs when the action is reject, then publishes a bulk reconciliation event so listeners stay in sync. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Downstream: `fetchAndPublishBulkReconciliationEvent` with `CodingEngineEventType.DOCUMENT_RECONCILED` (Kafka). Optional: `SleekAuditorService.insertLogsToSleekAuditor` on reject path and on errors. Upstream context: ML reconciliation results already stored per document. Related reads: `getDetailedReconciliationStatus`, `getBankTransactionStatusInSB`. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (MongoDB — `Reconciliation` model; updates `ml_reconciliation_results.bank_transactions.$[elem].status` and conditional `rejection_source`; reads `document_id` for company audit context via `fetchCompanyDataForAuditLog`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/reconciliation/reconciliation.controller.ts`**
  - `PUT reconciliation/update-status` — `@UseGuards(AuthGuard)`; body `UpdateBankTransactionStatusRequestDto`; passes `transaction`, authenticated `userDetails`, and optional `action` to `reconciliationService.updateBankTransactionStatus`.

- **`src/reconciliation/dto/reconciliation-status.dto.ts`**
  - `BankTransactionStatusUpdateDto`: `ids[]`, `document_id`, `status`.
  - `UpdateBankTransactionStatusRequestDto`: nested `transaction` plus optional `action` typed as `RejectionSourceActionType` (`cancel` | `reject`).

- **`src/reconciliation/reconciliation.service.ts` — `updateBankTransactionStatus`**
  - Validates at least one id; builds user-facing messages for “marked as rejected” copy.
  - `action === RejectionSourceActionType.REJECT`: `updateMany` with `$set` status and `rejection_source: RejectionSource.MANUAL`; calls `sleekAuditorService.insertLogsToSleekAuditor` with event `Bank Transaction Rejection` after `fetchCompanyDataForAuditLog(document_id)`.
  - Else: `updateMany` sets status and `$unset` `rejection_source` on matching array elements.
  - `arrayFilters: [{ 'elem.id': { $in: ids } }]`, query matches `document_id` and bank transaction ids under `ml_reconciliation_results.bank_transactions`.
  - On success: `fetchAndPublishBulkReconciliationEvent` with `CodingEngineEventType.DOCUMENT_RECONCILED`, projection including `ml_reconciliation_results`, `status`, `_id`, `EventCaller.RECONCILIATION_SERVICE.updateBankTransactionStatus`.
  - On error: optional error audit log to Sleek Auditor when `document_id` present; rethrows.

- **`src/reconciliation/models/reconciliation.schema.ts`**
  - `BankTransactions.status` uses `ReconciliationBankTransactionStatus`; optional `rejection_source` with `RejectionSource` enum — aligns with manual updates.

- **`src/reconciliation/interface/reconciliation.interface.ts`**
  - `RejectionSourceActionType` enum: `CANCEL`, `REJECT`.

- **`test/reconciliation/service/updateBankTransactionStatus.spec.ts`**
  - Service-level tests for `updateBankTransactionStatus` (mocked `Reconciliation` model and Sleek Auditor).
