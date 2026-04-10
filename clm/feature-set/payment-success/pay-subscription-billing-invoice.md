# Pay Subscription Billing Invoice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Pay Subscription Billing Invoice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (subscription holder) |
| **Business Outcome** | Enables customers to pay outstanding subscription invoices via a payment link using their preferred method, completing the billing cycle and confirming receipt of payment. |
| **Entry Point / Surface** | Email payment link → Sleek App > `/billing/payment/:token` → payment form → `/billing/payment/success` |
| **Short Description** | Customer opens a tokenised payment link, reviews the invoice, selects a payment method (credit card, bank transfer, PayNow, WeChat Pay, Alipay, or direct debit), and submits payment through Stripe. On success, a confirmation screen shows immediate success for credit card payments or a pending status for asynchronous methods, then routes the customer to their billing and subscriptions overview. |
| **Variants / Markets** | SG (PayNow), HK (WeChat Pay, ZH localisation), UK (BACS debit), AU (AU BECS debit) |
| **Dependencies / Related Flows** | Payment token validation; Stripe payment processing; coupon & credit balance application; billing configs; post-payment redirect to Billing & Subscriptions overview; `betaOnboarding` invoices redirect to Payment Completion (`/billing/payment-completion`); `customerRequest` invoices trigger workflow task handling via `handleTask`; Google Tag Manager analytics events |
| **Service / Repository** | customer-billing |
| **DB - Collections** | Unknown (no direct DB access from frontend; all mutations are backend-mediated via sleek-billings-backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which exact markets/currencies are live beyond SG and HK? Are there server-side fraud checks or rate limits beyond the client-side duplicate-payment guard (`recentPaymentReferenceId`)? Which MongoDB collections are mutated on payment confirmation in the backend? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry pages
- `src/modules/sleek-billing/payment/pages/PaymentPage.vue` — top-level page shell; mounts `PaymentRequestMicroservice`, subscribes to `MessagingTopic` for `ON_RENDER_PAYMENT_PAGE`, passes `subscriptionIds`, `task`, `oneOffCodes`, `requestPaymentId`, and `requestPaymentItems` into the form.
- `src/modules/sleek-billing/payment/pages/PaymentSuccessPage.vue` — post-payment confirmation page at `/billing/payment/success`; reads `?paidWith=CREDIT_CARD` URL param to branch between immediate success (credit card) and pending status (all other methods); prevents browser back-navigation via `popstate` handler and `beforeRouteLeave` guard; "View Subscriptions" button navigates to `/billing/billing-and-subscriptions/?cid=<companyId>`.

### Payment form
- `src/modules/sleek-billing/payment/components/PaymentRequest.microservice.vue` — loads and validates payment token via `GetPaymentTokenProxy`; checks for Stripe redirect params (`payment_intent`, `payment_intent_client_secret`) to handle async redirect-based methods (Alipay, WeChat Pay); guards against already-paid, bank-transfer-awaiting, DD-in-progress, failed/expired, 30-day-expired, and duplicate-subscription invoices; mounts `ManualPaymentContainer` with invoice line items and billing configs.
- `src/modules/sleek-billing/stripe-element/ManualPaymentContainer.vue` — orchestrates the payment UX: renders `ManualPaymentForm` (Stripe Elements), `CartSummary`, optional `TermOfEngagement`, and mandatory-declaration checkbox; on success calls `onPaymentRequestSuccess` which fires GTM `purchase_value` and `payment_success` events, then routes to success page (card/WeChat/Alipay → `POST_PAYMENT + ?paidWith=CREDIT_CARD`; SEPA/BACS/AU BECS debit → `POST_PAYMENT + ?paidWith=direct_debit`).

### Backend API calls (via sleek-billings-backend)
| Proxy | Endpoint | Purpose |
|---|---|---|
| `GetPaymentTokenProxy.get` | `GET /payment-token/:token` | Validate token and load invoice details |
| `SleekBillingsAPI.getBillingConfigs` | `GET /api/config` | Feature flags and Stripe config |
| `PaymentServiceProxy.payWithCard` | `POST /v2/payment/pay-with-card` | Credit card payment |
| `PaymentServiceProxy.payWithBank` | `POST /v2/payment/pay-with-bank` | Bank transfer payment |
| `PaymentServiceProxy.payWithPaymentMethod` | `POST /v2/payment/pay-with-payment-method` | Saved payment method |
| `PaymentServiceProxy.createPaymentIntent` | `POST /v2/payment/create-payment-intent` | Stripe payment intent creation |
| `PaymentServiceProxy.confirmPaymentIntent` | `POST /payment/confirm-payment-intent` | Confirm Stripe payment intent |
| `PaymentServiceProxy.applyCouponAndCreditBalance` | `POST /invoices/apply-coupon-and-credit-balance` | Discount and credit application |

### Payment method routing (post-payment)
- `card`, `wechat_pay`, `alipay` → success page with `paidWith=CREDIT_CARD`
- `sepa_debit`, `bacs_debit`, `au_becs_debit` → success page with `paidWith=direct_debit`
- `pay_now`, `bank_transfer` → `PaymentFormBankTransferMicroservice` (separate pending flow)
- `betaOnboarding` origin → `/billing/payment-completion`
- `customerRequest` origin → `handleTask` workflow

### Analytics
- GTM DataLayer: `purchase_value` event with `invoice.totalAmount`
- GTM DataLayer: `payment_success` event with `userId` and `paymentCountry`

### Duplicate-payment prevention
- `localStorage.recentPaymentReferenceId` checked on load; matches token → blocks re-payment with "paid invoice" error
- Client-side `preventDuplicatedRequest` wrapper on all payment proxy calls
