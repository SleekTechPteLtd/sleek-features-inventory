# Flag Invoice as Considered Reconciled

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Flag invoice as considered reconciled |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations staff can dismiss Xero invoices that already have a platform link from the unreconciled queue, keeping the queue focused on invoices that genuinely need action. |
| **Entry Point / Surface** | Sleek Billings Admin > Unreconciled Invoices — "Consider reconciled" row action (visible only when `platformLink` is set on the webhook record) |
| **Short Description** | When a Xero invoice has already been linked to a platform company record but still appears in the unreconciled queue, an operations user can mark it as "considered reconciled". The backend sets `isReconciled: true` on the webhook record without creating a new invoice or subscriptions, and the invoice is removed from the queue on the next list refresh. |
| **Variants / Markets** | SG (confirmed via billings-sg-sit spec); other markets Unknown |
| **Dependencies / Related Flows** | Upstream: Xero webhook ingestion (paid invoice events); Reconcile Invoice flow (for invoices without a platform link). Backend: `sleek-billings-backend` `InvoiceController.considerAsReconciled` → `InvoiceService.considerAsReconciled` → `WebhookRepository.updateById` |
| **Service / Repository** | sleek-billings-frontend, sleek-clm-monorepo (sleek-billings-backend) |
| **DB - Collections** | `webhooks` (SleekPaymentDB — Mongoose model `Webhook`; fields written: `isReconciled`, `createdSubscriptions`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Is this action reversible (no undo endpoint found in code)? 2. The UI fetches `/webhooks?platformLink=false` but shows "Consider reconciled" only when `webhook.platformLink` is truthy client-side — confirm whether the API filter behaviour matches the intent or if the filter is effectively ignored server-side. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI trigger
- `sleek-billings-frontend/src/pages/UnreconciledInvoices/UnreconciledInvoicesList.jsx:782–787` — "Consider reconciled" button rendered only when `webhook.platformLink` is truthy; calls `handleConsiderReconciledClick(webhook)`.
- `UnreconciledInvoicesList.jsx:172–175` — `handleConsiderReconciledClick` sets `selectedInvoice` and opens `showConsiderReconciledDialog`.
- `UnreconciledInvoicesList.jsx:177–190` — `handleConsiderAsReconciled` calls `sleekBillingsApi.considerAsReconciled(selectedInvoice._id, {})`, then refreshes list via `fetchInvoices()`.

### Confirmation dialog
- `UnreconciledInvoicesList.jsx:468–543` — `ConsiderReconciledDialog` component; shows invoice number, contact name, and total; confirms two effects: "Mark the invoice as reconciled in the system" and "Remove it from the unreconciled invoices list."

### API call (frontend)
- `sleek-billings-frontend/src/services/api.js:238–246` — `considerAsReconciled(webhookId, options)`: `POST /invoices/consider-as-reconciled?webhookId=${webhookId}` with empty body `{}`.

### Backend controller
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/invoice/controllers/invoice.controller.ts:182–188`
  - Route: `POST consider-as-reconciled`
  - Guards: `@Auth()` + `@GroupAuth(Group.BillingSuperAdmin, Group.BillingOperationsAdmin, Group.SalesAdmin)`
  - Calls `invoiceService.considerAsReconciled(webhookId)`.

### Backend service
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/invoice/services/invoice.service.ts:2047–2062`
  - Looks up webhook by ID via `webhookRepository.findById(webhookId)`; throws `NotFoundException` if missing.
  - Calls `webhookRepository.updateById(webhookId, { isReconciled: true, createdSubscriptions: false })`.
  - No new invoice is created; no Kafka event published (unlike the full reconcile flow).

### DB schema
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/webhook/entities/webhook.entity.ts` — `Webhook` class decorated with `@Schema`; no explicit `collection` name → Mongoose default `webhooks`.
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/webhook/repositories/webhook.repository.ts` — `@InjectModel(Webhook.name, SleekPaymentDB)`.
- Fields written by this action: `isReconciled: boolean`, `createdSubscriptions: boolean`.

### Auth surface
- Bearer JWT required; `App-Origin: admin` or `admin-sso`. Restricted to `BillingSuperAdmin`, `BillingOperationsAdmin`, `SalesAdmin` groups.

### Unreconciled invoice queue context
- `UnreconciledInvoicesList.jsx:41–45` — Queue populated by `GET /webhooks?source=xero&platformLink=false&paidInvoices=true`.
- `UnreconciledInvoicesList.jsx:86–103` — Client-side "Has Platform Link" filter surfaces invoices where `platformLink` is truthy (the subset eligible for this action).
