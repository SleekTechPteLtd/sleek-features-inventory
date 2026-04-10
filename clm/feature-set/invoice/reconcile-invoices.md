# Reconcile Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Reconcile Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Billing Admin (BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin) |
| **Business Outcome** | Ensure billing records are accurate by matching payment webhook data from Xero against internal invoices, with the option to auto-create subscriptions upon reconciliation or mark a webhook as reconciled without creating a new invoice |
| **Entry Point / Surface** | Internal admin API — `POST /invoices/reconcile` and `POST /invoices/consider-as-reconciled`; typically triggered from an ops/admin billing tool or unreconciled-invoices dashboard |
| **Short Description** | Allows authorised billing admins to reconcile a payment webhook from Xero: it creates an internal invoice in paid status (with optional subscription creation) and marks the webhook as reconciled. A lighter variant marks the webhook as reconciled without creating an invoice, for edge cases where no new invoice is needed. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: Xero payment webhooks (`webhooks` collection); Xero API (invoice data, online URL); Downstream: `PaymentDoneEvent` published via dataStreamerService (triggers subscription activation and onboarding emails); `customerSubscriptionService.createCustomerSubscriptionsFromInvoice` (optional); unreconciled-invoices dashboard (`clm/unreconciled-invoices`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices`, `webhooks`, `services` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which UI surface triggers these endpoints (admin portal, internal ops tool, or CLI)? Which markets are in scope — SG/HK/UK/AU? Is `consider-as-reconciled` used for manual overrides or specific business scenarios? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints (`invoice/controllers/invoice.controller.ts`)

| Method | Route | Guard |
|---|---|---|
| `POST` | `/invoices/reconcile?webhookId=<id>` | `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)` |
| `POST` | `/invoices/consider-as-reconciled?webhookId=<id>` | `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)` |

### `reconcileInvoice` flow (`invoice/services/invoice.service.ts`, line 1959)

1. Fetches webhook by `webhookId` from `webhooks` collection.
2. Initialises Xero client (`xeroService.init`).
3. Transforms Xero invoice line items into internal invoice payload (resolves service codes from `services` collection).
4. Resolves `companyId` from options or `webhook.oldSystemLink.companyId`.
5. Looks up company admin (`companyUserService.getCompanyAdmin`) to assign `userId`.
6. Creates invoice in `invoices` collection with `status: paid` and `invoiceOrigin: reconcile`.
7. Optionally calls `customerSubscriptionService.createCustomerSubscriptionsFromInvoice`.
8. Marks webhook `isReconciled: true` in `webhooks` collection.
9. Publishes `PaymentDoneEvent` via `dataStreamerService`.

### `considerAsReconciled` flow (`invoice/services/invoice.service.ts`, line 2049)

1. Fetches webhook by `webhookId`.
2. Sets `isReconciled: true`, `createdSubscriptions: false` on webhook — no invoice is created.

### Schema fields of note

- `Invoice.invoiceOrigin = 'reconcile'` — flags this invoice as reconciliation-sourced.
- `Webhook.isReconciled` — boolean flag updated by both flows.
- `Webhook.xeroInvoice` — raw Xero invoice payload used to build the internal invoice.
- `Webhook.oldSystemLink` — carries legacy `companyId`/`userId` when the webhook originated from an older system.
