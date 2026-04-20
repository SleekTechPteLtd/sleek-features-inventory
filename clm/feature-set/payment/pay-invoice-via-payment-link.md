# Pay invoice via payment link

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Pay invoice via payment link |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (external — invoice recipient, typically unauthenticated) |
| **Business Outcome** | Enables clients to self-serve pay outstanding invoices through a tokenized URL without requiring a Sleek login, reducing payment friction and accelerating cash collection. |
| **Entry Point / Surface** | **Customer app** — tokenised link → **`/billing/payment/:token`** — **PaymentPage** (“How would you like to pay?” card / bank / local methods). For automated capture, set **`CLM_PAYMENT_PAGE_TOKEN`** to a valid payment token (see `customer-billing` route **`/billing/payment/:token`**). |
| **Short Description** | Client opens a unique tokenized URL to review invoice line items and pay using card, PayNow, bank transfer, WeChat Pay, Alipay, or direct debit. Supports coupon code application, credit balance drawdown, optional terms-of-engagement acknowledgment, and post-payment workflow completion (task advancement for `customerRequest` origin invoices). |
| **Variants / Markets** | SG (card, PayNow, bank transfer, Alipay, WeChat Pay), HK (card, bank transfer, Alipay, WeChat Pay, Chinese-language UI), UK (card, BACS debit, SEPA debit), AU (card, AU BECS debit) |
| **Dependencies / Related Flows** | `GET /payment-token/{token}` (sleek-billings-backend — resolves invoice and payment options from token); `SleekBillingsAPI.getBillingConfigs()` (billing config); `PaymentServiceProxy.applyCouponAndCreditBalance()` (coupon + credit balance application); Stripe.js (card, Alipay, WeChat Pay payment intents); `PaymentFormBankTransferMicroservice` (PayNow / bank transfer sub-flow); `handleTask()` from `@sleek/customer-common` (post-payment workflow for `customerRequest` invoice origin); Post-payment success pages `/billing/payment/success` and `/billing/payment-completion` (betaOnboarding origin); GTM DataLayer (`purchase_value`, `payment_success` events) |
| **Service / Repository** | customer-billing, customer-common (shared libs), sleek-billings-backend |
| **DB - Collections** | Unknown (frontend only; server-side collections not visible in these files — likely `invoices`, `payments`, `paymentTokens` in sleek-billings-backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which sleek-billings-backend controller/service owns `GET /payment-token/{token}` — is it in `payment-token/` module? 2. What conditions on the invoice/request cause `showTermsOfEngagement` or `showMandateDeclaration` to be set in `paymentTokenDetails.options`? 3. Is the 30-day expiry enforced server-side, client-side only, or both? 4. Are WeChat Pay / Alipay available in SG as well as HK, or HK only? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point — `PaymentPage.vue`

- **File**: `src/modules/sleek-billing/payment/pages/PaymentPage.vue`
- Top-level page for the public payment URL. Renders a minimal navbar (Sleek logo + `LocalizationSwitch`) and embeds `PaymentRequestMicroservice` via `MessagingTopic` bus.
- Language support: `en` (English) and `zh` (Chinese — HK flag), toggled via URL `?lang=` param. Indicates HK market coverage.
- Receives internal events: `BILLING_EVENTS.ON_RENDER_PAYMENT_PAGE` carrying `subscriptionIds`, `task`, `oneOffCodes`, `requestPaymentId`, `requestPaymentItems`.

### Core payment logic — `PaymentRequest.microservice.vue`

- **File**: `src/modules/sleek-billing/payment/components/PaymentRequest.microservice.vue`
- Token resolution: extracts `:token` from `$route.params`, calls `GetPaymentTokenProxy.get()` → `GET /payment-token/{token}`.
- Fetches `billingConfigs` from `SleekBillingsAPI.getBillingConfigs()` to configure Stripe element and payment method types from CMS feature flags (`billing_service > stripe_element > payment_request`).
- Pre-render guard states (all show error message and abort payment form):
  - `statusCode` present → invalid/expired link
  - `status === 'PAID'` or `invoice.status === 'paid'` → already paid
  - `status === 'PAY_BY_BANK'` (betaOnboarding / paymentRequest origin) → bank transfer awaiting
  - `status === 'DD_IN_PROGRESS'` or `invoice.status === 'ddInProgress'` → direct debit in progress (3–7 days)
  - `status` in `['FAILED', 'EXPIRED']` or `invoice.status === 'voided'` → link expired
  - `invoice.issueDate` older than 30 days → invoice expired (shows "View Invoices" button)
  - `otherPendingPaidInvoicesWithSameSubscription` non-empty → duplicate subscription guard
  - `localStorage.recentPaymentReferenceId === data.token` → client-side duplicate payment guard
- Stripe redirect handling (`checkAndHandleStripeRedirect`): reads `payment_intent` and `payment_intent_client_secret` query params, calls `stripe.retrievePaymentIntent()`, cleans URL, and navigates to success page on `succeeded`/`processing` status. Used for Alipay and WeChat Pay redirect flows.
- On success: passes `paymentTokenDetails`, `selectedServices` (invoice items), and `companyId` to `ManualPaymentContainer`.

### Payment form — `ManualPaymentContainer.vue`

- **File**: `src/modules/sleek-billing/stripe-element/ManualPaymentContainer.vue`
- Conditionally renders `PaymentFormBankTransferMicroservice` for `pay_now` and `bank_transfer` methods; all other methods use `ManualPaymentForm` (Stripe Elements).
- **Coupon & credit balance**: `CartSummary` emits `onCouponCodeChange`; `onChangeCouponAndCreditBalance` calls `PaymentServiceProxy.applyCouponAndCreditBalance({ invoiceId, couponCode, isApplyCreditBalance })` — response updates `paymentTokenDetails.invoice` in place.
- **Terms of engagement**: shown when `paymentTokenDetails.options.showTermsOfEngagement` is truthy. Client must click "Review" → `TermOfEngagement` popup → agree before payment button is enabled.
- **Mandate declaration**: shown when `paymentTokenDetails.options.showMandateDeclaration` is truthy — checkbox: "On behalf of all subscribers, I confirm I am forming the company for a lawful purpose."
- **Notification preferences**: always shown — opt-in checkbox.
- **Payment method routing after success** (`onPaymentRequestSuccess`):
  - `invoiceOrigin === 'customerRequest'` → calls `handleTask()` from `@sleek/customer-common` to advance the linked workflow task (e.g. `amend-company-share-structure` fetches company users first).
  - `invoiceOrigin === 'betaOnboarding'` → redirects to `/billing/payment-completion`.
  - Otherwise (`paymentRequest`) → redirects to `/billing/payment/success`.
  - `card`, `wechat_pay`, `alipay` → `paidWith=card_payment`
  - `sepa_debit`, `bacs_debit`, `au_becs_debit` → `paidWith=direct_debit`
- **Analytics**: pushes `purchase_value` (total amount) and `payment_success` (userId, country) events to GTM DataLayer on successful payment.

### Token proxy — `get.js`

- **File**: `src/proxies/back-end/payment-token/get.js`
- `GetPaymentTokenProxy.get({ token, authToken, id, loggedInUser })` → `GET ${billingBackendUrl}/payment-token/${token}` via `BaseProxy.getAuthenticatedData()`.
- Response shape includes: `token`, `companyId`, `status`, `invoice` (with `_id`, `number`, `status`, `issueDate`, `totalAmount`, `items`, `invoiceOrigin`, `isApplyCreditBalance`), `paymentTokenDetails.options`, `taskDetails`, `otherPendingPaidInvoicesWithSameSubscription`.
