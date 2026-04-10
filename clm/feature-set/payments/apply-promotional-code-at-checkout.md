# Apply Promotional Code at Checkout

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Apply promotional code at checkout |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client |
| **Business Outcome** | Lets clients redeem discount coupons at payment time, reducing the total amount charged for their order without requiring manual intervention from Sleek staff. |
| **Entry Point / Surface** | Sleek App > Payment > Order Summary panel (promo code input + Apply button); present in both the Incorporation and Subscription Renewal payment flows |
| **Short Description** | During checkout, clients enter a promo code in the Order Summary panel. Clicking "Apply" locks the coupon via `POST /coupons/lock` on the core API. If valid, the order summary refreshes to reflect the discounted total. Only one promo code per order is permitted; the input is disabled once a coupon line item appears in the charge breakdown. |
| **Variants / Markets** | SG (currency hardcoded to SGD in component) |
| **Dependencies / Related Flows** | Coupon management (admin CRUD via payment-api: `/coupons`); charge-amount recalculation (`handleAppliedCoupon` → `fetchChargeAmount`); Stripe credit-card payment; bank-transfer payment; GA ecommerce transaction tracking |
| **Service / Repository** | sleek-website (frontend), core API (`/coupons/lock`), payment-api (`payment-api.sleek.sg` — coupon admin CRUD) |
| **DB - Collections** | Unknown — coupon persistence is in the payment-api or core API backend; not visible from frontend code |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns `/coupons/lock` — core API or payment-api? Are there market-specific coupon restrictions beyond the SGD currency lock? Is the one-code-per-order limit enforced server-side as well as in the UI? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI component
- `src/components/payment/payment.js`
  - Promo code input field (`name="promo_code"`) rendered in the Order Summary panel (line 117–122)
  - Input disabled when `chargeAmount.items` already contains a `code === "coupon"` line (line 121) — one promo per order enforced client-side
  - `promoData.status === "locked"` switches icon from `tag` → `tick-circle` (line 112–116)
  - `handleClickApplyPromoCode` (line 204): calls `this.props.lockCoupon(promoCode)`, shows success/failure alert, then triggers `this.props.handleAppliedCoupon()` to refresh the charge total
  - Apply button disabled while loading, when input is empty, or when entered code matches already-applied code (line 125)

### Coupon lock API call (core API)
- `src/utils/api.js:781` — `lockCoupon(options)` → `POST ${getBaseUrl()}/coupons/lock`
- Called from `src/views/payments/index.js:110` with `{ company_id, code }` body (subscription renewal flow)
- Called from `src/views/incorporate/steps/payment-step.js:58` (incorporation flow)

### Charge amount refresh after coupon applied
- `src/views/payments/index.js:176` — `handleAppliedCoupon` wired to `this.fetchChargeAmount` (re-fetches updated totals)
- `src/views/incorporate.js:221` — `handleAppliedCoupon` defined separately for the incorporation flow

### Coupon admin CRUD (payment-api)
- `src/utils/payment-api.js:109–141`
  - `getCouponList` → `GET /coupons`
  - `getCouponDetail(id)` → `GET /coupons/:id`
  - `getCouponUsages(id)` → `GET /coupons/:id/usages`
  - `createCoupon` → `POST /coupons`
  - `updateCoupon(couponId)` → `PUT /coupons/:id`
  - `deleteCoupon(id)` → `DELETE /coupons/:id`

### Currency
- `this.paymentCurrencyCode = "SGD"` (payment.js:26) — hardcoded; indicates SG-market primary scope
