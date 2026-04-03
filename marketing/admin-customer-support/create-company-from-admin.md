# Create company from admin

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Create company from admin |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Support staff (Admin) / Operations |
| **Business Outcome** | Operators can register a new customer-support custom company with optional linkage to an existing Sleek company and contact details, then land on the company detail view to continue support work. |
| **Entry Point / Surface** | Sleek Admin > Customer Support — **Create Company** navigates to `/admin/customer-support/create-company` (from `CustomerSupportView` in `src/views/admin/customer-support/index.js` via `redirectToCreateCompany`). |
| **Short Description** | Presents **Use existing company** search (`InternalCompanySearchForm`) backed by debounced admin company name search, plus **CompanyInfoForm** for name, registration ID (UEN / CR No.), optional customer emails (validated) and phones. Selecting an internal company prefills name, `registration_id` from `uen`, and `internal_id`. **Save Company** calls `StaffAllocationAPI.instance.createCompany(company)` (`POST /companies` on the resource-allocator service), then full-page redirect to `/admin/customer-support/company/?cid=${newCompany._id}`. Errors from the API response are shown in a Blueprint `Alert`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Staff Allocation API** → resource-allocator (`POST /companies`); **Main Sleek API** `getCompanies` with `admin: true` for internal company picker (`GET ${base}/companies?name=…`); downstream **Manage customer support company profile** on the company detail URL; optional future link to Sleek company overview when `internal_id` is set (handled on the detail page). |
| **Service / Repository** | sleek-website; resource-allocator (Staff Allocation API backend); main Sleek API (company list for search) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB collections for custom companies are owned by resource-allocator and are not visible from sleek-website alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Webpack entry**: `admin/customer-support/create-company` → `src/views/admin/customer-support/create-company/index.js` (bundled per `webpack/paths.js` and `webpack.common.js`).
- **Shell page**: Marko template `pages/admin/customer-support/create-company/index.html.marko` (referenced from webpack config).
- **View `CreateCustomCompanyView`**: Initial `company` state includes `name`, `registration_id`, `internal_id`, `emails`, `phones`, `active`, `remarks`, `metadata`. `onSave` → `StaffAllocationAPI.instance.createCompany(company)` then `window.location.href = `/admin/customer-support/company/?cid=${newCompany._id}``. Error handling reads `error.response.data.message` (array joined or string). `AdminLayout` with `sidebarActiveMenuItemKey="customer-support"`, `hideDrawer={true}`; toolbar title “Create Company”; back button uses `useRedirectHomePage` → `/admin/customer-support/`.
- **Staff Allocation client**: `src/utils/api-staff-allocation.js` — `createCompany(dto)` → `this.http.post("/companies", dto)`; base URL `API_STAFF_ALLOCATION_URL` or production `https://resource-allocator.sleek.sg` / dev `http://localhost:3015`. JSDoc `CustomCompany` includes `internal_id` as “Company ID in sleek db”.
- **Internal company search**: `src/views/admin/customer-support/forms/internal-company-search-form.js` — Blueprint `Select` with `useInternalCompanies(nameQuery)` from `src/views/admin/customer-support/hooks/internal-companies.js`. That hook debounces (500 ms) and calls `getCompanies({ query: { name }, admin: true })` (`src/utils/api.js` → `GET ${getBaseUrl()}/companies`). Parent `onSelectInternalCompany` either clears name/registration/internal_id or sets `name`, `registration_id` from `data.uen`, `internal_id` from `data._id`.
- **Company fields**: `src/views/admin/customer-support/forms/company-info-form.js` — `name`, `registration_id`, `emails` (`TagInput`, `emailValidationRegex` from `@/utils/user-validation`), `phones` (`TagInput`).
- **Customer Support home entry**: `src/views/admin/customer-support/index.js` — `redirectToCreateCompany` sets `window.location.href = "/admin/customer-support/create-company"`.
