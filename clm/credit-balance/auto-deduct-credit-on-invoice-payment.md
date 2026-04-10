# Auto-deduct Credit on Invoice Payment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Auto-deduct Credit on Invoice Payment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Automatically reduces the amount a customer owes on an invoice by consuming their available credit balance at payment time, ensuring credits are applied without manual intervention and every deduction is permanently audited. |
| **Entry Point / Surface** | No direct UI surface — triggered internally by `invoice.service.ts` during `markCouponAndCreditBalanceAsUsed()` when an invoice is confirmed paid, and during `createDowngradeInvoiceFromCreditNote()` for subscription downgrade flows. |
| **Short Description** | When an invoice is processed for payment, the system checks whether any line items carry a `creditBalanceDiscount`. If the total discount is non-zero, it atomically deducts that amount from the company's credit balance record and writes an audited `CreditBalanceTransaction` (type `deduct`) linked to the invoice and triggering user. Idempotency is enforced: if a transaction already exists for the same invoice ID, the deduction is silently skipped. |
| **Variants / Markets** | Unknown (no market-gating logic found in code) |
| **Dependencies / Related Flows** | Invoice payment confirmation flow (`markCouponAndCreditBalanceAsUsed`); Subscription downgrade flow (`createDowngradeInvoiceFromCreditNote`); Invoice line-item calculation (`getCreditBalanceAmountForInvoice` — caps credit discount to invoice total); Manual credit management (Add/Deduct via `POST /credit-balances`); Credit Balance admin UI (`manage-customer-credit-balances`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `creditbalances` (one balance record per company), `creditbalancetransactions` (per-deduction audit log, indexed on `invoiceId` and `companyId`) — both in `SleekPaymentDB` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) The full call chain that triggers `markCouponAndCreditBalanceAsUsed` (i.e., the payment-confirmed webhook or controller) was not traced — confirm the exact trigger event. (2) Rollback/compensation logic (revert credit refund on deduction failure) is implemented only in the downgrade path; unclear whether the standard payment path has similar safeguards. (3) Currency is not explicit in deduction logic — verify multi-currency or per-company currency handling. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `credit-balance/services/credit-balance.service.ts:91` — `deductCreditBalance(companyId, amount, description, userId, invoiceId, reason?)`: looks up existing balance, checks for prior transaction on same `invoiceId` (idempotency guard), validates sufficient balance, updates `creditbalances.balance` via `roundUp(existing - amount)`, then creates a `CreditBalanceTransaction` with `actionType: deduct`.
- `credit-balance/services/credit-balance.service.ts:137` — `getCreditBalanceAmountForInvoice(invoiceId, companyId?)`: returns 0 for onboarding invoices (no `companyId`); returns existing transaction amount if already deducted (idempotency read path); otherwise returns full `creditbalances.balance` as the available discount ceiling.
- `invoice/services/invoice.service.ts:2326` — `markCreditBalanceAsUsed(invoice)`: sums `item.creditBalanceDiscount` across all line items; calls `deductCreditBalance` only when total > 0.
- `invoice/services/invoice.service.ts:2341` — `markCouponAndCreditBalanceAsUsed(invoice)`: orchestrates both coupon and credit balance consumption after payment confirmation; errors are propagated after logging.
- `invoice/services/invoice.service.ts:800–828` — `createDowngradeInvoiceFromCreditNote`: calls `deductCreditBalance` after invoice creation; includes compensating transaction (reverts refunded credit) if deduction subsequently fails.
- `invoice/services/invoice.service.ts:1616` — `getCreditBalanceAmountForInvoice` called during invoice discount line-item calculation to cap the `creditBalance` discount type to available balance.
- `credit-balance/models/credit-balance-transaction.scheme.ts` — `CreditBalanceTransaction` schema: fields `companyId`, `creditBalanceId`, `userId`, `userEmail`, `invoiceId` (optional, indexed), `amount`, `actionType` (enum: `add` | `deduct`), `accountType` (enum: `general` | `sleek_internal`), `description`, `reason`; virtual populate of `invoice` via `Invoice` ref.
- `credit-balance/models/credit-balance.schema.ts` — `CreditBalance` schema: fields `companyId` (indexed), `balance`.
- `credit-balance/controllers/credit-balance.controller.ts` — `POST /credit-balances` (`@Auth()`) for manual add/deduct; `GET /credit-balances/:companyId` to retrieve balance + full transaction history. The auto-deduction path is **not** exposed via a controller endpoint — it is called directly as a service-to-service call within `invoice.service.ts`.
- `credit-balance/repositories/credit-balance-transaction.repository.ts` — extends `BaseRepository<CreditBalanceTransaction>`, bound to `SleekPaymentDB`.
- `credit-balance/repositories/credit-balance.repository.ts` — extends `BaseRepository<CreditBalance>`, bound to `SleekPaymentDB`.
