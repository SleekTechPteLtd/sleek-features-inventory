# Manage Payment Methods and Credit Balance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Payment Methods and Credit Balance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (Company) |
| **Business Outcome** | Customers can save, manage, and designate a preferred payment card via Stripe, and monitor their Sleek credit balance, so that subscription renewals and invoices are charged correctly and without service disruption. |
| **Entry Point / Surface** | Customer Billing App > Billing & Subscriptions > Payment tab |
| **Short Description** | Customers view all saved payment methods (credit/debit cards, SEPA, BACS, AU BECS direct debit) alongside their Sleek credit balance. They can add new cards via Stripe Elements, set a primary payment method, remove outdated ones, and receive proactive warnings when the primary card is expiring (within 30 days) or has already expired. A side drawer shows the full credit balance transaction history. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Stripe (SetupIntent + `confirmCardSetup` for card tokenisation); Billing backend (`/v2/payment/setup-intent`, `/payment-methods`, `/credit-balances/:companyId`); Invoice payment flows (credit balance is applied before charging the saved payment method); Subscription auto-renewal (primary payment method is charged on renewal) |
| **Service / Repository** | customer-billing; billing backend microservice (via `getBillingBackendUrl()`) |
| **DB - Collections** | Unknown (frontend only; backend collections not visible in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Does the billing backend store payment method records in its own collection or rely entirely on Stripe as the source of truth? What is the name/repo of the service behind `getBillingBackendUrl()`? Are SEPA, BACS, and AU BECS debit types actively enabled per market? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/modules/sleek-billing/billing-and-subscriptions/components/PaymentMethodsContent.vue` — main payment methods tab; lists saved methods, credit balance widget, expiry warnings, set-primary and remove actions
- `src/modules/sleek-billing/billing-and-subscriptions/pages/AddCardPaymentMethod.vue` — dedicated "Add a card" page using Stripe Elements (cardNumber, cardExpiry, cardCvc)
- `src/proxies/back-end/subscriptions/payment.microservice.js` — proxy class for all payment method and payment intent API calls
- `src/proxies/back-end/sleek-billings-backend/sleek-billings-api.js` — proxy for credit balance API

### Key behaviours
- **Add card**: mounts Stripe Elements, calls `POST /v2/payment/setup-intent` to get a `client_secret`, confirms via `stripe.confirmCardSetup`, then saves the resulting `payment_method` ID via `POST /payment-methods`
- **List methods**: `GET /payment-methods?companyId=...` returns cards and direct-debit accounts; sorted primary-first
- **Set primary**: `PUT /payment-methods/:id` with `{ isPrimary: true }`
- **Remove**: `DELETE /payment-methods/:id`; if the removed method was primary, the frontend automatically promotes the next valid card or account
- **Expiry logic**: a method is flagged *expiring* if `expiredAt` is within 30 days; *expired* if `expiredAt` is in the past; a banner warns when the **primary** method is in either state
- **Credit balance**: `GET /credit-balances/:companyId` returns `{ balance, transactions[] }`; balance is displayed in locale currency; transactions show `actionType` (add/deduct) and linked invoice number

### Payment method types supported
| Type | Brand logos shown | Market hint |
|---|---|---|
| `card` | Visa, Mastercard, Amex, Diners Club, JCB | All markets |
| `sepa_debit` | SEPA logo | EU / UK |
| `bacs_debit` | BACS logo | UK |
| `au_becs_debit` | BECS logo | AU |

### API surface (billing backend)
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/v2/payment/setup-intent` | Create Stripe SetupIntent |
| POST | `/payment-methods` | Persist payment method after Stripe confirmation |
| GET | `/payment-methods?companyId=` | List saved payment methods |
| PUT | `/payment-methods/:id` | Update (set as primary) |
| DELETE | `/payment-methods/:id` | Remove payment method |
| GET | `/credit-balances/:companyId` | Get credit balance + transaction history |
