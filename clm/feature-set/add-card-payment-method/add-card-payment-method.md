# Add Card Payment Method

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM (Billing & Payments) |
| **Feature Name** | Add Card Payment Method |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User / Company Admin |
| **Business Outcome** | Enables customers to save a credit or debit card as a reusable payment method so that Sleek can automatically charge future invoices and subscriptions without requiring manual payment each time. |
| **Entry Point / Surface** | Sleek Customer App > Billing & Subscriptions > Payment tab > Add Card |
| **Short Description** | Presents a Stripe Elements card form (number, expiry, CVC), creates a Stripe SetupIntent via the billing backend, confirms the card setup client-side with Stripe, then persists the confirmed payment method to the billing backend. On success the user is returned to the Payment tab. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Manage Payment Methods (clm/payment-method) — backend CRUD for saved methods; Add Credit Card (clm/credit-card) — legacy token-based backend flow; Billing & Subscriptions page (payment tab) — upstream and return destination; Stripe API — SetupIntent and confirmCardSetup |
| **Service / Repository** | customer-billing, sleek-billings-backend |
| **DB - Collections** | Unknown — client-side only; backend persists to `paymentmethods` (see clm/payment-method/manage-payment-methods.md) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Default currency in component is hardcoded to `SGD` — is the UI market-aware or does currency selection happen elsewhere? 2. No explicit auth guard at the Vue route level is visible in this file — is route-level auth enforced by the router config? 3. The component name is `PendingInvoicesPage` (a mismatch) — is this a copy-paste artifact or does this page serve dual purposes? 4. Is this the only path to add a card, or does the checkout flow also use a separate add-card UI? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend — `src/modules/sleek-billing/billing-and-subscriptions/pages/AddCardPaymentMethod.vue`

**Stripe integration (Stripe Elements)**
- Loads Stripe.js via `loadStripe(VUE_APP_STRIPE_PUBLISHABLE_KEY)` from runtime env (`getAppCustomEnv`)
- Creates three hosted input elements: `cardNumber`, `cardExpiry`, `cardCvc`
- Real-time field validation via element `change` events

**Add-card flow (`mounted` + `handleSubmit`)**
1. `mounted`: calls `PaymentServiceProxy.setupIntent({ companyId, authToken })` → `POST /v2/payment/setup-intent` — returns `client_secret`
2. `handleSubmit`: calls `stripe.confirmCardSetup(clientSecret, { payment_method: { card: cardNumber } })` — Stripe confirms card and returns a `setupIntent.payment_method` ID
3. On success: calls `PaymentServiceProxy.insertPaymentMethod({ externalId: setupIntent.payment_method, companyId }, { authToken })` → `POST /payment-methods` — saves confirmed method to billing backend
4. Success toast "Payment method added." + redirect to `billing-and-subscriptions?tab=payment`
5. Error: shows toast with Stripe or backend error message

**Auth surface**
- `companyId` and `authToken` sourced from `LocalStoreManager` (customer session store)
- No guest/unauthenticated path

### Proxy — `src/proxies/back-end/subscriptions/payment.microservice.js`

| Method | Endpoint | Purpose |
|---|---|---|
| `setupIntent` | `POST /v2/payment/setup-intent` | Creates Stripe SetupIntent; returns `client_secret` |
| `insertPaymentMethod` | `POST /payment-methods` | Persists confirmed Stripe payment method to backend |

- Both calls use `preventDuplicatedRequest` guard (debounce on concurrent calls)
- Base URL resolved via `BaseProxy.getBillingBackendUrl()` (env-driven)

### Related proxy methods (same file, not called from this page)
- `updatePaymentMethod` — `PUT /payment-methods/:id`
- `getPaymentMethods` — `GET /payment-methods`
- `deletePaymentMethod` — `DELETE /payment-methods/:id`
- `payWithCard` — `POST /v2/payment/pay-with-card`
- `payWithPaymentMethod` — `POST /v2/payment/pay-with-payment-method`
