# Manage company services

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company services |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek admin; **New Service**, **Edit**, and **Remove** require `user.permissions.company_services === "full"`) |
| **Business Outcome** | Operations can see and curate legacy **company service** rows (corporate service type, term length, start/end dates) per company, jump to the client dashboard or linked invoices, and remove or open the edit flow when permitted—keeping the platform’s company-service record aligned with billing and delivery context. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/services/`** (webpack entry **`admin/services`** → `src/views/admin/services.js`). **`AdminLayout`**: `sidebarActiveMenuItemKey="services"`. Optional query **`?st=<serviceType>`** persists service-type filter via `history.replaceState`. |
| **Short Description** | Paginated table of **company services** from **`GET /admin/company-services`** (query: `skip`, `service`, `company_id`, and a `status` field sent from client code — see Evidence). Columns: company (link to **`/dashboard/?cid=<companyId>`**), service name, duration (months), start/end dates, invoice links (opens invoice URLs in a new tab), **Edit** (**`/admin/services/edit/?id=`**) and **Remove** (confirm dialog, then **`DELETE /admin/company-services/:id`**). Toolbar: **New Service** (**`/admin/services/new/`**), pagination, filter by service type (transfer, incorporation, mailroom, secretary, etc.), and typeahead **Select company** (search via **`GET /admin/companies?name=...`**). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **`api.getCompanyServices`** → **`GET ${getBaseUrl()}/company-services`** with **`admin: true`**. **`api.deleteCompanyServices`** → **`DELETE`** same resource **`/company-services/:serviceId`**. **`api.getCompanies`** for company picker. Related UIs: **`/admin/services/new/`** (provision), **`/admin/services/edit/`** (assignments); **paid subscriptions** admin links into **edit service** (`src/views/admin/subscriptions/index.js`). Distinct from **Sleek Billings** “company subscriptions” on **Company Billing** (`manage-company-subscriptions.md`). |
| **Service / Repository** | **sleek-website**: `src/views/admin/services.js`, `src/utils/api.js` (`getCompanyServices`, `deleteCompanyServices`, `getCompanies`, `getUser`). **Main HTTP API** (backend behind **`getBaseUrl()`**): **`/company-services`**, **`/companies`**. |
| **DB - Collections** | Unknown — persistence for company-services and embedded invoice metadata lives in backend services, not this repo. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | **`getCompanyServices`** builds `query.status` from an identifier **`status`** that is not defined in module scope (possible bug or reliance on a global); confirm intended filter contract with the API. Unused **document template** handlers/state in `services.js` appear disconnected from **`render()`** — dead code or incomplete feature? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/services.js` (`AdminServicesView`)

- **Mount**: `getUser()` (`api.getUser`); `getCompanyServices()`. Unverified email redirects to `/verify/`.
- **Layout**: `AdminLayout` + `sidebarActiveMenuItemKey="services"`.
- **Toolbar**: **New Service** → `/admin/services/new/` (disabled unless `user.permissions.company_services === "full"`). Pagination (`page`, `perPage` 20, `maxPage` from `ceil(count / perPage)`). Service-type `<select>` (`serviceFilter`) updates URL `?st=`. Company search: `fetchCompaniesList` → `api.getCompanies({ query: { name }, admin: true })`; `handleSelectCompany` / clear selection sets `selectedCompanyId` and refetches.
- **Table**: `api.getCompanyServices({ admin: true, query: { status, skip, service: serviceFilter, company_id: selectedCompanyId } })`; displays `company.name` (dashboard link), `service`, `duration`, `start_at` / `end_at` (moment), invoice anchors from `companyService.invoices[].url` / `number`.
- **Actions**: **Edit** → `/admin/services/edit/?id=${companyService._id}` (gated on `company_services` **full**). **Remove** → confirm dialog → `api.deleteCompanyServices(service._id, { admin: true })` then `getCompanyServices()`.
- **Also in file**: `getTemplates`, document template CRUD, TinyMCE, `generateDocumentFromTemplate`, etc. — not referenced from the main `render()` path for this page (listing-only UX is `renderCompanyServices`).

### `src/utils/api.js`

- **`getCompanies`**: `GET ${getBaseUrl()}/companies`; with `options.admin === true`, `getResource` rewrites to **`/admin/companies`** (see `getResource`).
- **`getCompanyServices`**: `GET ${getBaseUrl()}/company-services` → admin **`/admin/company-services`** when `admin: true`.
- **`deleteCompanyServices(serviceId)`**: `DELETE ${getBaseUrl()}/company-services/${serviceId}` → **`/admin/company-services/...`** when `admin: true`.

### Webpack

- `paths.js`: `"admin/services": "./src/views/admin/services.js"`.
- `webpack.common.js`: outputs `admin/services/index.html` for this entry.
