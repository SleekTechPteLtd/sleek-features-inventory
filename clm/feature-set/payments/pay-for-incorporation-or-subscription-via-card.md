# Pay for Incorporation or Subscription via Card

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Pay for Incorporation or Subscription via Card |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client |
| **Business Outcome** | Allows clients to complete payment for company incorporation or subscription renewal by charging a saved or new Stripe credit/debit card, enabling Sleek to collect revenue at point of service. |
| **Entry Point / Surface** | Sleek Website > Incorporate > Payment Step; Sleek Website > Billings & Subscriptions > Renew |
| **Short Description** | Presents the client with a Stripe-powered card payment form (new card or saved card selection) alongside an order summary. On submission, tokenises the card via Stripe, saves it if new, then charges the card against the incorporation or subscription order. Optionally accepts a promo code before payment. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Stripe (card tokenisation); Manage Saved Payment Methods (add/select card); Apply Promo Code / Coupon; Bank Transfer / External Payment (alternative method on same screen); Google Analytics ecommerce tracking; Subscription Renewal flow; Company Incorporation wizard |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (frontend only; backend collections for credit cards, companies, coupons, and payment transactions inferred from API endpoints) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Currency is hardcoded to SGD — does this flow support HK or other markets? `applyForCompanyExternalPayment` (bank transfer path) is on the same screen — is it a separate feature or part of this one? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/components/payment/payment.js` — top-level `Payment` component; wraps `StripeProvider`; orchestrates card vs. bank-transfer selection, order summary table, promo code input, and pay button
- `src/components/payment/payment-method.js` — `PaymentMethod` component; radio group for selecting Credit/Debit Card vs. Bank Transfer; renders `CreditCard` or `BankTransfer` sub-form accordingly
- `src/components/payment/select-payment-method.js` — stateless `SelectPaymentMethod` radio group; locks to bank transfer when `externalPaymentInfo` is present
- `src/views/incorporate/steps/payment-step.js` — step-level controller embedded in the incorporation wizard; wires API calls to the `Payment` component; also handles subscription renewal context

### API calls (`src/utils/api.js`)
| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/credit-cards` | Fetch client's saved cards on mount |
| `POST` | `/credit-cards` | Save a new Stripe card (body: `{token}`) |
| `POST` | `/payment/create-company/{companyId}` | Charge the selected card for incorporation/renewal (body: `{card_id}`) |
| `POST` | `/coupons/lock` | Lock and apply a promo code (body: `{company_id, code}`) |
| `PUT` | `/companies/{companyId}/apply-for-external-payment` | Request bank transfer instructions via email (alternative path) |

### Key logic
- **New card path**: Stripe `createToken` → `POST /credit-cards` (save) → `POST /payment/create-company/{id}` (charge)
- **Saved card path**: select existing card → `POST /payment/create-company/{id}` (charge)
- **Post-payment**: GA ecommerce `addTransaction` + `addItem` events fired with transaction ID, revenue, and line items
- **Currency**: hardcoded `SGD` (`this.paymentCurrencyCode = "SGD"`)
- **Minimum amount guard**: pay button disabled and warning shown if `totalAmount <= 0`; server requires ≥ $1

### Related component
- `src/components/payment/credit-card.js` — `CreditCard` + `CheckoutForm` (injected Stripe); renders card number, cardholder name, expiry, CVC fields; supports saved card dropdown with "Add new card" option
