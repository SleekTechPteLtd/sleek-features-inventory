# Reconcile external invoices to company billing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Reconcile external invoices to company billing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / billing staff (Sleek Admin users with **invoices** secondary permission) |
| **Business Outcome** | Operators can attach the correct external billing document to a company so internal records and client billing stay aligned with Sleek or managed-service source documents, with control over client email and where to go next after success. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/invoices/reconcile/?cid=<companyId>`** (webpack entry `admin/invoices/reconcile/index`). Linked from **Company overview → Billing** and **Companies → Edit** (“Reconcile” style actions). `AdminLayout` with `sidebarActiveMenuItemKey="companies"`, `secondaryPermissionKey="invoices"`. |
| **Short Description** | Page loads company context from `cid`, fetches admin subscriptions for routing logic, and renders **Create Invoice** form: company lookup, document **Type** (Sleek invoice/credit note vs managed-service invoice/credit note based on partner flag), **External ID** with prefix validation (`INV-`, `CN-`, `INV-MS-`), optional **Do not notify client** for Sleek invoice type, then **POST** reconcile. On success, CMS feature flags choose redirect to company billing tab, **Update services** (`/admin/invoices/update-services/?iid=…`), or legacy company edit—depending on `refresh_subscriptions`, subscription `overdue_at`, invoice status, and type. |
| **Variants / Markets** | Multi-tenant CMS (`platformConfig`, `getAppFeatureProp`). Partner companies see managed-service types; non-partner see Sleek types. Markets not encoded in this view — **Unknown** (typical Sleek tenants SG, HK, UK, AU elsewhere in inventory). |
| **Dependencies / Related Flows** | **`api.reconcileInvoice`** → main API **`POST /admin/invoices/reconcile`** (body: `company_id`, `external_id`, `invoice_type`, `do_not_notify`). **`getAdminCompanyByIdSubscriptions`** → **`GET /v2/admin/companies/:id/subscriptions`** for post-success routing. **`api.getCompany`** for company name/partner. Company overview billing / **billing-invoice** flows reuse the same reconcile API with richer dialogs. Related: subscription reconcile (`reconcileSubscriptionRequest`), recovery file reconcile (different feature). |
| **Service / Repository** | **sleek-website**: `src/views/admin/invoices/reconcile/index.js`, `create-invoice-form.js`, `src/utils/api.js` (`reconcileInvoice`, `getAdminCompanyByIdSubscriptions`, `getCompany`, `getCompanies`). **sleek-back** (or equivalent main API): admin invoices reconcile handler and persistence — not in this repo. |
| **DB - Collections** | **Unknown** (reconcile persistence lives in backend services; not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | **`CreateInvoiceForm`** calls **`this.props.showErrorDialog`** when `refresh_subscriptions` is disabled, but **`ReconcileInvoice`** in `index.js` does not pass **`showErrorDialog`**—likely dead path or runtime issue; confirm intended UX. Post-success condition on line 128 uses **`invType !== CREDIT_NOTE || invType !== MS_CREDIT_NOTE`** (always true for a single type); confirm whether logic matches backend intent. Exact backend collections and idempotency rules for reconcile. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/invoices/reconcile/index.js` (`ReconcileInvoice`)

- Renders into `#root`; `AdminLayout` with `hideDrawer`, `sidebarActiveMenuItemKey="companies"`, `secondaryPermissionKey="invoices"`.
- Reads **`cid`** from `window.location.search` via `querystring`.
- **`getAdminCompanyByIdSubscriptions(query.cid)`** → subscriptions into state for child.
- Passes **`CreateInvoiceForm`** props: **`renderInvoiceMessage`**, **`subscriptions`**, **`companyId`**, **`isNewCompanyOverviewUIEnabled`** (from CMS `companies.overview.new_ui`).
- **`getUser`** from admin common; loads error copy from **`getAppFeatureProp`** (`messages.errors.GENERAL`) for generic alert.

### `src/views/admin/invoices/reconcile/create-invoice-form.js` (`CreateInvoiceForm`)

- **`api.getCompany(companyId)`** on mount → **`selectedCompany`** (`_id`, `name`, **`partner`**).
- **Type / ID validation** before submit: **`INVOICES_CONSTANTS`** — patterns **`INV-`**, **`CN-`**, **`INV-MS-`**; partner vs non-partner branches swap expected Sleek vs managed-service labels in error strings (`ADMIN_ERROR_MESSAGES.INVALID_INVOICE_ATTACHMENT`).
- Submit body: **`company_id`**, **`external_id`**, **`invoice_type`**, **`do_not_notify`** (from checkbox state **`isEnabled`**; checkbox only when type is Sleek **`invoice`**).
- **`api.reconcileInvoice({ body: JSON.stringify(data) })`**.
- Success routing uses **`getPlatformConfig`** → **`companies.billing.refresh_subscriptions`**. If disabled: attempts **`showErrorDialog`** then redirect to **`/admin/company-overview/?cid=…&currentPage=Billing&tab=1`**. If enabled: may redirect to **`/admin/invoices/update-services/?iid=`** + **`response.data.invoice._id`** when subscriptions have **`overdue_at`** or invoice **`status === "done"`** with type branch; else company overview billing or **`/admin/companies/edit/?cid=`**.
- **`hideDropdownValue`**: partner → show **`msInvoice`**, **`msCreditNote`** only; else **`invoice`**, **`creditNote`**.

### `src/utils/api.js`

- **`reconcileInvoice`**: **`POST ${getBaseUrl()}/admin/invoices/reconcile`** via **`postResource`**.
- **`getAdminCompanyByIdSubscriptions`**: **`GET ${getBaseUrl()}/v2/admin/companies/${companyId}/subscriptions`**.

### Related navigation (same repo)

- **`src/views/admin/company-overview/billing.js`**: link **`/admin/invoices/reconcile/?cid=`** + company id.
- **`src/views/admin/companies/edit/index.js`**: same reconcile href pattern.

### Constants

- **`src/views/admin/invoices/constants/invoices-constants.js`**: **`INVOICE_TYPES`**, **`INVOICE_VALUE_PATTERN`**.
