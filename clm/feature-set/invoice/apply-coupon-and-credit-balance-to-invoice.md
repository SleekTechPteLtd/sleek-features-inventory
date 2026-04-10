# Apply Coupon and Credit Balance to Invoice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Customer Lifecycle Management |
| **Feature Name** | Apply Coupon and Credit Balance to Invoice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | Reduces the amount due on an invoice by applying a discount coupon and/or the customer's available credit balance, enabling flexible pricing, referral incentives, and retention discounts at checkout. |
| **Entry Point / Surface** | Sleek App > Billing > Invoice payment flow — POST /invoices/apply-coupon-and-credit-balance |
| **Short Description** | Accepts an invoice ID, an optional coupon code, and a flag to apply credit balance. Validates coupon eligibility (type, usage limits, applicable invoice scope), distributes coupon and credit-balance discounts proportionally across line items, enforces Stripe minimum payment amount, persists updated totals to the invoice, and syncs the revised discounts to Xero if the invoice is already linked to an external Xero record. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Coupon management, Credit balance management, Invoice payment flow, Xero invoice sync, Stripe minimum payment enforcement |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | invoices, coupons, couponusages, services, creditbalances |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | The `POST /invoices/apply-coupon-and-credit-balance` endpoint has no `@Auth()` guard in the controller — unclear if intentionally public or if auth is enforced upstream (e.g. API gateway or middleware). Markets/jurisdictions are unknown; no region-specific logic is visible in this flow. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `invoice/controllers/invoice.controller.ts` — `POST /invoices/apply-coupon-and-credit-balance` (no `@Auth()` guard), calls `InvoiceService.applyCouponAndCreditBalance(payload)`
- Request DTO: `ApplyCouponAndCreditBalanceRequestDto` — fields: `invoiceId: string`, `couponCode: string`, `isApplyCreditBalance: boolean`
- Response DTO: `ApplyCouponAndCreditBalanceResponseDto` — fields: `invoice: Invoice`, `appliedCouponResult?: { discountAmount, couponCode }`

### Service logic (`invoice/services/invoice.service.ts`, line 2138)
1. **Fetch invoice** — `invoiceRepository.findById(invoiceId)` → 404 if not found.
2. **Persist selections** — `invoiceRepository.updateById(invoiceId, { isApplyCreditBalance, couponCode })`.
3. **Validate coupon** — `checkCouponCode({ invoiceId, couponCode })`:
   - Looks up coupon by code in `coupons` collection.
   - Checks `maxUsage` against `couponusages` count.
   - Enforces `applicableInvoiceType`: `onboardingOnly` (no prior paid invoices for company), `renewalOnly` (at least one prior paid invoice), `allInvoices`.
   - Referral-program coupons are always onboarding-only.
   - On failure, clears `couponCode` from the invoice and re-throws.
4. **Discount allocation** — `handleInvoiceDiscountsAllocation(invoice, isApplyCreditBalance, couponCode)`:
   - Resets existing coupon/credit-balance discounts to zero (`resetCouponAndCreditBalance`).
   - Processes discounts sequentially (coupon first, then credit balance).
   - **Coupon discount**: supports `flat` (fixed amount) and `percentage` calculation types; distributes proportionally across eligible line items.
   - **Credit balance discount**: distributes proportionally across all line items by line-amount weight.
   - Enforces Stripe minimum payment amount (`stripeService.getMinimumPaymentAmount()`); retries allocation once if total falls below minimum.
   - Persists updated `items`, `subTotal`, `totalAmount`, `totalTax`, `totalDiscount`, `couponCode`, `isApplyCreditBalance` to the invoice.
   - **Xero sync**: if invoice has `externalId`, calls `xeroService.updateInvoice()` with revised line-item discount amounts (`applyInvoiceDiscountsToXeroInvoice`).
5. **Return** — re-fetches invoice with `items.service` populated and returns alongside `appliedCouponResult`.

### External system calls
- **Stripe** — `stripeService.getMinimumPaymentAmount()` to cap discounts.
- **Xero** — `xeroService.getInvoiceFromIDs()` + `xeroService.updateInvoice()` to sync line-item discounts.

### MongoDB collections
- `invoices` — read and updated (items, totals, couponCode, isApplyCreditBalance).
- `coupons` — read to validate coupon code and configuration.
- `couponusages` — counted to enforce `maxUsage` limits.
- `services` — populated on the final invoice fetch (`items.service`).
- `creditbalances` — read via `CreditBalanceService` to determine available balance.
