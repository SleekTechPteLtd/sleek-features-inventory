# Monitor Xero Webhook Events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Xero Webhook Events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can view incoming Xero webhook events to track integration activity, diagnose processing failures, and validate that Xero invoice events are being received and handled correctly by the billings platform. |
| **Entry Point / Surface** | Sleek Billings Frontend > Developer Tools > Xero Webhook (`/xero-webhook`) |
| **Short Description** | Displays a searchable table of Xero webhook events with event ID, type, status, timestamp, payload, retry count, processing time, tenant ID, and source. The backend ingests webhook payloads from Xero via HMAC-signed POST, persists them in MongoDB, and exposes a GET endpoint for the UI; however, the frontend component is not yet wired to the API and still renders hardcoded sample data. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero Config Monitoring (`/xero-config-monitoring`); Stripe Webhook monitoring (`/stripe-webhook`); Unreconciled Invoices flow (consumes processed webhook records); Xero API (invoice status lookup); sleek-payment API (old-system invoice cross-reference); Bull queue `ProcessXeroWebhook` (async replay) |
| **Service / Repository** | sleek-clm-monorepo (`apps/sleek-billings-frontend`, `apps/sleek-billings-backend`); sleek-billings-frontend (standalone) |
| **DB - Collections** | `webhooks` (MongoDB, SleekPaymentDB — source, resourceExternalId, eventType, payload, xeroInvoice, platformLink, oldSystemLink, retryCount, isReconciled, createdSubscriptions) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | 1. Frontend still uses hardcoded sample data (no API wiring) — is the UI integration deferred or abandoned? 2. Search input and row-level kebab menu are unimplemented — what actions are planned (retry, inspect, resolve)? 3. `SWITCH_TO_SLEEK_BILLINGS` feature flag gates webhook processing — is this still a migration-phase toggle or permanent? 4. Only `UPDATE`/`INVOICE` events are stored; are other event types (contacts, payments) planned? 5. No market/region scoping — is this a global view across all Xero tenants? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend entry point
- `apps/sleek-billings-frontend/src/App.jsx:24` — lazy-imported as `XeroWebhookList`
- `apps/sleek-billings-frontend/src/App.jsx:173` — mounted at route `xero-webhook`, grouped under `{/* Developer Routes */}` alongside `stripe-webhook` and `xero-config-monitoring`; internal operator/developer tool, not end-user-facing

### Frontend component: `XeroWebhookList`
- `apps/sleek-billings-frontend/src/pages/XeroWebhook/XeroWebhookList.jsx:4–123`
- Renders a full-page table with a search input (state: `searchQuery`, not wired to filter logic)
- Table columns: Event ID, Type, Status, Timestamp, Payload, Retry Count, Processing Time, Tenant ID, Source, Actions
- Status badge pill (green for `SUCCESS`); Event ID in blue (suggesting future clickable detail)
- Row-level kebab menu (`EllipsisVerticalIcon`) — no click handler implemented
- `XeroWebhookList.jsx:8` — comment: `// Sample data - replace with actual data from your backend`; no API calls present

### Backend: webhook ingestion — `WebhookController`
- `apps/sleek-billings-backend/src/webhook/controllers/webhook.controller.ts`
- `POST /webhooks/xero` — receives Xero webhook payload; HMAC SHA-256 signature verification via `x-xero-signature` header; uses `XERO_WEBHOOK_KEY_MAIN` config; gated by `SWITCH_TO_SLEEK_BILLINGS === 'enabled'` feature flag; calls `WebhookService.handleXeroWebhookPayload()`
- `GET /webhooks` — `@Auth()` guard; query params: `source`, `platformLink`, `paidInvoices`; calls `WebhookService.getUnprocessedWebhooks()`; returns unreconciled, non-paid-platform-link records sorted by `createdAt` desc — the intended API for the UI list

### Backend: webhook processing — `WebhookService`
- `apps/sleek-billings-backend/src/webhook/services/webhook.service.ts`
- `handleXeroWebhookPayload()` — filters for `eventType === 'UPDATE'` and `eventCategory === 'INVOICE'` only; deduplicates by `resourceId`; 5-second delay between events; saves each via `saveWebhookXero()`; batch-fetches Xero invoice details (batch size 10) and enriches stored record via `addXeroInvoiceInformation()`
- `saveWebhookXero()` — resolves `platformLink` by looking up invoice by `externalId` in the local invoice repo; if found and unpaid, fetches Xero invoice — marks as paid (creates task) or voided; cross-references old system via `GET SLEEK_PAYMENT_API_URL/invoices/external-id/:id`; upserts into `webhooks` collection
- `getUnprocessedWebhooks()` — filters `isReconciled: { $ne: true }` and `platformLink.invoiceStatus: { $ne: 'paid' }`
- `replayWebhook()` — re-enqueues onto `ProcessXeroWebhook` Bull queue, increments `retryCount`

### Backend: async processor — `ProcessXeroWebhookProcessor`
- `apps/sleek-billings-backend/src/external-invoice/xero-webhook.processor.ts`
- Consumes `ProcessXeroWebhook` queue, job name `processXeroWebhook`
- Fetches Xero invoice by ID via `XeroService.getInvoiceFromIDs()` for replay/retry scenarios

### MongoDB schema — `Webhook` entity
- `apps/sleek-billings-backend/src/webhook/entities/webhook.entity.ts`
- Collection: `webhooks` (via Mongoose `SchemaFactory.createForClass(Webhook)`, injected into `SleekPaymentDB`)
- Fields: `source` (required), `resourceExternalId`, `eventType` (required), `payload` (required), `xeroInvoice`, `platformLink` (type, id, companyId, description, invoiceStatus), `oldSystemLink` (type, id, companyId, description, userId), `retryCount` (default 0), `isReconciled` (default false), `createdSubscriptions` (default false), `createdAt`, `updatedAt`
- Indexes: `source`, `processed`, `resourceExternalId`

### Related API surface
- `apps/sleek-billings-frontend/src/services/api.js:219–228` — `getWebhooks()` calls `GET /webhooks` with query params; used by Unreconciled Invoices page but not yet connected to `XeroWebhookList`

### Related developer-tools pages
- `apps/sleek-billings-frontend/src/pages/XeroConfigMonitoring/XeroConfigMonitoringList.jsx` — route `xero-config-monitoring`
- `apps/sleek-billings-frontend/src/pages/StripeWebhook/StripeWebhookList.jsx` — route `stripe-webhook`
