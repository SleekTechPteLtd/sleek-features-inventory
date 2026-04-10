# Review Unreconciled Xero Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Unreconciled Xero Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives operations teams a single view of paid Xero invoices that have not yet been matched to the internal billing platform, enabling them to spot and act on revenue discrepancies before they cause downstream issues. |
| **Entry Point / Surface** | Sleek Billings Admin > Unreconciled Invoices (`/unreconciled-invoices`) |
| **Short Description** | Operations users browse a filtered list of paid Xero invoices that lack a corresponding billing-platform record. Filters include free-text search (invoice number, customer name, status, reference), a system-status selector (all / Not found in Billing Beta / Has Platform Link / Only in XERO), and a start/end date range. Results are sortable by event date. From the list, users can drill into invoice details, trigger reconciliation, or mark an invoice as considered-reconciled. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Reconcile Xero Invoice to Billing Platform (`reconcile-xero-invoice-to-billing-platform.md`), Flag Invoice as Considered Reconciled (`flag-invoice-as-considered-reconciled.md`), Xero webhook ingestion (`POST /webhooks/xero`), Billing platform invoice records |
| **Service / Repository** | sleek-billings-frontend, sleek-clm-monorepo/apps/sleek-billings-backend |
| **DB - Collections** | `webhooks` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Market/region scope is not encoded in the UI or API query — unclear whether this view covers SG only or all tenants. The `SWITCH_TO_SLEEK_BILLINGS` feature flag gates Xero webhook ingestion; unclear if the list view is also gated behind it. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend
- `sleek-billings-frontend/src/pages/UnreconciledInvoices/UnreconciledInvoicesList.jsx`
  - Calls `sleekBillingsApi.getWebhooks({ source: "xero", platformLink: false, paidInvoices: true })` on mount and after filter changes.
  - Client-side filtering by: search query (invoice number, contact name, status, reference), system-status enum (`oldSystem` / `platformLink` / `onlyXero`), and UTC event date range.
  - Sortable by `eventDateUtc` (asc/desc toggle).
  - System-status badge logic: `webhook.oldSystemLink` → "Not found in Billing Beta"; `webhook.platformLink.invoiceStatus` mismatch → "Discrepancy between XERO and Billing Beta"; no link → "Only in XERO App".
  - Action buttons per row: **Reconcile** (when no `platformLink`) and **Consider reconciled** (when `platformLink` present), both delegating to sibling features.
  - Deep-link to Admin company overview via `VITE_ADMIN_APP_URL/admin/company-overview/?cid=...&currentPage=Billing+Beta`.

- `sleek-billings-frontend/src/services/api.js`
  - `sleekBillingsApi.getWebhooks(options)` → `GET /webhooks?source=xero&platformLink=false&paidInvoices=true`
  - `sleekBillingsApi.reconcileInvoice(webhookId, options)` → `POST /invoices/reconcile?webhookId={id}`
  - `sleekBillingsApi.considerAsReconciled(webhookId, options)` → `POST /invoices/consider-as-reconciled?webhookId={id}`

### Backend — Webhook query
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/webhook/controllers/webhook.controller.ts`
  - `GET /webhooks` (`@Auth()`) — calls `webhookService.getUnprocessedWebhooks(source, platformLink, paidInvoices)`.
  - `POST /webhooks/xero` — HMAC-verified Xero event ingestion; guarded by `SWITCH_TO_SLEEK_BILLINGS` feature flag.

### Backend — Reconcile actions
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/invoice/controllers/invoice.controller.ts`
  - `POST /invoices/reconcile` — `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)`.
  - `POST /invoices/consider-as-reconciled` — same group auth.

### Schema
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/webhook/entities/webhook.entity.ts`
  - Collection: `webhooks`
  - Key fields: `source`, `eventType`, `payload` (includes `eventDateUtc`), `xeroInvoice` (invoiceNumber, contact, status, lineItems, totals), `platformLink` (companyId, invoiceStatus), `oldSystemLink` (companyId), `isReconciled`, `createdSubscriptions`.
  - Indexes: `source`, `processed`, `resourceExternalId`.
