# Provision company services with linked invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Provision company services with linked invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (internal staff — Sleek Admin surface) |
| **Business Outcome** | Staff can onboard a company onto secretary, director, or mailroom-style services with a billing anchor by creating the invoice first, then attaching it to the new company service so admin billing and service records stay aligned. |
| **Entry Point / Surface** | **sleek-website** admin: **Create Service** page (webpack entry `admin/services/new`; route pattern **`/admin/services/new`** consistent with sibling admin services views). **`AdminLayout`**: `sidebarActiveMenuItemKey="services"`; back link to **`/admin/services/`**. |
| **Short Description** | Two-step submit: **`POST /admin/invoices`** creates an invoice (title, URL, transaction id, number, company, total amount, status), then **`POST /admin/company-services`** creates a company service with **`company_id`**, **`service`** (secretary / director / mailroom), **`duration`** (months), **`start_at`**, and **`invoices`** set to the new invoice id. Company is chosen via searchable admin company list; invoice fields are entered on the same form. |
| **Variants / Markets** | **Unknown** (API base defaults to SG production host in code; no per-market branching in these views). |
| **Dependencies / Related Flows** | **`api.createInvoice`** → **`POST ${getBaseUrl()}/admin/invoices`**. **`api.createCompanyService`** with **`admin: true`** → **`POST ${getBaseUrl()}/admin/company-services`** (see **`postResource`** path rewrite). Loads companies via **`api.getCompanies`** (initial list and admin search). Upstream: company directory and invoice creation in main API. Downstream: company service and subscription flows (e.g. **edit-and-refresh-subscription** on other admin screens) — not implemented in this file. |
| **Service / Repository** | **sleek-website**: `src/views/admin/services/new.js`, `form-segment-service.js`, `form-segment-invoice.js`, `src/utils/api.js`. **Main API** (backend): invoice and company-service persistence — not in this repo. |
| **DB - Collections** | **Unknown** (MongoDB or other stores for invoices and company services live in backend services; not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | **`makePostInvoiceRequest`** sends **`external_id`** from form state, but **`form-segment-invoice`** does not expose an **`external_id`** field — value may be undefined unless set elsewhere. **`renderCompaniesSelect`** button label uses **`selectedCompanyId`** / **`selectedCompanyName`** while initial state omits them (empty label until selection). Whether backend requires **`external_id`** or validates invoice–company consistency beyond ids — **none** if contract is documented on API. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/services/new.js` (`ServicesNew`)

- **`componentDidMount`**: **`fetchCommonData`** (`viewUtil.fetchDashboardCommonData`) and **`fetchCompanyData`** (`api.getCompanies` → `companyList`).
- **`handleSubmit`**: **`makePostInvoiceRequest`** then **`makePostServiceRequest`**. On invoice error, shows alert with message. On service error, same. On success, alert then **`window.location = "/admin/services/"`**.
- **`makePostInvoiceRequest`**: builds JSON from keys **`title`**, **`url`**, **`transaction_id`**, **`number`**, **`external_id`**, **`company`**, **`total_amount`**, **`status`** → **`api.createInvoice`**.
- **`makePostServiceRequest`**: builds **`company_id`** from **`formValues.company`**, **`invoices`**: **`[invoice._id]`**, plus **`service`**, **`duration`**, **`start_at`** → **`api.createCompanyService({ admin: true, body: … })`**.

### `src/views/admin/services/form-segment-service.js` (`FormSegmentService`)

- **`formType === "new"`**: searchable **`Select`** of companies — **`api.getCompanies({ query: { name }, admin: true })`** on query change; **`handleSelectCompany`** sets parent **`company`** via **`handleChangeCompany(company._id)`**.
- Service type **`select`**: **`secretary`**, **`director`**, **`mailroom`**.
- **`DateInput`** for **`start_at`** (required); number field **`duration`** (months).

### `src/views/admin/services/form-segment-invoice.js` (`FormSegmentInvoice`)

- Text/number fields: **`title`**, **`url`**, **`transaction_id`**, **`number`**, **`total_amount`**; **`status`** select: **`processing`**, **`done`**, **`failed`**.

### `src/utils/api.js`

- **`createInvoice`**: **`postResource`** → **`${getBaseUrl()}/admin/invoices`**.
- **`createCompanyService`**: **`postResource`** → **`${getBaseUrl()}/company-services`**; with **`admin: true`**, **`postResource`** rewrites to **`${getBaseUrl()}/admin/company-services`**.
- **`getCompanies`**: **`GET ${getBaseUrl()}/companies`** with optional **`admin`** path segment when **`options.admin === true`** (via **`getResource`**).
