# Reconcile Xero Invoice to Billing Platform

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Reconcile Xero Invoice to Billing Platform |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Ensures every paid Xero invoice is accounted for in the billing platform by linking it to a company and optionally provisioning subscriptions, preventing revenue leakage from unmatched invoice records. |
| **Entry Point / Surface** | Sleek Billings Admin > Unreconciled Invoices (`/unreconciled-invoices`) |
| **Short Description** | Operations users review a list of paid Xero invoices that have no matching record in the billing platform. For each invoice they can either reconcile it (linking it to a company, with or without creating subscriptions) or mark it as "considered reconciled" to dismiss it from the queue without creating a platform record. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero webhook ingestion (upstream — populates the unreconciled queue); billing platform company records (must exist to link against); customer subscription creation flow (optional downstream path triggered during reconcile via `createCustomerSubscriptionsFromInvoice`) |
| **Service / Repository** | sleek-billings-frontend; sleek-clm-monorepo/apps/sleek-billings-backend |
| **DB - Collections** | `webhooks` (read + updated: `isReconciled`, `createdSubscriptions`); `invoices` (created on reconcile with `invoiceOrigin: "reconcile"`, `status: "paid"`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Are markets scoped (SG/HK/AU/UK) or global? 2. What specific subscription types does `createCustomerSubscriptionsFromInvoice` create — any constraints on service codes? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/App.jsx:164` — route `unreconciled-invoices` renders `UnreconciledInvoicesList`
- `src/components/Navbar.jsx:120` — nav item `Unreconciled Invoices` at path `/unreconciled-invoices`
- `src/data/nav-rail-items.js:38` — nav rail item `navigation: "/unreconciled-invoices"`

### UI component
- `src/pages/UnreconciledInvoices/UnreconciledInvoicesList.jsx`
  - `fetchInvoices()` — calls `sleekBillingsApi.getWebhooks({ source: "xero", platformLink: false, paidInvoices: true })` to load the queue
  - Filters: free-text search (invoice number, customer name, status, reference), system-status filter (`oldSystem` / `platformLink` / `onlyXero`), date range
  - Sort: by `eventDateUtc` asc/desc
  - **Reconcile flow** (`handleReconcileClick` / `ReconcileModal`): opens modal showing full invoice detail (line items, payment summary); user selects reconcile option (with or without subscriptions) and optionally enters a `companyId` when no `oldSystemLink` exists; submits via `handleReconcile(createSubscriptions)`
  - **Consider-as-reconciled flow** (`handleConsiderReconciledClick` / `ConsiderReconciledDialog`): confirmation dialog; marks invoice as reconciled and removes it from the queue without creating a billing platform invoice

### API calls (`src/services/api.js`)
| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/webhooks?source=xero&platformLink=false&paidInvoices=true` | Fetch unreconciled Xero invoice webhooks |
| `POST` | `/invoices/reconcile?webhookId={id}` | Reconcile invoice; body `{ createSubscriptions, companyId }` |
| `POST` | `/invoices/consider-as-reconciled?webhookId={id}` | Mark invoice as reconciled without full platform link |

### Backend controller (`sleek-billings-backend`)
- `src/invoice/controllers/invoice.controller.ts:170` — `POST /invoices/reconcile`
  - Guards: `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)`
  - Delegates to `invoiceService.reconcileInvoice(webhookId, { createSubscriptions, companyId })`
- `src/invoice/controllers/invoice.controller.ts:182` — `POST /invoices/consider-as-reconciled`
  - Guards: `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)`
  - Delegates to `invoiceService.considerAsReconciled(webhookId)`

### Backend service logic (`invoice.service.ts:1957`)
- `reconcileInvoice()`:
  1. Loads the webhook from `webhookRepository`
  2. Initialises Xero client (`xeroService.init`)
  3. Transforms Xero line items into internal invoice payload (`invoiceOrigin: "reconcile"`, `status: "paid"`)
  4. Resolves `companyId` from request body or falls back to `webhook.oldSystemLink.companyId`
  5. Looks up company admin user via `companyUserService.getCompanyAdmin(companyId)`
  6. Creates invoice in `invoices` collection via `invoiceRepository.create()`
  7. If `createSubscriptions: true` → fires `customerSubscriptionService.createCustomerSubscriptionsFromInvoice()`
  8. Marks webhook `isReconciled: true`, `createdSubscriptions: <bool>` via `webhookRepository.updateById()`
  9. Publishes payment-done event via `publishPaymentDoneEvent()`
- `considerAsReconciled()`:
  1. Loads webhook, sets `isReconciled: true`, `createdSubscriptions: false` — no invoice created

### Webhook schema (`src/webhook/entities/webhook.entity.ts`)
Key fields: `source`, `payload` (incl. `eventDateUtc`), `xeroInvoice` (full Xero invoice object), `platformLink` (`{ type, id, companyId, invoiceStatus }`), `oldSystemLink` (`{ type, id, companyId, userId }`), `isReconciled`, `createdSubscriptions`

### Data shape observed in UI
- `webhook.xeroInvoice` — invoiceNumber, reference, status, date, dueDate, fullyPaidOnDate, contact (name, contactID, emailAddress), lineItems (description, itemCode, quantity, unitAmount, taxAmount, lineAmount), subTotal, totalTax, total, amountPaid, amountDue
- `webhook.platformLink` — present if invoice already exists in billing platform
- `webhook.oldSystemLink` — present if invoice was found in the legacy billing system (pre-migration)
