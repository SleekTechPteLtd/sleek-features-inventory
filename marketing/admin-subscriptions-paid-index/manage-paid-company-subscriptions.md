# Manage paid company subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage paid company subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin users with subscription / company-services permissions (`company_services` full for edit and remove) |
| **Business Outcome** | Operations staff can see which companies have paid subscription services, how long they run, which invoices tie to them, and correct or remove records when authorised. |
| **Entry Point / Surface** | **sleek-website** admin: **Subscriptions → Paid** (`/admin/subscriptions/paid/`) — `AdminLayout` with `sidebarActiveMenuItemKey="subscriptions"` and `sidebarActiveMenuSubItemKey="paid-subscriptions"`. Edit: `/admin/subscriptions/paid/edit/?id=<companyServiceId>`. |
| **Short Description** | Lists **company services** (paid subscription rows) with pagination: optional **company** filter (searchable select fed by admin company search), status filter **Any / Currently Active / Past** (`is_active` true/false), and `selected_only: true`. Table shows company (link to customer dashboard), service type, duration, start/end dates, invoice links (new tab), and **Edit** / **Remove** when `user.permissions.company_services === "full"`. Edit screen loads one company service, shows service fields and read-only invoice segments, submits updates via PUT. |
| **Variants / Markets** | Unknown (tenant not specialised in these views; main API is shared). |
| **Dependencies / Related Flows** | **`api.getCompanyServices`** (`admin: true`) → `GET /admin/company-services` with query `skip`, `company`, `selected_only`, optional `is_active`. **`api.getCompanies`** (`admin: true`) for company picker (`views/admin/subscriptions/common.js`). **`api.getUser`**, **`api.getCompanyService`**, **`api.updateCompanyService`**, **`api.deleteCompanyServices`** — all `company-services` routes under `/admin/...` when `admin: true` in `api.js`. Related: unpaid subscriptions, new subscription flows, **`viewUtil.fetchDashboardCommonData`** on edit page. |
| **Service / Repository** | **sleek-website**: `src/views/admin/subscriptions/paid/index.js`, `src/views/admin/subscriptions/common.js`, `src/views/admin/subscriptions/paid/edit/index.js`, `src/utils/api.js` (`getCompanyServices`, `getCompanyService`, `updateCompanyService`, `deleteCompanyServices`, `getCompanies`, `getUser`). **Backend** (not in this repo): admin company-services controller and persistence. |
| **DB - Collections** | **MongoDB** (backend only; not in sleek-website): resources behind `company-services` and `companies` admin APIs — **Unknown** exact collection names without sleek-back source. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Edit **`makePutServiceRequest`** builds payload keys `company_id`, `service`, `duration`, `start_at` from `formValues`, while `populateCompanyServiceForm` sets `company` (not `company_id`); confirm backend accepts partial updates or whether this is legacy / bug. Whether `getCompanies()` on edit mount (non-admin) is intentional for company list context. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/subscriptions/paid/index.js` (`AdminPaidSubscriptionsView`)

- **Mount**: `getUser()` (from `../../subscriptions/common` re-exports), `getCompanyServices()`.
- **Filters**: `serviceFilter` — empty = Any; `"active"` sets `query.is_active = true`; `"past"` sets `is_active = false`. `selected_only: true`, `company` = `selectedCompanyId`, pagination `skip` from `page` and `perPage` (20).
- **API**: `api.getCompanyServices({ admin: true, query })` → `GET /admin/company-services?...` per `getResource` admin prefix in `api.js`.
- **Table**: Company name → `/dashboard/?cid=...`; invoice cells use `invoice.url` and `invoice.number`; **Edit** → `/admin/subscriptions/paid/edit/?id=${companyService._id}`; **Remove** → confirm dialog then `api.deleteCompanyServices(service._id, { admin: true })` → `DELETE /admin/company-services/:id`.
- **Permissions**: Edit and Remove disabled unless `user.permissions.company_services === "full"`.

### `src/views/admin/subscriptions/common.js`

- Shared handlers: `handleSelectCompany`, `handleSelectNoCompany`, `handleSearchCompany`, `fetchCompaniesList` → `api.getCompanies({ query: { name: selectCompanySearch }, admin: true })`, pagination helpers, `getUser` with `checkResponseIfAuthorized` on failure.

### `src/views/admin/subscriptions/paid/edit/index.js` (`ServicesEdit`)

- **Load**: `fetchDashboardCommonData`, `api.getCompanies()` for `companyList`, `api.getCompanyService(query.id, { admin: true })` to fill `formValues` (company, duration, service, start_at, invoices).
- **Submit**: `api.updateCompanyService(query.id, { admin: true, body: JSON.stringify(payload) })` → `PUT /admin/company-services/:id`; success alert then `window.location = "/admin/subscriptions/paid/"`.
- **UI**: `FormSegmentService`, read-only `FormSegmentInvoice` per invoice; toolbar back link to paid list.

### `src/utils/api.js`

- `getCompanyServices` → `GET ${getBaseUrl()}/company-services` (+ `/admin` prefix when `options.admin === true`).
- `getCompanyService` / `updateCompanyService` / `deleteCompanyServices` → `/company-services/:companyServiceId` with same admin prefix behaviour.
- `getCompanies` → `/companies` (admin variant when `admin: true`).
