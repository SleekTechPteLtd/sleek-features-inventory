# Pay Invoice with Card or Saved Payment Method

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Pay Invoice with Card or Saved Payment Method |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operator, Customer |
| **Business Outcome** | Allows operators or customers to settle an outstanding invoice immediately using a credit card on file or a stored Stripe payment method, completing the billing cycle and syncing payment status to Xero. |
| **Entry Point / Surface** | Sleek App > Billing > Invoice > Pay Now (card or saved payment method selection) |
| **Short Description** | Charges an invoice via a stored credit card or a Stripe payment method (saved card, direct debit). Handles Stripe payment intent lifecycle, 3DS authentication prompts, direct-debit-in-progress guards, and surfaces charge errors to the caller. On success, marks the payment token as paid, updates the invoice status, and triggers a Xero bank transaction fee record. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Payment Token (checkout session pre-requisite), Invoice lifecycle, Stripe payment intents & charges, Xero external invoice sync (`markExternalInvoiceAsPaid`, `createBankTransactionFee`), Credit Card management, Saved Payment Methods, Coupon & credit-balance application, Audit Logs, Task queue (`createBankTransactionFee` async task), Subscription Auto-Upgrade |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | payments, payment_tokens, invoices, customers, credit_cards, payment_methods, audit_logs |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Invoice status update on `payWithPaymentMethod` success appears commented out — is that intentional or a regression? 2. `chargePaymentMethod` route (`POST /v2/payment/charge-payment-method`) seems to be a retry/fallback path — what triggers it vs. the direct pay-with-card/payment-method routes? 3. Market-specific payment method types (wechat_pay, alipay) are gated at Stripe intent level — is there a CMS feature flag controlling which methods appear per market? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `payment/controllers/payment-v2.controller.ts`

| Route | Guard | Purpose |
|---|---|---|
| `POST /v2/payment/pay-with-card` | `@Auth()` | Charges a stored credit card (`cardId`) against an invoice identified by payment token |
| `POST /v2/payment/pay-with-payment-method` | `@Auth()` | Charges a stored Stripe payment method (`paymentMethodId`) against an invoice; always sets `confirm: true` |
| `POST /v2/payment/charge-payment-method` | `@Auth()` | Retry/operator-triggered charge against a specific invoice using whichever saved method is available |

- Client type is derived from company record via `getClientTypeFromCompany(company)` (main vs. manageService).
- `BadRequestException` is thrown at controller level if company is not found or if `chargeStatus === 'failed'`.

### Service — `payment/services/payment-v2.service.ts`

**`payWithCard`** (lines 528–751)
- Resolves payment token → fetches latest invoice state
- Calls `chargeCreditCard()` → `stripeService.chargeByCard(card.token, invoice.totalAmount, stripeCustomerId)`
- On success: marks `PaymentToken` as `PAID`, sets `InvoiceStatus.paid`, calls `externalInvoiceService.markExternalInvoiceAsPaid()`, enqueues `createBankTransactionFee` task
- On failure: records Stripe decline code on card, resets coupon/credit-balance discounts, returns `chargeStatus: 'failed'`
- Emits audit log with tag `pay-with-card`

**`payWithPaymentMethod`** (lines 342–526)
- Resolves payment method record → creates Stripe payment intent → calls `stripeService.confirmPaymentIntent()`
- Status outcomes:
  - `succeeded` → marks token `PAID`, emits audit log
  - `requires_action` → marks token `REQUIRES_ACTION`, returns `clientSecret` for 3DS on frontend
  - `processing` (bacs_debit / au_becs_debit) → marks token `DD_IN_PROGRESS`
- Resets invoice discounts on any exception

**`chargePaymentMethod`** (lines 1615–1665)
- Validates invoice and payment token; guards against overlapping DD-in-progress invoices
- Short-circuits on zero-amount invoices
- Delegates to `attemptPaymentWithAvailableMethods()`

### DTOs

- `PayWithCardRequestV2Dto` — `cardId`, `companyId`, `paymentToken`, `paymentType`, `couponCode`, `isApplyCreditBalance`, `instantCheckout`
- `PayWithPaymentMethodRequestV2Dto` — `paymentMethodId`, `companyId`, `paymentToken`, `paymentType`, `couponCode`, `isApplyCreditBalance`, `confirm`
- `ChargePaymentMethodRequestDto` — `companyId`, `invoiceId`

### External systems

| System | Call |
|---|---|
| Stripe | `chargeByCard`, `createPaymentIntent`, `confirmPaymentIntent`, `cancelPaymentIntent`, `getBalanceTransaction` |
| Xero | `markExternalInvoiceAsPaid`, `createBankTransactionFee` (via ExternalInvoiceService + XeroService) |
| Task queue | `taskService.createTask({ name: 'createBankTransactionFee', ... })` |
| Audit logs | `auditLogsService.addAuditLog()` — tagged `payment-v2`, `pay-with-card` / `pay-with-payment-method-v2` |

### Collections

- `payments` — Payment schema (`payment/models/payment.schema.ts`): records charge, status, method, invoiceId, chargeId
- `payment_tokens` — PaymentToken schema (`payment-token/schemas/payment-token.schema.ts`): tracks payment intent lifecycle, status, paidAt/paidBy
- `invoices` — updated for status, chargeId, paidAt
- `customers` — Stripe customer ID lookup and creation
- `credit_cards` — card token, decline status tracking
- `payment_methods` — stored Stripe payment method externalId, type, userId
- `audit_logs` — action trail per payment attempt
