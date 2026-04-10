# Save Payment Method for Future Billing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Save Payment Method for Future Billing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operator |
| **Business Outcome** | Allows an operator to register a card against a company's Stripe customer record so it can be charged automatically for recurring or future invoices without requiring the customer to be present at checkout. |
| **Entry Point / Surface** | Sleek App > Billing > Payment Methods (exact navigation path Unknown) |
| **Short Description** | Creates a Stripe SetupIntent scoped to a company's Stripe customer (`usage: off_session`) and returns the client secret to the frontend. The frontend completes card capture via Stripe.js, attaching the payment method to the customer for future off-session charges. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Stripe SetupIntent API; Customer service (create/upsert Stripe customer linked to companyId); Pay with Payment Method flow (`POST /v2/payment/pay-with-payment-method`); Charge Payment Method flow (`POST /v2/payment/charge-payment-method`); Auto-Charge Invoice Upgrade flow |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customers` (stores `stripeCustomerId` mapped to `referenceId`/companyId); `paymentmethods` (stores confirmed payment method details after setup completion) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No webhook handler for `setup_intent.succeeded` was found — it is unclear whether payment method persistence after confirmation is handled entirely on the frontend (via Stripe.js) or if there is a separate backend step. Exact UI navigation path is not derivable from code alone. Markets/platform flag not restricted in this endpoint. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoint
- `POST /v2/payment/setup-intent` — `PaymentV2Controller.setupIntent` (`payment/controllers/payment-v2.controller.ts:46–53`)
- Guard: `@Auth()` — authenticated operator required
- Body: `SetupIntentRequestDto` — single field `companyId: string` (`payment/dtos/setup-intent.request.dto.ts`)
- Returns: `Stripe.SetupIntent` (including `client_secret` for frontend confirmation)

### Service logic
- `PaymentServiceV2.setUpIntent(companyId, user)` (`payment/services/payment-v2.service.ts:330–340`)
  1. Calls `createStripeCustomer(companyId, user)` — looks up or creates a `Customer` document keyed by `referenceId = companyId`; provisions a Stripe customer ID if absent and stores it in the `customers` collection
  2. Calls `StripeService.setUpIntent(['card'], customer.stripeCustomerId)` (`stripe/stripe.service.ts:317–329`)
  3. Stripe API: `setupIntents.create({ payment_method_types: ['card'], customer: stripeCustomerId, usage: 'off_session' })`

### Post-confirmation (downstream)
- `PaymentServiceV2` lines 1176–1190: when a subsequent payment is processed, the code calls `paymentMethodService.createPaymentMethod(...)` using the Stripe `externalPaymentMethodId` — this is how confirmed methods land in the `paymentmethods` collection.
- `ChargePaymentMethod` / `PayWithPaymentMethod` flows iterate `paymentMethodService.getPaymentMethods({ companyId })` to reuse stored methods.

### Collections
- `customers` schema: `customer.schema.ts` — fields `stripeCustomerId`, `referenceId`, `type`
- `paymentmethods` schema: `payment-method.schema.ts` — fields `externalId` (Stripe PM ID), `userId`, `companyId`, `lastDigits`, `brand`, `type`, `isPrimary`

### Stripe webhook
- `StripeController` (`stripe/stripe.controller.ts`) handles `payment_intent.succeeded/failed/processing` only; no explicit `setup_intent.succeeded` handler found.
