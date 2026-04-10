# Review Unprocessed Xero Webhooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Unprocessed Xero Webhooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can query Xero webhook events that have not yet been reconciled with the internal billing system, enabling them to detect and investigate payment sync gaps where Xero has processed a payment or status change but the platform record has not been updated. |
| **Entry Point / Surface** | Internal Admin API — `GET /webhooks`; surfaced in `sleek-billings-frontend` at route `/xero-webhook` via `getWebhooks()` API call |
| **Short Description** | Returns unreconciled Xero webhook events sorted by most recent, filtered by source, Xero invoice payment status, and whether a platform invoice link exists. Excludes any event already marked as reconciled or whose linked platform invoice is already paid. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Monitor Xero Webhook Events (frontend view at `/xero-webhook`); Xero Config Monitoring (`/xero-config-monitoring`); Unreconciled Invoices flow (downstream consumer of reconciled webhook state); `POST /webhooks/xero` ingestion endpoint (produces the webhook records queried here); `SWITCH_TO_SLEEK_BILLINGS` feature flag must be enabled for webhook ingestion to run |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `webhooks` (SleekPaymentDB) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. `platformLink` filter param is accepted by the controller but commented out in the service query — was this intentionally disabled or is it a regression? 2. What markets/Xero tenants are active — the only tenant ID wired is `XERO_TENANT_ID_MAIN`; are multi-tenant or per-market tenant IDs planned? 3. The replay endpoint (`POST /webhooks/:id/replay`) is commented out in the controller — is replay functionality deferred or deprecated? 4. `isReconciled` flag exists on the schema but the `markWebhookAsProcessed` method (which sets `processed`/`processedAt`) does not set `isReconciled=true` — what process marks a webhook as reconciled? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/webhook/controllers/webhook.controller.ts:62–70` — `GET /webhooks` protected by `@Auth()` decorator
- Query params: `source` (string filter), `platformLink` (boolean, currently inactive), `paidInvoices` (boolean — filters to `xeroInvoice.status = 'PAID'`)

### Service: `getUnprocessedWebhooks`
- `src/webhook/services/webhook.service.ts:200–226`
- Always applies `isReconciled: { $ne: true }` and `platformLink.invoiceStatus: { $ne: 'paid' }`
- Optional: `source` filter and `xeroInvoice.status = 'PAID'` filter
- Returns results sorted by `createdAt: -1` (most recent first)
- `platformLink` existence filter is commented out (lines 212–214)

### Repository
- `src/webhook/repositories/webhook.repository.ts` — extends `BaseRepository<Webhook>` on the `SleekPaymentDB` connection

### Schema: `Webhook` entity
- `src/webhook/entities/webhook.entity.ts`
- Key fields: `source`, `resourceExternalId` (Xero invoice ID), `eventType`, `payload`, `xeroInvoice` (enriched Xero invoice snapshot), `platformLink` (internal invoice cross-reference with `invoiceStatus`), `oldSystemLink` (legacy SleekPayment system cross-reference), `isReconciled`, `retryCount`, `createdSubscriptions`
- Indexed on: `source`, `processed`, `resourceExternalId`

### Related ingestion flow
- `src/webhook/controllers/webhook.controller.ts:32–60` — `POST /webhooks/xero` receives Xero webhook callbacks, validates HMAC-SHA256 signature against `XERO_WEBHOOK_KEY_MAIN`, gated by `SWITCH_TO_SLEEK_BILLINGS=enabled`
- `src/webhook/services/webhook.service.ts:247–309` — `handleXeroWebhookPayload` deduplicates events, filters to `UPDATE/INVOICE` type, calls `saveWebhookXero` per event, then enriches stored records with full Xero invoice detail via `addXeroInvoiceInformation`
- `src/webhook/services/webhook.service.ts:58–174` — `saveWebhookXero` resolves platform invoice link, triggers `markExternalInvoiceAsPaid` task or voids invoice, and cross-references the legacy SleekPayment API

### External integrations touched during ingestion
- Xero API via `XeroService.getInvoiceFromIDs` (fetches invoice detail for enrichment)
- SleekPayment API: `GET {SLEEK_PAYMENT_API_URL}/invoices/external-id/:resourceId` (legacy system cross-reference)
- Bull queue: `QUEUES.ProcessXeroWebhook` (used by `replayWebhook`, currently inactive via commented controller route)
- `InvoiceRepository`, `PaymentTokenRepository`, `TaskService`, `InvoiceService` — all touched during ingestion, not during the query path
