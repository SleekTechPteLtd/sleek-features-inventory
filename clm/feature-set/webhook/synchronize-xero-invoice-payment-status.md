# Synchronize Xero Invoice Payment Status

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Synchronize Xero invoice payment status |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps internal invoice and payment records accurate when Xero marks an invoice as paid or voided, preventing stale billing state and ensuring subscription upgrade cancellations are triggered correctly. |
| **Entry Point / Surface** | Xero webhook push → `POST /webhooks/xero` (no user-facing surface; system-to-system only) |
| **Short Description** | Receives batched Xero `INVOICE UPDATE` events, validates HMAC-SHA256 signatures, deduplicates by resource ID, then per event: fetches the current Xero invoice state, marks the internal invoice as paid or voided, updates the associated payment token status, and cancels any pending subscription upgrade when the invoice is voided. Also cross-links the event against the legacy Sleek Payment system for reconciliation. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero API (`XeroService.getInvoiceFromIDs`); `markExternalInvoiceAsPaid` task flow; `cancelSubscriptionUpgradeWhenInvoiceVoided` (InvoiceService); legacy Sleek Payment API (`SLEEK_PAYMENT_API_URL`); `ProcessXeroWebhook` Bull queue (replay path); `SWITCH_TO_SLEEK_BILLINGS` feature flag gates all processing |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `webhooks`, `invoices`, `paymenttokens` (all SleekPaymentDB / MongoDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which Xero tenants / markets are covered by `XERO_TENANT_ID_MAIN`? Is HK on a separate tenant? Is the `SWITCH_TO_SLEEK_BILLINGS` flag fully enabled in production? The replay endpoint (`POST /webhooks/:id/replay`) is commented out — is it still used via the queue directly? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/webhook/controllers/webhook.controller.ts:32` — `POST /webhooks/xero`, no auth guard, raw-body required for HMAC validation
- HMAC-SHA256 computed over raw request body and compared against `x-xero-signature` header; mismatch → `UnauthorizedException`
- `SWITCH_TO_SLEEK_BILLINGS !== 'enabled'` short-circuits processing and returns early

### Core processing — `handleXeroWebhookPayload`
- `src/webhook/services/webhook.service.ts:247` — filters payload to `eventType === 'UPDATE'` and `eventCategory === 'INVOICE'` for the configured main tenant only
- Deduplicates events by `resourceId` (Set) to avoid double-processing
- Applies a 5 s delay between events before calling `saveWebhookXero`
- After processing all events, fetches full Xero invoice objects in batches of 10 and stores them on the webhook record via `addXeroInvoiceInformation`

### Status synchronization — `saveWebhookXero`
- `src/webhook/services/webhook.service.ts:58` — looks up internal invoice by `externalId`
- **PAID path** (`Invoice.StatusEnum.PAID`):
  - Creates a `markExternalInvoiceAsPaid` task via `TaskService` (line 94)
  - Updates `paymentToken.status = PAID` and sets `paidAt` from Xero's `fullyPaidOnDate` (line 105)
- **VOIDED path** (`Invoice.StatusEnum.VOIDED`):
  - Updates `invoice.status = voided` (line 113)
  - Updates `paymentToken.status = EXPIRED` (line 116)
  - If invoice originated from an auto-upgrade, calls `invoiceService.cancelSubscriptionUpgradeWhenInvoiceVoided` (line 125)
- Legacy cross-link: HTTP GET to `SLEEK_PAYMENT_API_URL/invoices/external-id/:resourceId` to populate `oldSystemLink` on the webhook record (line 136)

### Persistence
- `src/webhook/entities/webhook.entity.ts` — `Webhook` schema stored in `SleekPaymentDB`; fields: `source`, `resourceExternalId`, `eventType`, `payload`, `xeroInvoice`, `platformLink`, `oldSystemLink`, `retryCount`, `isReconciled`
- `src/webhook/repositories/webhook.repository.ts` — upserts by `resourceExternalId`

### Replay / queue
- `src/external-invoice/xero-webhook.processor.ts` — `ProcessXeroWebhook` Bull processor, `processXeroWebhook` job: re-fetches Xero invoice by `invoiceId` from the task data (used for retries)
- Replay endpoint (`POST /webhooks/:id/replay`) exists in service but is commented out in the controller

### DTOs
- `src/external-invoice/dtos/webhook-payload.dto.ts` — `XeroWebhookPayload` wraps an array of `XeroEvent` (fields: `resourceId`, `eventType`, `eventCategory`, `tenantId`, `eventDateUtc`, `resourceUrl`)
