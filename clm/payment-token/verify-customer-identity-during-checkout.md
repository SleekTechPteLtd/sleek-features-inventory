# Verify Customer Identity During Checkout

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Verify Customer Identity During Checkout |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (end user paying an invoice via a payment link) |
| **Business Outcome** | Ensures only verified customers can proceed to payment, reducing fraud risk and confirming identity before funds are collected |
| **Entry Point / Surface** | Sleek Billing > Payment Link (tokenised checkout page) |
| **Short Description** | When a customer opens a payment link, the system checks whether their account is verified (via `registered_at` flag). If unverified, it resends a verification email so they can confirm their identity before completing payment. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Invoice generation (invoice module), One-time token issuance (one-time-token module), User/Company lookup (company module), Stripe minimum payment validation (stripe module), Credit balance display (credit-balance module) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | payment_tokens, invoices, credit_balances, customer_subscriptions |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Is this checkout page customer-facing (unauthenticated flow) or does it require a logged-in session? No auth guards present on controller endpoints suggests unauthenticated/token-gated access. 2. Which markets have verification enforced vs. skipped? 3. What happens if `resendVerificationEmail` fails silently? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/payment-token/payment-token.controller.ts`

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /payment-token/:id/is-user-verified` | `isUserVerified(id)` | Returns `verified` / `unverified` / `retry` based on whether `user.registered_at` is set |
| `GET /payment-token/:id/resend-verification-email` | `resendVerificationEmailUsingPaymentToken(id)` | Looks up the user via the payment token's linked invoice and calls `userService.resendVerificationEmail(email)` |
| `POST /payment-token` | `createPaymentToken(dto)` | Creates a time-limited token (default 24 h, from `PAYMENT_TOKEN_VALIDITY_HOURS`) tied to an invoice; also creates a one-time token for the user if `userId` is present |
| `GET /payment-token/:id` | `getPaymentToken(id)` | Resolves full payment context including user email, company name/status, credit balance, and Stripe minimum-amount guard |

No auth guards (`@UseGuards`, `JwtAuthGuard`, etc.) are applied — access is token-gated rather than session-authenticated.

### Service — `src/payment-token/payment-token.service.ts`

- **`isUserVerified`** (line 248): fetches `PaymentToken` → resolves linked `Invoice.userId` → calls `userService.getUser(userId)` → checks `user.registered_at`; returns `{ status, companyId, email }`.
- **`resendVerificationEmailUsingPaymentToken`** (line 226): fetches token, resolves user via invoice, calls `userService.resendVerificationEmail(user.email)`.
- **`createPaymentToken`** (line 36): validates invoice exists, handles `betaOnboarding` and `manualRenewal` origins, calls `oneTimeTokenService.createToken`, persists token to `PaymentToken` collection and back-links to `Invoice.paymentTokenId`.
- **`getPaymentToken`** (line 128): enforces Stripe minimum payment amount check; throws `BadRequestException` if `totalAmount < stripeMinimumPaymentAmount`.

### Schema — `src/payment-token/schemas/payment-token.schema.ts`

- Collection: `payment_tokens` (inferred from `PaymentToken` class with `@Schema({ timestamps: true })`)
- Key fields: `token` (UUID v4, indexed), `invoice` (ref: `Invoice`), `status` (`PaymentTokenStatus`), `validUntil`, `oneTimeToken`, `companyId`, `userId`, `paymentIntentId`/`paymentIntentIds`

### External service calls

| Service | Call |
|---|---|
| `UserService` | `getUser(userId)`, `resendVerificationEmail(email)` |
| `CompanyService` | `getCompanyDetails(companyId)` |
| `StripeService` | `getMinimumPaymentAmount(false)` |
| `OneTimeTokenService` | `createToken({ userId, referenceId, referenceType, period })` |
| `CreditBalanceRepository` | `findOne({ companyId })` |
| `CustomerSubscriptionRepository` | `findById(subscriptionId)` (used in duplicate-payment detection) |
