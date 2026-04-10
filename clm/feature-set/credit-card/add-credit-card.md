# Add credit card

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM (Billing & Payments) |
| **Feature Name** | Add credit card |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User / Company Admin |
| **Business Outcome** | Enables a company to register a Stripe-tokenized credit card as a reusable payment method, so that invoices and subscriptions can be charged automatically without re-entering card details. |
| **Entry Point / Surface** | Sleek App > Billing > Payment Methods; Manage Service portal (app-origin: mscomsec) |
| **Short Description** | Accepts a Stripe token and a company ID, provisions a Stripe customer for the user if one does not yet exist, attaches the card as a Stripe customer source, and persists the card record (last 4 digits, expiry, brand, primary flag) to the database. The first card added for a company is automatically designated as the primary payment card. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | CustomerService — Stripe customer provisioning; PaymentMethodRepository — primary-card coordination on update; AuditLogsService — audit trail for card lifecycle; StripeService — Stripe API (two separate Stripe accounts: main vs manage-service); Manage Payment Methods (clm/payment-method) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `credit_cards`, `customers` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Two Stripe secret keys (`STRIPE_SECRET_KEY_MAIN` vs `STRIPE_SECRET_KEY_MANAGE_SERVICE`) — which markets or products use each account? 2. A `// @TODO` in the controller notes that card retrieval should allow both the card owner and a company admin, but currently only the owner is checked — access control for GET is incomplete. 3. The `reference` field stored on `CreditCard` documents has no clear business definition in the code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `POST /` — `CreditCardController.createCreditCard()` (`credit-card/credit-card.controller.ts:71–81`)
- Guard: `@Auth()` decorator — JWT-authenticated user required
- `app-origin` header determines client type (`mscomsec` → `ClientType.manageService`, otherwise `ClientType.main`)

### Core flow (`credit-card/services/credit-card.service.ts:58–137`)
1. Validates `token` and `companyId` are present.
2. Calls `StripeService.init(clientType)` — selects the correct Stripe secret key.
3. Calls `getStripeCustomerId(user._id)` → `CustomerService.getCustomerByReferenceId()` — looks up existing Stripe customer ID.
4. If no Stripe customer ID exists, calls `createStripeCustomerId(user, clientType)`:
   - Creates a `Customer` document in MongoDB if none exists (`CustomerService.createCustomer()`).
   - Creates a Stripe customer via `StripeService.createStripeCustomerId(user.email)` → `stripe.customers.create()`.
   - Persists the returned `stripeCustomerId` back to the `Customer` document.
5. **Non-testing path**: calls `StripeService.createStripeCustomerSource(stripeCustomerId, token)` → `stripe.customers.createSource()` — returns `last4`, `exp_year`, `exp_month`, `brand`, `id`.
6. **Testing path** (`testing: true`): calls `StripeService.createStripeSource(token)` → `stripe.sources.create({ type: 'card', token })` — sets `lastDigits = 'TEST'`, expiry +4 years.
7. Checks `creditCardRepository.findOne({ companyId })` — if no prior card exists for the company, marks the new card as `isPrimary: true`.
8. Persists `CreditCard` document.
9. Records audit log with action `create`, tags `['credit-card', 'adding-credit-card']`.
10. Returns sanitized card (token field omitted).

### Stripe service (`stripe/stripe.service.ts`)
- `createStripeCustomerId()` — `stripe.customers.create({ email })` (line 53)
- `createStripeCustomerSource()` — `stripe.customers.createSource(customerId, { source: token })` (line 295)
- `createStripeSource()` — `stripe.sources.create({ type: 'card', token })` (line 280); used for test cards only

### Schemas / collections
- `CreditCard` (`credit-card/models/credit-card.schema.ts`) → collection `credit_cards`
  - Fields: `userId`, `companyId`, `lastDigits`, `expiredAt`, `type` (card brand), `isPrimary`, `token` (Stripe source/card ID), `reference`, `status`, `migratedAt`
  - Indexes: `userId`, `companyId`
- `Customer` (`customer/models/customer.schema.ts`) → collection `customers`
  - Fields: `referenceId` (user `_id`), `stripeCustomerId`, `type` (`user | company | onboarding_user`), `email`, `firstName`, `lastName`
  - Unique index: `(type, referenceId)`

### Related operations on the same controller
- `GET /:id` — fetch single card detail (owner-only, TODO to add admin access)
- `GET /` — list cards by `companyId` or `userId`
- `PUT /:id` — update card (e.g. set as primary); also resets `isPrimary` on all other cards and payment methods for the company
- `DELETE /:id` — delete card; allowed for card owner or company admin
