# Renew Subscriptions by Credit Card

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Renew Subscriptions by Credit Card |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (company user) |
| **Business Outcome** | Enables clients to pay for one or more expiring subscriptions using a saved or new Stripe credit card, completing the subscription renewal cycle and maintaining uninterrupted service. |
| **Entry Point / Surface** | **Customer app** — **`/billing/renew-subscriptions`**. (After this entry, card payment may continue on the legacy payment page with subscription id query params — see Evidence.) |
| **Short Description** | Clients arrive at the payment page with subscription IDs pre-selected via URL. They choose a saved card or enter new card details via Stripe Elements, optionally apply a promo code, and confirm payment. The backend charges the card and redirects back to the Billing & Subscriptions dashboard on success. |
| **Variants / Markets** | SG (currency hardcoded to SGD in the frontend) |
| **Dependencies / Related Flows** | Billing & Subscriptions dashboard (`/billings-and-subscriptions/`) as source and redirect target; Stripe (card tokenisation via react-stripe-elements); Credit card management (save/list cards); Coupon/promo locking flow; Bank transfer / external payment alternative (`applyForExternalPaymentForMultipleSubscriptions`); Google Analytics ecommerce plugin (transaction tracking on success) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown — frontend only; backend manages credit cards and company subscription payment records |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are HK / UK / AU markets ever routed here, or is this view strictly SG? Which backend service owns `/payment/company-subscriptions` and `/get-subscription-price`? Is this the legacy payment path being replaced by the `customer-billing` Vue app? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry & subscription loading
- `src/views/payments/index.js`
  - Parses `?sid=` query param (multiple IDs joined by `@@`) to determine which subscriptions to renew
  - `fetchChargeAmount()` → `GET /get-subscription-price?companySubscriptionIds[]=…` — fetches itemised pricing and total
  - `componentDidMount` also calls `GET /credit-cards` to pre-load saved cards

### Payment methods
- **Registered (saved) card**: `payWithRegisteredCard(cardId)` → `POST /payment/company-subscriptions?companySubscriptionIds[]=…` with `{ card_id }`
- **New (unregistered) card**: `payWithUnregisteredCard(stripeToken)` → `POST /credit-cards` with `{ token }` to save the card, then delegates to `payWithRegisteredCard` using the returned `_id`
- **Bank transfer alternative**: `applyForExternalPayment(payload)` → `POST` to `applyForExternalPaymentForMultipleSubscriptions` — triggers an emailed payment instruction

### UI components
- `src/components/payment/payment.js`
  - Wraps everything in `<StripeProvider>` using `STRIPE_PUBLISHABLE_KEY` env var
  - `getDetailedPaymentMethod()` returns `"registered_card"`, `"unregistered_card"`, or `"bank"`
  - Renders order summary table (items + total) from `chargeAmount.items`
  - Promo code input calls `lockCoupon({ company_id, code })` → `POST /lock-coupon`; on success re-fetches charge amount
  - Currency display hardcoded to `"SGD"`
  - On payment success: tracks GA ecommerce transaction (`window.ga("ecommerce:addTransaction", …)`) then calls `handlePaymentSuccess()` → redirects to `/billings-and-subscriptions/`

- `src/components/payment/credit-card.js`
  - Shows saved-card dropdown when cards exist; adds "Add new card" option
  - When no cards or "Add new card" selected: renders Stripe Elements form (`CardNumberElement`, `CardExpiryElement`, `CardCVCElement`, cardholder name input)
  - `getStripeToken()` calls `this.props.stripe.createToken({ name: cardHolderName })`

### API endpoints (from `src/utils/api.js`)
| Function | Method | Path |
|---|---|---|
| `getSubscriptionsPrice` | GET | `/get-subscription-price` |
| `getCreditCards` | GET | `/credit-cards` |
| `postCreditCard` | POST | `/credit-cards` |
| `payForSubscriptions` | POST | `/payment/company-subscriptions` |
| `lockCoupon` | POST | `/lock-coupon` (approx) |
| `applyForExternalPaymentForMultipleSubscriptions` | POST | (see api.js) |
