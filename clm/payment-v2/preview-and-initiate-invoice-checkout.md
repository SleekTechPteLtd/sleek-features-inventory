# Preview and Initiate Invoice Checkout

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Preview and Initiate Invoice Checkout |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (unauthenticated, arriving via payment link) |
| **Business Outcome** | Allows customers to see a full breakdown of what they'll be charged — including item discounts, coupon savings, and applicable taxes — and to create a Stripe payment intent before submitting payment, enabling frictionless invoice payment without a Sleek account session. |
| **Entry Point / Surface** | Customer-facing checkout page (payment link, unauthenticated) |
| **Short Description** | Two unauthenticated endpoints: one returns a real-time checkout preview (subtotal, discounts, tax, total) for a set of invoice line items with an optional coupon; the other validates a payment token and creates or retrieves a Stripe PaymentIntent, creating a Stripe customer record as needed. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Payment token issuance (upstream); Stripe PaymentIntent confirmation / pay-with-card / pay-with-bank (downstream); coupon validation (InvoiceService); tax rate lookup (SubscriptionConfigService); feature flags (AppFeatureService / sleek-cms); optional user association via one-time-token |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | payment_tokens (read/update), invoices (read via PaymentToken), customers (read/create via CustomerService), services (read for tax rate lookup) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/platforms are actually active for this checkout flow (SG, HK, UK, AU)? Are wechat_pay and alipay payment methods live in any market? Is the `isSubmitPayment` flag in the DTO still used or commented out permanently? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints (`payment/controllers/payment-v2.controller.ts`)

| Method | Route | Auth | Notes |
|---|---|---|---|
| `POST` | `/v2/payment/preview-checkout` | None | Reads `app-origin` header to derive `clientType`; no user session required |
| `POST` | `/v2/payment/create-payment-intent` | None | Reads `app-origin` and `one-time-token` headers; no `@Auth()` guard |

### `previewCheckoutItems` (`payment/services/payment-v2.service.ts:1401`)

- Accepts a list of `InvoiceItemDto` items and an optional `couponCode`.
- Computes `subTotal` and item-level discounts (by `discountRate` or flat `discountAmount`).
- Calls `InvoiceService.checkCouponCode` to apply coupon discounts (supports `flat` and `percentage` `CouponCalculationType`).
- Checks `AppFeatureService` (`AppFeature.billingService / taxCalculation`) feature flag; if enabled, calls `SubscriptionConfigService.getTaxRateByServiceCodes` to compute GST/tax per line.
- Returns `PreviewCheckoutItemsResponseDto`: `checkoutItems`, `subTotalAmount`, `totalDiscount`, `totalTax`, `totalAmount`, and an optional `error` object.
- Read-only — nothing is persisted.

### `createPaymentIntent` (`payment/services/payment-v2.service.ts:881`)

- Accepts `CreatePaymentIntentRequestDtoV2`: `paymentToken` (wraps an existing invoice), optional `companyId`, `paymentType`, `items`, `couponCode`, `paymentMethodTypes`, `paymentMethodId`, `email`, `firstName`, `lastName`, `requireCvcRecollection`, `isSubmitPayment`.
- Validates `oneTimeToken` via `OneTimeTokenService` to resolve a `userId` without a login session.
- Loads `PaymentToken` (which embeds the linked `Invoice`) and updates `paymentMethodType`.
- Finds or creates a Stripe customer (`CustomerService` → `StripeService.createStripeCustomerId`).
- Handles migrated `card_*` IDs by looking up the payment method owner via `PaymentMethodService`.
- Creates or reuses a Stripe `PaymentIntent`; creates a new one if the existing intent's status or payment method types no longer match.
- Supported Stripe payment method types: `card`, `wechat_pay`, `alipay` (and platform-specific defaults from `PAYMENT_METHODS[PLATFORM]`).
- Skips `setup_future_usage: off_session` for wechat_pay / alipay (one-time payments only).

### DTOs

- `CreatePaymentIntentRequestDtoV2` — `payment/dtos/create-payment-intent-v2.request.dto.ts`
- `PreviewCheckoutItemsRequestDto` — `payment/dtos/preview-checkout-items.request.dto.ts` (items: `InvoiceItemDto[]`, couponCode)
- `PreviewCheckoutItemsResponseDto` — `payment/dtos/preview-checkout-items.response.dto.ts` (checkoutItems, subTotalAmount, totalDiscount, totalTax, totalAmount, error)

### Module registrations (`payment/payment-v2.service.module.ts`, `payment-v2.processor.module.ts`)

Collections confirmed via `MongooseModule.forFeature`: `PaymentToken`, `Invoice`, `Service`, `Task`, `CustomerSubscription`.
