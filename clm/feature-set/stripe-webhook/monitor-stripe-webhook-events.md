# Monitor Stripe Webhook Events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Stripe Webhook Events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can inspect incoming Stripe webhook events — including processing status, raw payload, retry count, and processing time — to diagnose and troubleshoot payment integration issues without needing direct database or log access. |
| **Entry Point / Surface** | Sleek Billings Frontend > Developer Tools > Stripe Webhook (`/stripe-webhook`) |
| **Short Description** | Displays a searchable table of Stripe webhook events showing Event ID, event type, status, timestamp, payload, retry count, processing time, and source. Intended as an internal diagnostic tool for operators investigating payment processing problems. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero Webhook monitoring (`/xero-webhook`); Xero Config Monitoring (`/xero-config-monitoring`); `getWebhooks` API function (`/webhooks`) in `src/services/api.js` (not yet wired to this component); Stripe payment processing pipeline |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend |
| **DB - Collections** | `payment_tokens` (read: look up PaymentIntent ID before dispatching task); `webhooks` (Xero-only at time of scan — Stripe events are not persisted to this collection) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | 1. Backend API not yet connected — component uses hardcoded sample data; is this feature still in development? 2. The existing `GET /webhooks` endpoint retrieves Xero webhooks only; a Stripe-specific list endpoint does not yet exist — will one be added, or will Stripe events start being persisted to the `webhooks` collection? 3. The Stripe controller does not persist incoming events to any collection — only dispatches queue tasks — so there is no current data source for the UI table; is event persistence planned? 4. The row-level action menu (EllipsisVerticalIcon) has no click handler — what operations are planned (e.g. manual retry, view full payload)? 5. No pagination, date-range filtering, or market scoping is implemented. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/App.jsx:23` — lazy-imported as `StripeWebhookList`
- `src/App.jsx:172` — mounted at route `stripe-webhook`, grouped under `{/* Developer Routes */}` alongside `xero-webhook` and `xero-config-monitoring`; indicates this is an internal operator/developer tool

### Component: `StripeWebhookList`
- `src/pages/StripeWebhook/StripeWebhookList.jsx:4–116`
- Renders a full-page table with a search input (client-side filter via `searchQuery` state, though filtering logic is not yet applied to the data array)
- Table columns: Event ID, Type, Status, Timestamp, Payload, Retry Count, Processing Time, Source, Actions
- Data shape per row: `{ eventId, type, status, timestamp, payload, retryCount, processingTime, source }`
- Sample data shows `type: 'payment_intent.succeeded'`, `status: 'SUCCESS'`, `retryCount: 0`, `processingTime: '245ms'`, `source: 'Stripe'`
- Status rendered as a green colour-coded badge pill (green for SUCCESS)
- Payload column is truncated (`max-w-xs truncate`) for display — full payload not expandable at time of scan
- Row-level kebab menu button (`EllipsisVerticalIcon`) present but no click handler implemented

### Backend integration status
- `src/pages/StripeWebhook/StripeWebhookList.jsx:7` — comment: `// Sample data - replace with actual data from your backend`
- No `useEffect`, `fetch`, Axios, or API hook calls present — data is entirely static at time of scan
- No error or loading states implemented

### Related API function
- `src/services/api.js:219–228` — `getWebhooks(options)`: calls `GET /webhooks?{queryParams}` — generic webhooks endpoint that may eventually back this page; also used by `UnreconciledInvoicesList` via `reconcileInvoice` and `considerAsReconciled` calls that reference `webhookId`

### Related pages in the same developer-tools group
- `src/pages/XeroWebhook/XeroWebhookList.jsx` (route `xero-webhook`) — Xero webhook event monitoring; structurally identical pattern (same sample-data approach, same table layout, same unimplemented action menu)
- `src/pages/XeroConfigMonitoring/XeroConfigMonitoringList.jsx` (route `xero-config-monitoring`) — Xero tenant config sync health monitoring

### Backend webhook receiver (sleek-billings-backend)
- `src/stripe/stripe.controller.ts:24–124` — `POST /stripe/webhook` (no auth guard; signature verified via HMAC using `STRIPE_WEBHOOK_SECRET`)
  - Validates Stripe signature via `StripeService.constructEvent()`; throws `UnauthorizedException` on failure
  - Short-circuits if `SWITCH_TO_SLEEK_BILLINGS` feature flag is not `'enabled'`
  - Short-circuits if `payment_origin` metadata is not `'sleek-billing-backend'`
  - Looks up `PaymentToken` by `paymentIntentId` before dispatching any task
  - Handles three event types:
    - `payment_intent.succeeded` → dispatches `resolveLatestPaymentIntentV2` task to `PAYMENT_INTENT_RESOLVER` queue
    - `payment_intent.processing` → dispatches `paymentIntentProcessingForDirectDebitV2` task (no queue name set, uses default)
    - `payment_intent.payment_failed` → dispatches `failedPaymentDirectDebitV2` task (direct-debit path only)
  - Does **not** persist the Stripe event to any MongoDB collection

- `src/stripe/stripe.service.ts:331–343` — `constructEvent()` reads `stripe-signature` header and verifies raw body against webhook secret
- `src/shared/consts/queues.ts:2` — `PAYMENT_INTENT_RESOLVER` queue name constant

### Webhook entity and collection (sleek-billings-backend)
- `src/webhook/entities/webhook.entity.ts` — `Webhook` schema on `SleekPaymentDB` → `webhooks` collection
  - Fields: `source`, `eventType`, `payload`, `resourceExternalId`, `retryCount`, `platformLink`, `oldSystemLink`, `isReconciled`, `createdSubscriptions`
  - Currently populated only by Xero webhook events; Stripe events are **not** saved here
- `src/webhook/controllers/webhook.controller.ts:62–70` — `GET /webhooks` returns unprocessed webhooks filtered by `source` (Xero only in practice)

### PaymentToken collection (sleek-billings-backend)
- `src/payment-token/schemas/payment-token.schema.ts` — `PaymentToken` schema on MongoDB
  - Looked up by `paymentIntentId` or `paymentIntentIds[]` during Stripe webhook processing
  - Fields relevant to webhook flow: `paymentIntentId`, `paymentIntentIds`, `status`, `chargeId`, `paymentMethodType`
