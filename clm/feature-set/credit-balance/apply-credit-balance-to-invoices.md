# Apply Credit Balance to Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Apply Credit Balance to Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Automatically reduces the amount a customer owes on an invoice by consuming their available credit balance at payment time, ensuring credits are applied without manual intervention and every deduction is permanently audited. |
| **Entry Point / Surface** | No direct UI surface — triggered internally by `invoice.service.ts` during `markCouponAndCreditBalanceAsUsed()` when an invoice is confirmed paid, and during `createDowngradeInvoiceFromCreditNote()` for subscription downgrade flows. |
| **Short Description** | When an invoice is processed for payment, the system checks the company's available credit balance and deducts it from the invoice total. Idempotency is enforced via the `CreditBalanceTransaction` collection: if a transaction already exists for the same `invoiceId`, the deduction is silently skipped. The deducted amount is written as an audited transaction record linked to the invoice and triggering user. |
| **Variants / Markets** | Unknown (no market-gating logic found in code) |
| **Dependencies / Related Flows** | Invoice payment confirmation flow (`markCouponAndCreditBalanceAsUsed`); Subscription downgrade flow (`createDowngradeInvoiceFromCreditNote`); Invoice line-item discount calculation (`getCreditBalanceAmountForInvoice` — caps credit discount to invoice total); Manual credit management (Add/Deduct via `POST /credit-balances`); Credit balance admin UI (`manage-customer-credit-balances`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `creditbalances` (one balance record per company), `creditbalancetransactions` (per-deduction audit log, indexed on `invoiceId` and `companyId`) — both in `SleekPaymentDB` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) The exact upstream trigger for `markCouponAndCreditBalanceAsUsed` (payment-confirmed webhook or controller) was not fully traced — confirm the entry event. (2) Rollback/compensation logic on deduction failure is present in the downgrade path but not confirmed in the standard payment path. (3) Currency handling is implicit — verify multi-currency or per-company currency behaviour. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `credit-balance/services/credit-balance.service.ts:91` — `deductCreditBalance(companyId, amount, description, userId, invoiceId, reason?)`: looks up existing balance, checks for prior transaction on the same `invoiceId` (idempotency guard — returns early if found), validates sufficient balance, updates `creditbalances.balance` via `roundUp(existing - amount)`, then creates a `CreditBalanceTransaction` with `actionType: CreditBalanceActionType.deduct`.
- `credit-balance/services/credit-balance.service.ts:137` — `getCreditBalanceAmountForInvoice(invoiceId, companyId?)`: returns `0` for onboarding invoices (no `companyId`); returns the existing transaction `amount` if already deducted (idempotency read path); otherwise returns the full `creditbalances.balance` as the available discount ceiling.
- `credit-balance/services/credit-balance.service.ts:23` — `updateOrCreateCreditBalance(payload, req?)`: upserts the company's credit balance record and writes a corresponding `CreditBalanceTransaction` (action type `add` or `deduct` depending on sign of `payload.amount`). Used by the manual admin endpoint.
- `credit-balance/controllers/credit-balance.controller.ts:17` — `POST /credit-balances` (`@Auth()`) for manual add/deduct; `GET /credit-balances/:companyId` to retrieve balance + full transaction history. The auto-deduction path is **not** exposed via a REST endpoint — it is called as an internal service method within `invoice.service.ts`.
- `credit-balance/models/credit-balance-transaction.scheme.ts` — `CreditBalanceTransaction` schema: fields `companyId`, `creditBalanceId`, `userId`, `userEmail`, `invoiceId` (optional, indexed), `amount`, `actionType` (enum: `add` | `deduct`), `accountType` (enum: `general` | `sleek_internal`), `description`, `reason`; virtual populate of `invoice` via `Invoice` ref; indexes on `invoiceId` and `companyId`.
- `credit-balance/models/credit-balance.schema.ts` — `CreditBalance` schema: fields `companyId` (indexed), `balance`.
- `credit-balance/repositories/credit-balance-transaction.repository.ts` — extends `BaseRepository<CreditBalanceTransaction>`, bound to `SleekPaymentDB` via `@InjectModel(CreditBalanceTransaction.name, SleekPaymentDB)`.
- `credit-balance/repositories/credit-balance.repository.ts` — extends `BaseRepository<CreditBalance>`, bound to `SleekPaymentDB`.
