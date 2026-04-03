# Create customer company records

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Create customer company records |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Support staff (Admin) |
| **Business Outcome** | Support staff can register custom company profiles for staff allocation, optionally linking an internal Sleek company for name and registration id, then continue on the company detail page. |
| **Entry Point / Surface** | Sleek Admin > Customer Support > **Create Company** — route `/admin/customer-support/create-company` (webpack entry `admin/customer-support/create-company`; page shell in `pages/admin/customer-support/create-company/`). |
| **Short Description** | **Use existing company** uses `InternalCompanySearchForm` (debounced name search against the main Sleek companies API with `admin: true`) to optionally set `name`, `registration_id` (from `uen`), and `internal_id` (Sleek company `_id`). **CompanyInfoForm** collects required name and registration id, optional validated customer emails and phone numbers. **Save Company** calls `StaffAllocationAPI.instance.createCompany` (`POST /companies` on the resource-allocator service), then redirects to `/admin/customer-support/company/?cid=${newCompany._id}`. API errors surface in a Blueprint `Alert`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Resource allocator** (Staff Allocation API) persists custom companies; **main Sleek API** `getCompanies` with `admin: true` powers the internal company picker; downstream **customer support company detail** at `/admin/customer-support/company/`; broader staff allocation flows (`createStaffAllocation`, etc.) use the same API client. |
| **Service / Repository** | sleek-website; resource-allocator (base URL `API_STAFF_ALLOCATION_URL` or `https://resource-allocator.sleek.sg` / `http://localhost:3015`); main Sleek API (company search) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB (or other) collections for custom companies live in the resource-allocator service; not determined from sleek-website alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`CreateCustomCompanyView`** — `src/views/admin/customer-support/create-company/index.js`: state shape `name`, `registration_id`, `internal_id`, `emails`, `phones`, `active`, `remarks`, `metadata`. `onSave` → `StaffAllocationAPI.instance.createCompany(company)`; success → `window.location.href = `/admin/customer-support/company/?cid=${newCompany._id}``. `onSelectInternalCompany` clears or sets `name`, `registration_id` from `data.uen`, `internal_id` from `data._id`. `AdminLayout` `sidebarActiveMenuItemKey="customer-support"`, `hideDrawer={true}`; toolbar “Create Company”; back via `useRedirectHomePage`.
- **`StaffAllocationAPI.createCompany`** — `src/utils/api-staff-allocation.js`: `POST /companies` with DTO; axios interceptors unwrap `response.data.data`; JSDoc `CustomCompany` documents `internal_id` as Sleek DB company id.
- **`CompanyInfoForm`** — `src/views/admin/customer-support/forms/company-info-form.js`: required `name` and `registration_id`; optional `emails` (`TagInput`, `emailValidationRegex` from `@/utils/user-validation`); optional `phones` (`TagInput`).
- **`InternalCompanySearchForm`** — `src/views/admin/customer-support/forms/internal-company-search-form.js`: Blueprint `Select` + `useInternalCompanies(nameQuery)`.
- **`useInternalCompanies`** — `src/views/admin/customer-support/hooks/internal-companies.js`: 500 ms debounce; `getCompanies({ query: { name }, admin: true })` from `@/utils/api`; uses `response.data.companies`, filters empty names.
