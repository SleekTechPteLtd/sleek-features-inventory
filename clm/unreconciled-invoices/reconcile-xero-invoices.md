# Reconcile Xero invoices with billing platform

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Reconcile Xero invoices with billing platform |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operations to identify and close gaps between paid Xero invoices and the internal billing platform, so revenue records stay in sync across both systems |
| **Entry Point / Surface** | Sleek Billings Admin > Unreconciled Invoices |
| **Short Description** | Displays a filterable list of paid Xero invoices that have no matching billing platform record. Operations users can inspect invoice details, trigger reconciliation (with or without creating subscriptions), or manually mark an invoice as considered reconciled. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Billing backend API (`/webhooks`, `/invoices/reconcile`, `/invoices/consider-as-reconciled`); Xero (source of invoices via webhook events); Sleek Admin App (company overview deep-link for matched records) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend (inferred) |
| **DB - Collections** | Unknown (frontend only; `webhooks` and `invoices` collections inferred from API routes `/webhooks` and `/invoices/reconcile`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets / Xero tenants are in scope? Currency symbol is read from localStorage but no market filter exists in the UI. 2. What does the backend do when `createSubscriptions=true` — does it create records in a third system? 3. Is "consider as reconciled" a soft-delete / flag only, or does it push state back to Xero? 4. What is the `oldSystemLink` — does it refer to a pre-Billing Beta billing system? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/UnreconciledInvoices/UnreconciledInvoicesList.jsx` — main page component
- `src/services/api.js` — API client (`sleekBillingsApi`)

### API calls (frontend → backend)

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/webhooks?source=xero&platformLink=false&paidInvoices=true` | Load paid Xero webhooks with no platform link |
| `POST` | `/invoices/reconcile?webhookId={id}` | Trigger reconciliation; body: `{ createSubscriptions: bool, companyId?: string }` |
| `POST` | `/invoices/consider-as-reconciled?webhookId={id}` | Mark invoice as manually reconciled (no platform match needed) |

### UI capabilities

- **Search** — free-text across `invoiceNumber`, `contact.name`, `status`, `reference` (debounced 500 ms)
- **System status filter** — All / Not found in Billing Beta (`oldSystemLink` present) / Has Platform Link (`platformLink` present) / Only in XERO App (neither link)
- **Date range filter** — filters on `payload.eventDateUtc`
- **Sort** — by event date, ascending or descending
- **Reconcile modal** — shows full invoice detail (line items, payment summary, customer info); user picks reconcile option (with or without subscriptions) and optionally enters a company ID when no `oldSystemLink` exists
- **Consider reconciled dialog** — confirmation before calling `considerAsReconciled`; removes invoice from list after success
- **View Company** — deep-links to `VITE_ADMIN_APP_URL/admin/company-overview/?cid=...&currentPage=Billing+Beta` for any webhook that has `oldSystemLink` or `platformLink`

### Webhook data shape (inferred from UI rendering)

```
webhook._id                          — record ID
webhook.payload.eventDateUtc         — Xero event timestamp
webhook.xeroInvoice.invoiceNumber    — Xero invoice number
webhook.xeroInvoice.reference        — Xero reference field
webhook.xeroInvoice.status           — PAID / DRAFT / etc.
webhook.xeroInvoice.contact          — { name, contactID, emailAddress }
webhook.xeroInvoice.lineItems[]      — { description, itemCode, quantity, unitAmount, taxAmount, lineAmount }
webhook.xeroInvoice.{subTotal, totalTax, total, amountPaid, amountDue, fullyPaidOnDate}
webhook.oldSystemLink                — { companyId } if matched to legacy billing system
webhook.platformLink                 — { companyId, invoiceStatus } if matched to Billing Beta
```

### Auth surface
Bearer JWT or raw token from `localStorage("auth")`; `App-Origin: admin` or `admin-sso` header — internal ops admin tool only.
