# Access invoice payment checkout context

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Access invoice payment checkout context |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User / Customer (arrives via tokenized invoice payment link) |
| **Business Outcome** | Enables the payment page to surface all necessary context — invoice details, company info, user identity, available credit balance, and subscription status — so a customer can review and complete payment for a Sleek invoice. |
| **Entry Point / Surface** | Sleek App > Billing > Invoice Payment Page (tokenized URL delivered via email) |
| **Short Description** | When a user follows a payment link, the payment page resolves the token to load the full checkout context: populated invoice with line items and services, company name and status, user email, available credit balance, and any other pending invoices on the same subscription. A secondary flow lets the page check user verification status and trigger resend of verification emails before payment proceeds. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Invoice management (InvoiceRepository), Credit balance (CreditBalanceRepository), Customer subscriptions (CustomerSubscriptionRepository), One-time token service (OneTimeTokenService), User verification (UserService.resendVerificationEmail), Stripe minimum payment validation (StripeService.getMinimumPaymentAmount) |
| **Service / Repository** | sleek-billings-backend; depends on internal CompanyService and UserService; Stripe |
| **DB - Collections** | paymenttokens, invoices, creditbalances, customersubscriptions, onetimetokens |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No `@UseGuards` visible on the controller — is `GET /payment-token/:id` a public endpoint secured only by token opacity? Who is authorised to call `POST /payment-token` to generate tokens (internal service call or open)? No market-specific branching found — confirm whether SG/HK/UK/AU behaviour differs at the frontend layer. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `payment-token/payment-token.controller.ts`

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/payment-token` | Create a new payment token for an invoice |
| `GET` | `/payment-token/:id` | **Primary capability** — resolve token and return full checkout context |
| `GET` | `/payment-token` | List all payment tokens (internal/admin use) |
| `GET` | `/payment-token/:id/resend-verification-email` | Trigger resend of email-verification link via token |
| `GET` | `/payment-token/:id/is-user-verified` | Check whether the invoice owner has verified their account |

No `@UseGuards` decorators present — access control relies on token opacity.

### Service — `payment-token/payment-token.service.ts`

**`getPaymentToken(token)`** (main capability, line 128):
1. Fetches `PaymentToken` with `invoice` and `items.service` populated.
2. Queries `creditbalances` for the company's available balance.
3. Resolves user email via `UserService.getUser(userId)`.
4. Guards against deleted users (`NotFoundException` if companyId present but user missing).
5. Validates invoice `totalAmount` meets Stripe minimum via `StripeService.getMinimumPaymentAmount`.
6. Resolves company name and status via `CompanyService.getCompanyDetails`.
7. Calls `getOtherPendingPaidInvoicesWithSameSubscription` — cross-checks `customersubscriptions` for renewed/upgraded/downgraded status and surfaces other paid/DD-in-progress invoices on the same subscription.

**`createPaymentToken(dto)`** (line 36):
- Validates invoice exists and origin (`betaOnboarding` requires `companyDetails`; `manualRenewal` requires `companyId`).
- Creates a 24-hour (configurable via `PAYMENT_TOKEN_VALIDITY_HOURS`) UUID v4 token.
- Optionally generates a 15-day `OneTimeToken` when a `userId` is present.
- Back-references the new token on the invoice (`paymentTokenId`).

**`isUserVerified(id)`** (line 248):
- Returns `verified` (has `registered_at`), `unverified`, or `retry` (user not yet available).
- Exposes `companyId` and `email` alongside status so the frontend can route appropriately.

### Schema — `payment-token/schemas/payment-token.schema.ts`

Collection: **`paymenttokens`**

Key fields: `token` (indexed), `invoice` (ref `Invoice`), `companyId`, `userId`, `oneTimeToken`, `status` (enum: ACTIVE / PAID / PAY_BY_BANK / EXPIRED / REQUIRES_ACTION / DD_IN_PROGRESS / DD_FAILED / FAILED), `paymentOrigin` (PORTAL / SALES / API / MANUAL_RENEWAL), `paymentIntentId`, `paymentIntentIds[]`, `paymentMethodId` (ref `PaymentMethod`), `customerId` (ref `Customer`), `validUntil`, `paidAt`, `companyDetails`, `options`, `taskDetails`, `paymentError`, `paymentMethodType`.

Composite indexes: `{ token, status }`, `{ invoice, status }`.

### DTOs — `payment-token/dto/`

- `CreatePaymentTokenDto` — `invoice` (required), optional `companyId`, `userId`, `paymentIntentId`, `paymentOrigin`, `validUntil`, `requestedBy`, `returnUrl`, `companyDetails`, `options`.
- `PaymentTokenDto` — response shape including `creditBalance` (number) augmented by the service.
