# Customer support company detail

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Customer support company detail |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets support staff inspect and maintain a custom (resource-allocator) company record alongside staff allocation, with a quick path to the main Sleek company overview when linked. |
| **Entry Point / Surface** | Sleek Admin > Customer Support — open a row (e.g. from the custom company list) to `/admin/customer-support/company/?cid={customCompanyId}`; also reached after creating a company from Customer Support. |
| **Short Description** | Loads the company by `cid` query param via the Staff Allocation API (`GET /companies/:id`). Read-only view shows company name (linked to `/admin/company-overview/?cid=` when `internal_id` exists), registration ID, customer emails, and phones. Edit mode uses `CompanyInfoForm` and `PATCH /companies/:id`. The page also embeds staff allocation and supports delete via `DELETE /companies/:id`. Back navigation goes to `/admin/customer-support/`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `StaffAllocationAPI` → resource-allocator service (`API_STAFF_ALLOCATION_URL` or prod `https://resource-allocator.sleek.sg`); upstream list/navigation from `custom-company-row.js` and post-create redirect from `create-company/index.js`; downstream Sleek overview at `/admin/company-overview/` when `internal_id` is set; same-page `StaffAllocation` and `useDeleteCompany`. |
| **Service / Repository** | sleek-website; resource-allocator (Staff Allocation API backend, not in this repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB collection names for custom companies live in resource-allocator; not determined from sleek-website alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page shell**: `pages/admin/customer-support/company/index.html.marko` — title “Customer Support - Company”; webpack entry `admin/customer-support/company` → `src/views/admin/customer-support/company/index.js`.
- **Load by `cid`**: `querystring.parse(window.location.search.slice(1))` → `getCompanyData(query.cid)`; `StaffAllocationAPI.instance.getCompany(companyId)` (`src/utils/api-staff-allocation.js` — `GET /companies/${companyId}`).
- **Displayed fields (read-only)**: Name as heading; if `company.internal_id`, name links to `/admin/company-overview/?cid=${company.internal_id}` (new tab, share icon). `Reg. ID:` from `registration_id` or “-”. `Customer Emails` / `Customer Phone Numbers` from `company.emails` and `company.phones` arrays (or “-”).
- **Edit / persist**: `editMode` toggles `CompanyInfoForm` vs read-only grid; `updateCompanyDetails` → `StaffAllocationAPI.instance.updateCompany(company._id, tempData)` (`PATCH /companies/${companyId}`).
- **Related UI**: `StaffAllocation` with `company` and `platformConfig`; `useDeleteCompany` → `deleteCompany(company._id)`; `useRedirectHomePage` → `/admin/customer-support/`.
- **Layout**: `AdminLayout` with `sidebarActiveMenuItemKey="customer-support"`, `hideDrawer={true}`, toolbar title “Company Overview”.
- **Inbound links**: `src/views/admin/customer-support/custom-list/custom-company-row.js` — `href` `/admin/customer-support/company/?cid=${company._id}`; `create-company/index.js` redirects to same pattern after create.
