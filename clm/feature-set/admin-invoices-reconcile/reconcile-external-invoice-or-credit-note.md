# Reconcile External Invoice or Credit Note

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Reconcile External Invoice or Credit Note |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Closes the gap between the external billing system and the platform subscription record by allowing admins to link a Sleek or Managed Service invoice/credit note to a company account, keeping billing state consistent across systems. |
| **Entry Point / Surface** | Sleek Admin App > `/admin/invoices/reconcile/?cid=<companyId>`; also reachable from Company Overview > Billing tab (billing-subscription and billing-invoice views) |
| **Short Description** | Admins select a company, choose a document type (Sleek Invoice, Sleek Credit Note, Managed Service Invoice, or Managed Service Credit Note), and enter an external ID. The system validates that the ID prefix matches the selected type and company tier (partner vs non-partner), then POSTs to `/admin/invoices/reconcile` to link the external document to the company's subscription record. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `getAdminCompanyByIdSubscriptions` (loads company subscription state before form); `billing.refresh_subscriptions` feature flag (controls post-reconciliation redirect behaviour); Update Services flow (`/admin/invoices/update-services/`) triggered when reconciled invoice is `done` and company has overdue subscriptions; Company Overview Billing tab |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service handles `POST /admin/invoices/reconcile` and what collections does it write to? Is this feature available in all markets or SG/HK only? What triggers an invoice to land in `status: done` vs other states? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `views/admin/invoices/reconcile/index.js` — top-level page component; fetches company subscriptions via `getAdminCompanyByIdSubscriptions(cid)` on mount; renders `CreateInvoiceForm` inside `AdminLayout` with `secondaryPermissionKey="invoices"` (admin-only gate).

### Form logic
- `views/admin/invoices/reconcile/create-invoice-form.js` — `CreateInvoiceForm`:
  - Loads company details (`api.getCompany`) to determine if company is a **partner** (Managed Service) or non-partner (Sleek).
  - Filters invoice type dropdown by company tier: partner companies see `msInvoice` / `msCreditNote` only; non-partner companies see `invoice` / `creditNote` only.
  - Validates `external_id` prefix against type before submitting:
    - `invoice` → must start with `INV-` (but not `INV-MS-`)
    - `creditNote` → must start with `CN-`
    - `msInvoice` → must start with `INV-MS-`
    - `msCreditNote` → must start with `CN-`
  - "Do not Notify Client" checkbox shown only for `invoice` type; suppresses email notification to the client when checked.
  - On success with `billing.refresh_subscriptions` flag enabled: redirects to `/admin/invoices/update-services/?iid=<invoiceId>` if invoice status is `done` and company has overdue subscriptions; otherwise redirects to Company Overview Billing tab.
  - Calls `api.reconcileInvoice({ body: JSON.stringify({ company_id, external_id, invoice_type, do_not_notify }) })`.

### Constants
- `views/admin/invoices/constants/invoices-constants.js` — defines:
  - `INVOICE_TYPES`: `invoice`, `creditNote`, `msInvoice`, `msCreditNote`
  - `INVOICE_VALUE_PATTERN`: `INV-`, `CN-`, `INV-MS-`

### API
- `utils/api.js:1675` — `reconcileInvoice()` → `POST /admin/invoices/reconcile`

### Additional call sites (same API, different UI surfaces)
- `views/admin/company-overview/billing-subscription.js:863`
- `views/admin/company-overview/billing-invoice.js:335`
