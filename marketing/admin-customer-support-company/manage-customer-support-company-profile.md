# Manage customer support company profile

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage customer support company profile |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Support staff (Admin) |
| **Business Outcome** | Support staff can keep customer-support custom company records accurate by viewing, editing, and deleting name, registration, and contact details backed by the resource-allocator service. |
| **Entry Point / Surface** | Sleek Admin > Customer Support — open a company from the custom company list (`/admin/customer-support/company/?cid={customCompanyId}`); also reachable after creating a company from Customer Support. |
| **Short Description** | Loads a custom company by `cid` via the Staff Allocation API (`GET /companies/:id`). Read-only mode shows company name (link to Sleek company overview when `internal_id` exists), registration ID, customer emails, and phones. Edit mode uses `CompanyInfoForm` to change name, registration ID, emails (validated), and phones; changes persist with `PATCH /companies/:id`. Delete uses a confirmation dialog requiring the exact company name, then `DELETE /companies/:id`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `StaffAllocationAPI` → resource-allocator (`API_STAFF_ALLOCATION_URL` or production `https://resource-allocator.sleek.sg`); inbound navigation from `custom-company-row.js` and post-create redirect from `create-company/index.js`; optional link to `/admin/company-overview/?cid=` when `internal_id` is set; same page embeds `StaffAllocation` (separate capability). |
| **Service / Repository** | sleek-website; resource-allocator (Staff Allocation API backend, not in this repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB collection names for custom companies are owned by resource-allocator and are not visible from sleek-website alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page**: Webpack entry `admin/customer-support/company` → `src/views/admin/customer-support/company/index.js` (Marko shell `pages/admin/customer-support/company/index.html.marko` — title “Customer Support - Company”).
- **Load**: `querystring.parse(window.location.search.slice(1))` → `StaffAllocationAPI.instance.getCompany(companyId)` — `GET /companies/${companyId}` in `src/utils/api-staff-allocation.js` (`getCompany`).
- **Read-only display**: Name as heading; with `company.internal_id`, name links to `/admin/company-overview/?cid=${company.internal_id}` (new tab). `Reg. ID` from `registration_id`; `Customer Emails` / `Customer Phone Numbers` from `company.emails` and `company.phones` arrays.
- **Edit UI**: `editMode` toggles `CompanyInfoForm` from `src/views/admin/customer-support/forms/company-info-form.js` — fields `name`, `registration_id`, `emails` (`TagInput`, validated with `emailValidationRegex` from `@/utils/user-validation`), `phones` (`TagInput`). `onUpdate` merges into `tempData`; `updateCompanyDetails` → `StaffAllocationAPI.instance.updateCompany(company._id, tempData)` — `PATCH /companies/${companyId}` (`updateCompany`).
- **Delete**: `useDeleteCompany` in `src/views/admin/customer-support/hooks/delete-company.js` — Blueprint `Alert` confirmation; user must type matching `company.name`; `StaffAllocationAPI.instance.deleteCompany(company._id)` — `DELETE /companies/${companyId}` (`deleteCompany`). Success message or error surfaced via alerts; `useRedirectHomePage` can return to `/admin/customer-support/`.
- **API client**: `StaffAllocationAPI` — axios base URL from `API_STAFF_ALLOCATION_URL`, else prod `https://resource-allocator.sleek.sg` or dev `http://localhost:3015`; default headers via `getDefaultHeaders`; response unwrap `{ data }` from JSON body.
- **Layout**: `AdminLayout` with `sidebarActiveMenuItemKey="customer-support"`, `hideDrawer={true}`, toolbar “Company Overview”, back chevron to customer support home.
