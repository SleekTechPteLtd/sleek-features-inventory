# Control customer visibility of ledger transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Control customer visibility of ledger transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Bookkeeper (hide/unhide via authenticated API); Customer (sees filtered lists when `app-origin` is customer) |
| **Business Outcome** | Operators can remove sensitive or in-progress SleekMatch bank lines from what the client sees in the customer app while keeping the full ledger transaction record for internal bookkeeping and audit. |
| **Entry Point / Surface** | Coding Engine REST API: `POST /ledger-transactions/:ledger_transaction_id/hide` and `POST /ledger-transactions/:ledger_transaction_id/unhide` (Bearer auth). Customer-facing Sleek flows that call ledger transaction list, download, totals, or filter counts with `app-origin: customer` inherit exclusion of hidden rows. Exact admin UI path is not in these handlers. |
| **Short Description** | Persists `is_hidden_from_customer`, `hidden_at`, and `hidden_by` on the ledger transaction. When requests are scoped to the customer app origin, MongoDB match queries exclude hidden transactions so they do not appear in listings, downloads, or filter counts; eligible totals are unchanged but pending totals omit hidden rows. Unhide clears visibility flags. Hide and unhide emit Sleek Auditor events for bank-account audit trails. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: authenticated user and company context from platform auth. Downstream: Sleek Auditor (`insertLogsToSleekAuditor`) for “SleekMatch Transaction Hidden/Unhidden” events with tags `bsm`, `sleekmatch`. Related: `getLedgerTransactionsForCompany`, download, `getFilterCounts`, and `getEligibleAndPendingTotalTransactionAmount` all use shared match logic or parallel rules for customer vs internal visibility. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `ledger_transactions` (fields `is_hidden_from_customer`, `hidden_at`, `hidden_by`; Mongoose `LedgerTransaction` on coding-engine DB) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Hide/unhide routes use `AuthGuard` only (no `CompanyAccessGuard` on those actions)—confirm intended role/tenant scoping vs other ledger routes. Product navigation for operators is not defined in controller code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/ledger-transaction/ledger-transaction.controller.ts`**
  - `POST :ledger_transaction_id/hide` — `@UseGuards(AuthGuard)`; `@ApiOperation` “Hide transaction from customer view”; delegates to `ledgerTransactionService.hideTransaction`.
  - `POST :ledger_transaction_id/unhide` — `@UseGuards(AuthGuard)`; `@ApiOperation` “Unhide transaction (make visible to customer)”; delegates to `ledgerTransactionService.unhideTransaction`.

- **`src/ledger-transaction/ledger-transaction.service.ts`**
  - `hideTransaction`: `findOne({ ledger_transaction_id })`; sets `is_hidden_from_customer = true`, `hidden_at`, `hidden_by` (actor `user._id`); `save()`; audit log event `SleekMatch Transaction Hidden` / action “hid a SleekMatch transaction from customer view” via `sleekAuditorService.insertLogsToSleekAuditor`.
  - `unhideTransaction`: clears flags; audit `SleekMatch Transaction Unhidden` / “made a SleekMatch transaction visible to customer”.
  - `buildLedgerTransactionMatchQuery`: when `appOrigin === AppOrigin.CUSTOMER`, adds `$and` with `$or` on `is_hidden_from_customer` — exclude `true`, allow missing field (legacy rows).
  - `getEligibleAndPendingTotalTransactionAmount` aggregation: `pending_total` branch excludes `is_hidden_from_customer: true` (eligible total logic does not use this field).
  - Enriched transaction mapping includes `is_hidden_from_customer` in API responses (`mapTransactionToResponse` path).

- **`src/ledger-transaction/models/ledger-transaction.schema.ts`**
  - Collection `ledger_transactions`: `is_hidden_from_customer` (default false), optional `hidden_at`, `hidden_by`.

- **`src/ledger-transaction/dto/ledger-transaction.dto.ts`**
  - `HideTransactionResponseDto` / `UnhideTransactionResponseDto`, `EnrichedLedgerTransactionResponseDto.is_hidden_from_customer`.
