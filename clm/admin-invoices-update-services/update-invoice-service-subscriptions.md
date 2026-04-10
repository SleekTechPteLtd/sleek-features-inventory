# Update Invoice Service Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Update Invoice Service Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Ensures subscription periods are correctly set for services tied to an invoice — particularly after reconciliation, when an invoice is marked done but associated subscriptions need their billing cycle (start date and duration) refreshed to reflect actual entitlements. |
| **Entry Point / Surface** | Sleek Admin App > `/admin/invoices/update-services/?iid=<invoiceId>`; typically navigated to from the Reconcile Invoice flow when the invoice status is `done` and the company has overdue subscriptions |
| **Short Description** | Admins view all services linked to an invoice (excluding incorporation, incorporation-discount, and transfer), edit each service's subscription duration (3, 6, or 12 months) and start date, then submit to refresh all subscriptions in parallel via `PUT /admin/company-services/{id}/edit-and-refresh-subscription`. After saving, the admin is redirected to the company's billing page. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Reconcile External Invoice or Credit Note (upstream trigger); `billing.new_ui` feature flag in `platformConfig.cmsAppFeatures.companies.billing` (controls which form variant renders); Company Overview Billing tab (`/admin/company-overview/?currentPage=Billing&tab=1`) as post-submit destination for new UI |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service handles `PUT /admin/company-services/{id}/edit-and-refresh-subscription` and what collections does it write to? Is the `new_ui` flag fully rolled out or still being phased in? Are there markets where this flow does not apply? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `views/admin/invoices/update-services/index.js` — top-level page component; renders inside `AdminLayout` with `secondaryPermissionKey="invoices"` (admin-only gate); checks `platformConfig.cmsAppFeatures.companies.billing.new_ui` to decide which form variant to mount.

### Form variants
- `views/admin/invoices/update-services/update-services-form.js` (`UpdateServicesForm`) — legacy Blueprint.js UI; duration dropdown + date picker per service; "Refresh Subscription" submit button; redirects to `/admin/companies/edit/?cid=...` on success.
- `views/admin/invoices/update-services/new-update-services-form.js` (`NewUpdateServicesForm`) — Material-UI redesign with `MaterialSelect` and `MaterialDateInput`; same business logic; redirects to `/admin/company-overview/?cid=...&currentPage=Billing&tab=1` on success; adds a back/cancel button to the billing invoice page.

### API calls
- `GET /admin/invoices/{invoiceId}/get-services` (`api.getServicesByInvoice`) — loads the invoice record and all associated company services; invoked on mount and after submit to refresh state.
- `PUT /admin/company-services/{companyServiceId}/edit-and-refresh-subscription` (`api.editAndRefreshSubscription`) — sends `{ duration, start_at }` per service; all service updates are fired in parallel via `Promise.all`.

### Business rules in code
- Services of type `incorporation`, `incorporation-discount`, and `transfer` are excluded from the form.
- **Mailroom** and **secretary** services: duration field is locked to 12 months (`setDurationTo12Months`).
- **Corp-sec** variants (`corp-sec-1-shareholder` through `corp-sec-31-to-50-shareholder`): start date field is editable regardless of existing subscription `overdue_at`; other services lock the start date if an active subscription with `overdue_at` exists (`has_existing_subscription` flag).
- Duration options: 3, 6, or 12 months.

### Related feature noted in reconcile flow
- `views/admin/invoices/reconcile/` references the update-services path as a downstream step when a reconciled invoice is `done` and the company has overdue subscriptions.
