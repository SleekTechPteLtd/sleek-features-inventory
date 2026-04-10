# Apply Promo Code to Subscription Renewal

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Apply Promo Code to Subscription Renewal |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client |
| **Business Outcome** | Enables clients to redeem promotional discounts at checkout, reducing the amount due on their subscription renewal and incentivising timely payment. |
| **Entry Point / Surface** | Sleek App > Subscription Renewal Checkout (`/payments/`) — Order Summary panel |
| **Short Description** | During subscription renewal checkout, clients enter a promotional code and click Apply. The code is validated and locked against the company via the backend, and the order summary is refreshed to reflect the discounted total before final payment. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Subscription Renewal checkout (pay with credit card / bank transfer); `GET /get-subscription-price` to refresh charge amount after coupon is applied; coupon management (admin coupons create/edit) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | What backend service owns `/coupons/lock` and what collections does it touch? Is coupon applicability restricted to specific subscription types or plans? Can this promo code flow also apply during new-purchase checkout, or only renewal? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/components/payment/payment.js` — `Payment` React component; renders promo code input field inside the Order Summary panel (`line 109–141`); `handleClickApplyPromoCode` (line 204) drives the apply flow
- `src/views/payments/index.js` — `Payments` view; mounts `Payment` for Subscription Renewal; supplies `lockCoupon` (line 110) and `handleAppliedCoupon → fetchChargeAmount` (line 176) as props

### API calls (via `src/utils/api.js`)
| Call | Method + Endpoint | Purpose |
|---|---|---|
| `api.lockCoupon` | `POST /coupons/lock` | Validates and locks a promo code for a given company; body: `{ company_id, code }` |
| `api.getSubscriptionsPrice` | `GET /get-subscription-price?companySubscriptionIds=...` | Fetches updated charge breakdown after coupon is applied |
| `api.payForSubscriptions` | `POST /payment/company-subscriptions` | Processes final card payment (with coupon discount already baked into total) |

### Key UI behaviour
- Promo code input is **disabled** once a coupon item (code `"coupon"`) already exists in `chargeAmount.items`, enforcing one promo code per order (`payment.js:121`).
- Locked state shows a `tick-circle` icon; unlocked state shows a `tag` icon (`payment.js:112–116`).
- On successful lock, an alert confirms the code and `fetchChargeAmount` is called to reload the discounted total (`index.js:176`).
- On failure, the server error message is surfaced in an alert (`payment.js:216–222`).

### Payment surface
- Currency is hardcoded to `SGD` (`payment.js:26`), indicating Singapore-only scope.
- Supports credit card (Stripe — registered or new card) and bank transfer payment methods.
- GA ecommerce tracking fires on successful payment (`payment.js:345–381`).
