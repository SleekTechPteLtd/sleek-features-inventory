# Handle Stripe Payment Outcome Webhooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Handle Stripe Payment Outcome Webhooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ensures that when Stripe confirms a payment success, processing (direct debit), or failure, the platform immediately enqueues resolution tasks to update invoice payment state and handle direct debit lifecycle events — keeping billing records in sync with actual charge outcomes. |
| **Entry Point / Surface** | `POST /stripe/webhook` — Stripe-facing HTTP endpoint; no user auth guard; validated via Stripe webhook signature and `SWITCH_TO_SLEEK_BILLINGS` feature flag |
| **Short Description** | Receives and validates Stripe webhook events for `payment_intent.succeeded`, `payment_intent.processing`, and `payment_intent.payment_failed`. For each relevant event the handler looks up the matching PaymentToken and enqueues the appropriate background task (`resolveLatestPaymentIntentV2`, `paymentIntentProcessingForDirectDebitV2`, or `failedPaymentDirectDebitV2`) to update payment state. Direct-debit-specific failure handling is applied only when the payment method type contains "debit". |
| **Variants / Markets** | Unknown — currency is driven by AppFeature `tenant_config`; event processing is gated on the `SWITCH_TO_SLEEK_BILLINGS` env flag |
| **Dependencies / Related Flows** | Stripe API (webhook signature verification); AppFeature / sleek-cms (`SWITCH_TO_SLEEK_BILLINGS` flag, `tenant_config.currency`); Task queue infrastructure (Bull / Redis — `PAYMENT_INTENT_RESOLVER` queue); downstream task workers: `resolveLatestPaymentIntentV2`, `paymentIntentProcessingForDirectDebitV2`, `failedPaymentDirectDebitV2`; upstream: payment intent creation flow that stamps `payment_origin: sleek-billing-backend` metadata |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `payment_tokens` (SleekPaymentDB — lookup by `paymentIntentId` / `paymentIntentIds`), `tasks` (task creation and status tracking), `archived_tasks` (completed/expired task archive) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `paymentIntentProcessingForDirectDebitV2` and `failedPaymentDirectDebitV2` tasks are created without an explicit `queue` — which queue do they land on (default queue or a separate one)? 2. `SWITCH_TO_SLEEK_BILLINGS` — is this a temporary migration flag or a permanent per-tenant setting, and which markets currently have it enabled? 3. Failed card payments (non-debit) are only logged — no task is enqueued. Is this intentional (card failures handled by a separate flow) or a known gap? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/stripe/stripe.controller.ts:24–125` — `@Post('webhook')` on `StripeController`; no `@UseGuards` decorator; validated via `StripeService.constructEvent()` which calls `stripe.webhooks.constructEvent()` with the raw request body and `STRIPE_WEBHOOK_SECRET`

### Feature flag and origin filter
- `stripe.controller.ts:37–41` — skips processing if `SWITCH_TO_SLEEK_BILLINGS !== 'enabled'`
- `stripe.controller.ts:43–46` — skips events where `event.data.object.metadata.payment_origin !== 'sleek-billing-backend'` (ensures only intents created by this service are processed)

### PaymentToken lookup (guard before task dispatch)
- `stripe.controller.ts:48–61` — for all three event types, looks up `PaymentTokenRepository.findOne({ $or: [{ paymentIntentId }, { paymentIntentIds: { $in: [paymentIntentId] } }] })`; skips if not found
- `src/payment-token/repositories/payment-token.repository.ts` — wraps Mongoose model for the `PaymentToken` collection in `SleekPaymentDB`
- `src/payment-token/schemas/payment-token.schema.ts` — fields: `paymentIntentId`, `paymentIntentIds[]`, `status`, `chargeId`, `paymentMethodType`, `invoice` (ref), `companyId`, `customerId` (ref)

### Task dispatch per event type
- **`payment_intent.succeeded`** (`stripe.controller.ts:64–83`): enqueues `resolveLatestPaymentIntentV2` on `QUEUES.PAYMENT_INTENT_RESOLVER` with `{ paymentIntentId, chargeId, externalPaymentMethodId, chargeAmount }`; maxRetry=1, interval=5 000 ms
- **`payment_intent.processing`** (`stripe.controller.ts:85–95`): enqueues `paymentIntentProcessingForDirectDebitV2` (no explicit queue) with `{ paymentIntentId, externalPaymentMethodId }`; maxRetry=1, interval=10 000 ms
- **`payment_intent.payment_failed`** (`stripe.controller.ts:98–119`): only enqueues `failedPaymentDirectDebitV2` (no explicit queue) if `paymentMethodType` contains "debit"; carries `{ paymentIntentId, errorMessage }`; maxRetry=1, interval=1 000 ms; non-debit failures are logged only

### Task infrastructure
- `src/task/services/task.service.ts:96–151` — `createTask()` deduplicates on name + data before creating; sets status=`ready`; persists to `tasks` collection
- `src/task/models/task.schema.ts` — `tasks` and `archived_tasks` collections; fields: `name`, `queue`, `data`, `status`, `attempts`, `maxRetry`, `interval`, `companyId`, `rootTaskId`, `parentTaskId`

### Queue constants
- `src/shared/consts/queues.ts` — `PAYMENT_INTENT_RESOLVER = 'PAYMENT_INTENT_RESOLVER'`; `paymentIntentProcessing` and `failedPaymentDirectDebit` tasks do not reference a named queue constant at call site
