# Manage company service assignments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company service assignments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek admin using the **Services** admin area) |
| **Business Outcome** | Operations can keep each company’s corporate-service subscription (service type, term length, and start date) accurate in the platform and review related invoice metadata in context, so downstream operations and billing references stay aligned. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/services/edit/?id=<companyServiceId>`** (webpack entry `admin/services/edit`). Reached from **`/admin/services/`** (per-row edit link) and from **paid subscriptions** admin (**`/admin/subscriptions/paid/`**) via **“edit service”** links. **`AdminLayout`**: `sidebarActiveMenuItemKey="services"`. |
| **Short Description** | Loads one **company service** by query **`id`**, hydrates the form with company id, **service** type, **duration**, **start_at**, and nested **invoices**. Admins edit service type (**secretary**, **director**, **mailroom**), start date, and duration (months), then submit. Linked invoices render read-only (**title**, **url**, **transaction_id**, **number**, **total_amount**, **status**) for context. Submit calls **`PUT`** on **`/company-services/:companyServiceId`** with JSON body keys **`company_id`**, **`service`**, **`duration`**, **`start_at`**. |
| **Variants / Markets** | **Unknown** (no market-specific branching in this view; corporate service types are fixed in the form). |
| **Dependencies / Related Flows** | **`api.getCompanyService`** → **`GET ${getBaseUrl()}/company-services/:companyServiceId`**. **`api.updateCompanyService`** → **`PUT`** same path. **`api.getCompanies`** → **`GET ${getBaseUrl()}/companies`** (admin list support). Related elsewhere: **`editAndRefreshSubscription`** (**`/admin/company-services/:id/edit-and-refresh-subscription`**) used from invoice update-services flows, not this screen. Invoice rows are whatever the backend embeds on the company-service resource — not loaded separately in this view. |
| **Service / Repository** | **sleek-website**: `src/views/admin/services/edit.js`, `form-segment-service.js`, `form-segment-invoice.js`, `src/utils/api.js`. **Main HTTP API** (backend behind **`getBaseUrl()`**): company-services and companies — persistence not visible in this repo. |
| **DB - Collections** | **Unknown** (MongoDB or other stores for company-services / invoices live in backend services). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Submit builds payload with keys **`company_id`**, **`service`**, **`duration`**, **`start_at`**, but loaded form state uses **`company`** (not **`company_id`**) for the company id — verify backend accepts missing **`company_id`** or aliasing, or whether updates should map **`company` → company_id**. Whether **`AdminLayout`** / **`fetchDashboardCommonData`** **`company`** context is always meaningful on this admin route — **none** if backend contract is documented elsewhere. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/services/edit.js` (`ServicesEdit`)

- **`componentDidMount`**: **`fetchDashboardCommonData`**, **`fetchCompanyData`** (**`api.getCompanies`** → **`state.companyList`**), **`populateCompanyServiceForm`**.
- **`populateCompanyServiceForm`**: **`querystring.parse`** → **`api.getCompanyService(query.id, { admin: true })`**; sets **`formValues`**: **`company`** from **`company.company._id`**, **`duration`**, **`service`**, **`start_at`** as **`Date`**, **`invoices`** array.
- **`makePutServiceRequest`**: same **`query.id`**; reduces **`update_service_keys`** **`["company_id", "service", "duration", "start_at"]`** from **`formValues`** → **`api.updateCompanyService(query.id, { admin: true, body: JSON.stringify(payload) })`**.
- **`handleSubmit`**: on success, alert then **`window.location = "/admin/services/"`**.
- **`renderBodyContent`**: **`FormSegmentService`** with **`companyList`**; **`FormSegmentInvoice`** per invoice with **`disabled={true}`**. Toolbar back link **`/admin/services/`**.

### `src/views/admin/services/form-segment-service.js` (`FormSegmentService`)

- Service type **select**: **secretary**, **director**, **mailroom**.
- **`DateInput`** for **`start_at`** (DD/MM/YYYY via **`utils/date`** and **moment**).
- **`duration`** number input (months).
- Company **Select** and **`api.getCompanies({ query, admin: true })`** search path used when **`formType == "new"`** (not the edit page’s primary path).

### `src/views/admin/services/form-segment-invoice.js` (`FormSegmentInvoice`)

- **FormInputs** for invoice **title**, **url**, **transaction_id**, **number**, **total_amount**, **status** (processing / done / failed). Typically read-only on edit (**`disabled`** from parent).

### `src/utils/api.js`

- **`getCompanies`**: **`GET ${getBaseUrl()}/companies`** via **`getResource`**.
- **`getCompanyService`**: **`GET ${getBaseUrl()}/company-services/${companyServiceId}`**.
- **`updateCompanyService`**: **`PUT ${getBaseUrl()}/company-services/${companyServiceId}`** via **`putResource`**.

### Related navigation (same repo)

- **`src/views/admin/services.js`**: index table links to **`/admin/services/edit/?id=${companyService._id}`**.
- **`src/views/admin/subscriptions/index.js`**: paid subscriptions link to the same edit URL.
