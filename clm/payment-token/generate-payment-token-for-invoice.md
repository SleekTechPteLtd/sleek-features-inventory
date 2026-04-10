# Generate Payment Token for Invoice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Generate Payment Token for Invoice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User; System |
| **Business Outcome** | Enables customers to securely pay invoices by generating a time-limited, unique payment link tied to an invoice — supporting beta onboarding and manual subscription renewal flows. |
| **Entry Point / Surface** | Internal API — `POST /payment-token`; triggered by ops tooling, admin portals, or automated onboarding/renewal workflows |
| **Short Description** | Creates a UUID-based payment token linked to a specific invoice with a configurable expiry (default 24 h). Simultaneously creates a 15-day one-time authentication token for the associated user. The token is embedded in a URL that directs the customer to a Stripe-backed payment page. Supports two invoice origins: `betaOnboarding` (requires `companyDetails`) and `manualRenewal` (requires `companyId`). Also exposes helper endpoints to check user verification status and resend the verification email via the token. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | OneTimeTokenService (auth token creation); InvoiceRepository (invoice lookup + paymentTokenId backfill); CreditBalanceRepository (credit balance read on token retrieval); UserService (user lookup, resend verification email); CompanyService (company details on token retrieval); CustomerSubscriptionRepository (duplicate-paid-invoice guard); StripeService (minimum payment amount validation); Beta Onboarding flow; Manual Renewal flow |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `paymenttokens`, `invoices`, `creditbalances`, `customersubscriptions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No auth guard is present on the controller — is this endpoint protected at the API gateway / network level, or intended to be internal-only? Who calls `POST /payment-token` in practice (ops admin UI, automated job, or both)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/payment-token/payment-token.controller.ts`

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/payment-token` | Create token (no visible auth guard — likely internal) |
| `GET` | `/payment-token/:id` | Retrieve full token payload (with invoice, company, credit balance, subscription data) |
| `GET` | `/payment-token` | List all tokens |
| `GET` | `/payment-token/:id/resend-verification-email` | Resend email verification to the invoice's user |
| `GET` | `/payment-token/:id/is-user-verified` | Check whether the invoice's user has completed registration |

### Service — `src/payment-token/payment-token.service.ts`

- `createPaymentToken()` — generates `uuidv4` token; expiry from `PAYMENT_TOKEN_VALIDITY_HOURS` env var (default 24 h); calls `oneTimeTokenService.createToken()` (15-day period, referenceType `"Payment Token"`); validates `invoiceOrigin` (`betaOnboarding` / `manualRenewal`); writes to `paymenttokens`; back-fills `invoices.paymentTokenId`.
- `getPaymentToken()` — populates invoice → items.service; resolves user email, company name/status via `UserService` / `CompanyService`; validates Stripe minimum payment amount; calls `getOtherPendingPaidInvoicesWithSameSubscription()` to surface any duplicate paid invoices on the same subscription.
- `resendVerificationEmailUsingPaymentToken()` — resolves userId from invoice, delegates to `userService.resendVerificationEmail()`.
- `isUserVerified()` — checks `user.registered_at` to determine `verified` / `unverified` / `retry` state.

### DTO — `src/payment-token/dto/create-payment-token.dto.ts`

- Required: `invoice` (ObjectId string)
- Optional: `companyId`, `userId`, `paymentIntentId`, `paymentOrigin` (`PORTAL | SALES | API | MANUAL_RENEWAL`), `validUntil`, `requestedBy`, `returnUrl`, `companyDetails`, `options`
- `PaymentTokenStatus` values: `ACTIVE`, `PAID`, `PAY_BY_BANK`, `EXPIRED`, `REQUIRES_ACTION`, `DD_IN_PROGRESS`, `DD_FAILED`, `FAILED`, `FULLY_PAID_BY_DISCOUNT`

### Schema — `src/payment-token/schemas/payment-token.schema.ts`

- Collection: `paymenttokens` (Mongoose default pluralisation of `PaymentToken`)
- Indexes: `{ token: 1 }`, `{ token: 1, status: 1 }`, `{ invoice: 1, status: 1 }`
- Notable fields: `oneTimeToken`, `paymentIntentId`, `paymentIntentIds[]`, `validUntil`, `paidAt`, `paidBy`, `paymentMethodId`, `paymentMethodType` (`card`, `bacs_debit`, `au_becs_debit`, `bank_transfer`, `pay_now`, `wechat_pay`, `alipay`), `taskDetails`, `oldStripeCardId`
- Market signal from `paymentMethodType`: `bacs_debit` → UK; `au_becs_debit` → AU; `pay_now` → SG; `wechat_pay`/`alipay` → SG/HK
