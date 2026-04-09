# Review reconciliation status

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review reconciliation status |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User |
| **Business Outcome** | Users can see whether a document’s bank lines are aligned with Coding Engine reconciliation state and with SleekBooks before deciding to match, reconcile, or troubleshoot. |
| **Entry Point / Surface** | Sleek bookkeeping experience that calls the Coding Engine reconciliation API (document-scoped reads). Exact in-app navigation is not defined in these handlers; surface is the authenticated reconciliation status endpoints below. |
| **Short Description** | Exposes document-level reconciliation records and, for SleekBooks-backed checks, per-transaction status: coding-engine reconciliation line status vs SleekBooks document status, reconciliation link analysis (cash-coded via journal entry vs document-reconciled), duplicate-match warnings, and aggregate summaries. A separate route returns the stored reconciliation status by reconciliation id; another returns a lean detailed payload (status, flags, reconcile entries, primary bank transaction). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Downstream read: SleekBooks bank transaction API (`getBankTransactionById`) for live SB status and payment-entry shape. Upstream data: `reconciliations` document keyed by `document_id`, including `ml_reconciliation_results.bank_transactions` and `reconcile_entries`. Related: ML reconciliation pipeline and listener docs; manual reconcile / match flows that consume the same reconciliation aggregate. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (Mongoose `Reconciliation` model on `CODING_ENGINE`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET reconciliation/document/:documentId` (`getReconciliationByDocumentId`) has no `AuthGuard` in the controller—confirm whether this is intentionally public or should be locked down. Product-specific UI path for “before or after matching” is not stated in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/reconciliation/reconciliation.controller.ts`**
  - `GET document/:documentId/get-bank-transaction-status-in-sb` — `@UseGuards(AuthGuard)`; `@ApiOperation` describes retrieving bank transaction status from SleekBooks and reconciliation type flags (`is_cash_coded`, `is_document_reconciled`). Delegates to `reconciliationService.getBankTransactionStatusInSB(documentId)`.
  - `GET :id/status-check` — `@UseGuards(AuthGuard)`; `checkReconciliationStatus` → `reconciliationService.checkReconciliationStatus(id)` (returns stored `ReconciliationStatus` from Mongo by reconciliation `_id`).
  - `GET :documentId/detailed-status` — `@UseGuards(AuthGuard)`; `@ApiResponse` type `ReconciliationStatusResponseDto`; `getDetailedReconciliationStatus` → `reconciliationService.getDetailedReconciliationStatus(documentId)`.
  - `GET document/:documentId` — `getReconciliationByDocumentId` → full reconciliation document lookup (no guard on this route in controller).

- **`src/reconciliation/reconciliation.service.ts`**
  - `getBankTransactionStatusInSB`: loads reconciliation by `document_id`; iterates `ml_reconciliation_results.bank_transactions`; for each id calls `sleekbooksService.getBankTransactionById`; when SB shows `Reconciled`, calls `checkBankTransactionReconciliationLinks` to compute `reconciliation_links`, `has_duplicate_match`, `reconciliation_type`, `is_cash_coded`, `is_document_reconciled`; returns `reconciliation_id`, `document_id`, per-transaction rows, `total_transactions`, `status_summary`.
  - `checkBankTransactionReconciliationLinks`: finds other reconciliations referencing the same bank transaction id; inspects `payment_entries[0].payment_document` for `Journal Entry` vs invoice/payment types to set cash-coded vs document-reconciled flags (`ReconciliationType`).
  - `checkReconciliationStatus`: `reconciliationModel.findById` → returns `status`.
  - `getDetailedReconciliationStatus`: `findOne({ document_id })` sorted by `updatedAt` desc; returns `status`, `reconciliation_id`, `document_id`, `auto_reconcile`, `reconciled_from_script`, `reconcile_entries`, `bank_transaction`.

- **`src/reconciliation/models/reconciliation.schema.ts`**
  - Fields supporting the above: `document_id`, `company_id`, `status`, `auto_reconcile`, `reconciled_from_script`, `bank_transaction`, `reconcile_entries`, `ml_reconciliation_results`, `has_pending_refresh_match`.

- **`src/reconciliation/dto/reconciliation-status.dto.ts`**
  - `ReconciliationStatusResponseDto`: documents API shape for detailed status (`status`, `reconciliation_id`, `document_id`, `auto_reconcile`, `reconciled_from_script`, `reconcile_entries`, optional `bank_transaction`).

- **`src/reconciliation/reconciliation.module.ts`**
  - `MongooseModule.forFeature` registers `Reconciliation` on `DBConnectionName.CODING_ENGINE`.
