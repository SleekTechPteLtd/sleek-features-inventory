# Manage subscription services on invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage subscription services on invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin with **invoices** secondary permission) |
| **Business Outcome** | Operations staff can align each billed service’s subscription term length and effective start with what was agreed, so renewals and downstream billing stay consistent with the invoice. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/invoices/update-services/?iid=<invoiceId>`** (webpack entry `admin/invoices/update-services/index`). Reached after **invoice reconcile** success when routing sends operators here, or from **Company overview → Billing** flows that redirect with `iid`. `AdminLayout`: `sidebarActiveMenuItemKey="companies"`, `secondaryPermissionKey="invoices"`, `hideDrawer`. |
| **Short Description** | Reads **`iid`** from the query string, loads invoice and line services, drops incorporation/discount/transfer-only rows, and shows one block per service with **duration** (3, 6, or 12 months; **mailroom** and **secretary** fixed to 12) and **start date**. If a service already has a subscription with **`overdue_at`**, the start field is read-only for non–corp-sec tiered services (initial value uses **`overdue_at`**). Submit calls **`editAndRefreshSubscription`** for every listed service with **`duration`** and **`start_at`**, then redirects: legacy form to **`/admin/companies/edit/?cid=`**; new billing UI to **company overview → Billing** tab. Which form renders depends on CMS **`companies.billing.new_ui`**. |
| **Variants / Markets** | Multi-tenant CMS feature flags (`platformConfig`, `getAppFeatureProp`). Per-market SG/HK/UK/AU not encoded in this view — **Unknown**. |
| **Dependencies / Related Flows** | **`api.getServicesByInvoice`** → **`GET /admin/invoices/:invoiceId/get-services`**. **`api.editAndRefreshSubscription`** → **`PUT /admin/company-services/:companyServiceId/edit-and-refresh-subscription`** (JSON body: **`duration`**, **`start_at`**). Upstream: **Reconcile external invoices** (`/admin/invoices/reconcile/`) and company billing screens that redirect with **`iid`**. Downstream: company services and subscriptions in the main API — not visible in sleek-website. |
| **Service / Repository** | **sleek-website**: `src/views/admin/invoices/update-services/index.js`, `update-services-form.js`, `new-update-services-form.js`, `src/utils/api.js`. **Main API** (sleek-back or equivalent): admin invoice services and company-service subscription refresh — not in this repo. |
| **DB - Collections** | **Unknown** (invoice and company-service persistence lives in backend services; not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | **`refreshServices`** loops services with **`forEach`** and calls **`setState`** per iteration (stale closure risk vs intended merge). Toast message spells **“succcessfully”**. Whether backend validates **`duration`** / **`start_at`** against invoice state beyond this UI — **none** for product owner if backend contract is documented elsewhere. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/invoices/update-services/index.js` (`UpdateServicesView`)

- Mounts **`getUser`**; loads **`platformConfig`** from **`store`** and error copy from **`getAppFeatureProp`** (`messages.errors.GENERAL`).
- **`getBodyContent`**: if CMS **`companies.billing.new_ui`** is enabled → **`NewUpdateServicesForm`**; else **`UpdateServicesForm`**. Both receive **`renderToastMessage`**.

### `src/views/admin/invoices/update-services/update-services-form.js` (`UpdateServicesForm`)

- **`refreshServices`**: **`querystring.parse`** → **`api.getServicesByInvoice(query.iid)`**; filters out **`incorporation`**, **`incorporation-discount`**, **`transfer`**.
- Initializes form from each service: **`duration`**, **`start_at`** from **`subscription[0].overdue_at`** when present (except **corp-sec-\*** tier services use **`service.start_at`**), sets **`_has_existing_subscription`** to lock the date field when applicable.
- **`handleSubmit`**: for each service, **`api.editAndRefreshSubscription(service._id, { body: JSON.stringify({ duration, start_at }) })`**, then **`refreshServices`**, then **`window.location = "/admin/companies/edit/?cid=" + invoice.company`**, then success toast.

### `src/views/admin/invoices/update-services/new-update-services-form.js` (`NewUpdateServicesForm`)

- Same data load, filter, and submit contract as legacy form; Material UI controls (**`MaterialSelect`**, **`MaterialDateInput`**), **`VerticalCard`** wrapper.
- **`backToBillingInvoice`** and post-submit redirect: **`/admin/company-overview/?cid=…&currentPage=Billing&tab=1`** instead of company edit.
- Submit triggered from primary button calling **`handleSubmit`** (not native form submit for the Material actions row).

### `src/utils/api.js`

- **`getServicesByInvoice`**: **`GET ${getBaseUrl()}/admin/invoices/${invoiceId}/get-services`** via **`getResource`**.
- **`editAndRefreshSubscription`**: **`PUT ${getBaseUrl()}/admin/company-services/${companyServiceId}/edit-and-refresh-subscription`** via **`putResource`**.

### Related navigation (same repo)

- **`src/views/admin/invoices/reconcile/create-invoice-form.js`**, **`src/views/admin/company-overview/billing-invoice.js`**, **`billing-invoice.microservice.js`**: success redirects to **`/admin/invoices/update-services/?iid=`** + invoice id.
