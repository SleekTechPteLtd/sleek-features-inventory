# Accept or reject ML reconciliation matches

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Accept or reject ML reconciliation matches |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Customers can confirm or dismiss machine-proposed bank-to-document matches so only intended pairings proceed to reconciliation, with access limited to their company’s data. |
| **Entry Point / Surface** | Sleek customer app — bank transaction / ML suggested-match review (exact navigation not defined in these files); API: `PUT …/reconciliation/customer/update-match-status` on acct-coding-engine. |
| **Short Description** | Authenticated users update a proposed ML match by ledger transaction id and document id: **accept** runs the same reconcile flow as manual reconciliation, then marks the ledger line under review in SleekBooks-facing state; **reject** marks the match rejected with manual rejection source, unlinks the document from the transaction so it can reappear for a new upload. Company ownership is enforced before any change. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: ML reconciliation results and `NEW` match rows on reconciliations. Downstream: `reconcileBankTransaction` (SleekBooks reconciliation), `ledgerTransactionDbService.updateByLedgerTransactionId` / `resetDocumentLink`, optional Sleek Auditor audit events. Related inventory: process ML reconciliation results (listener pipeline). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `reconciliations` (Reconciliation model, `ml_reconciliation_results.bank_transactions` status and `rejection_source`), `ledger_transactions` (company-scoped lookup and post-accept/reject updates) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none — product navigation path for the customer UI not evidenced in these three files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/reconciliation/reconciliation.controller.ts`**
  - `PUT customer/update-match-status` → `customerUpdateMatchStatus`.
  - Guards: `AuthGuard`, `CompanyAccessGuard` (company-scoped authorization).
  - Swagger: summary “Customer accept or reject a reconciliation match”; describes validation of company ownership and match state; responses 200 / 400 / 403 / 404.
  - Passes `CustomerUpdateMatchStatusDto`, builds `userDetails`, delegates to `ReconciliationService.customerUpdateMatchStatus` with `request.user`.

- **`src/reconciliation/dto/customer-match-status.dto.ts`**
  - `CustomerUpdateMatchStatusDto`: `ledger_transaction_id`, `document_id`, `action` enum `accept` | `reject`.
  - `CustomerUpdateMatchStatusResponseDto`: `success`, `message`, `ledger_transaction_id`, `new_status`.

- **`src/reconciliation/reconciliation.service.ts` — `customerUpdateMatchStatus`**
  - Loads ledger transaction via `ledgerTransactionDbService.findByLedgerTransactionId`; `NotFoundException` if missing.
  - If `user` present: `userAuthorizationService.assertCompanyAccess(user, ledgerTransaction.company_id)` — company match required.
  - Loads reconciliation where `document_id` matches and `ml_reconciliation_results.bank_transactions.id` equals `ledger_transaction_id`; `NotFoundException` if no row.
  - Requires embedded bank transaction `status === ReconciliationBankTransactionStatus.NEW`; else `ConflictException` (“no longer actionable”).
  - **Accept:** sets flow to `reconcileBankTransaction` with bank line fields from ML result; then `ledgerTransactionDbService.updateByLedgerTransactionId` with `document_upload_status: UNDER_REVIEW` and `document_id` (hides from customer view per comment).
  - **Reject:** `reconciliationModel.updateOne` with `$set` status `REJECTED` and `rejection_source: RejectionSource.MANUAL` on the array element; `ledgerTransactionDbService.resetDocumentLink(ledger_transaction_id)` so the transaction can show again for a new document.
  - Best-effort `sleekAuditorService.insertLogsToSleekAuditor` for “Customer Accepted Match” / “Customer Rejected Match”.

- **`src/reconciliation/models/reconciliation.schema.ts`**
  - `Reconciliation.ml_reconciliation_results.bank_transactions[]` holds `status`, `rejection_source`, and transaction fields used when accepting.

- **Connections:** `Reconciliation` and `LedgerTransaction` registered on `DBConnectionName.CODING_ENGINE` in `reconciliation.module.ts`; ledger schema uses collection `ledger_transactions`.
