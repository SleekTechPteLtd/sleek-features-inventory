# Manage company profile and staff allocation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company profile and staff allocation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / support staff (Sleek Admin users on Customer Support) |
| **Business Outcome** | Operators keep each **custom company** record accurate—legal identity, customer contacts, and which internal staff own which operational roles—and can retire companies only after explicit confirmation, reducing mis-routing and mistaken deletions. |
| **Entry Point / Surface** | **sleek-website** admin: **Customer Support** → open a company from the list → **Company Overview** (`/admin/customer-support/company/?cid={customCompanyId}`). `AdminLayout` with `sidebarActiveMenuItemKey="customer-support"`; primary toolbar back control returns to the Customer Support home. |
| **Short Description** | Loads one custom company via **Staff Allocation API** (`GET /companies/:id`). Operators **Edit Company** to change name, registration ID, customer emails, and phones (`CompanyInfoForm` with tag inputs and email validation). **Staff Assigned** lists CMS-configured roles (`getActiveRoles`); edit mode saves non-empty staff emails per `role_type` via **bulk patch** (`PATCH /companies/allocations/bulk`). **Delete Company** opens a danger dialog: the user must type the exact company name before `DELETE /companies/:id` runs; success or fetch errors surface via alerts and optional redirect to the list. |
| **Variants / Markets** | Unknown — no market branching in these views; API base in production defaults to `https://resource-allocator.sleek.sg` (SG hostname). |
| **Dependencies / Related Flows** | **Upstream**: Customer Support company list and navigation to this page with `cid`. **StaffAllocationAPI** (`src/utils/api-staff-allocation.js`) → **resource-allocator** (not in this repo): `getCompany`, `updateCompany`, `updateResourceAllocationBulk`, `deleteCompany`. **CMS / platform config**: `usePlatformConfig` + `getActiveRoles` → `platformConfig.cmsAppFeatures` → `companies.overview.new_ui.new_resource_allocation`, filtered by `is_visible_to_staff_assigned_widget`. When `internal_id` is set, company name links to **`/admin/company-overview/?cid={internal_id}`** (Sleek internal company). **Related**: `onUpdateCompany` on `StaffAllocation` is optional and not wired from the parent page, so the parent `company` state is not refreshed from the bulk allocation response in the current code. |
| **Service / Repository** | **sleek-website**: `src/views/admin/customer-support/company/index.js`, `src/views/admin/customer-support/company/staff-allocation.js`, `src/views/admin/customer-support/hooks/delete-company.js`, `src/views/admin/customer-support/forms/company-info-form.js`, `src/views/admin/customer-support/utils.js` (`getActiveRoles`, `errorParser`), `src/utils/api-staff-allocation.js`. **resource-allocator** (external): REST API for custom companies and allocations. |
| **DB - Collections** | Unknown from this frontend — persistence is behind **resource-allocator**; MongoDB (or other) collections are not named in sleek-website. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `clearDeleteStatus` in `useDeleteCompany` should call `setDeleteMessage(null)` instead of `deleteMessage(null)` (likely bug). Exact backend schema and collection names for custom companies and resource allocations. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/customer-support/company/index.js` (`CustomCompanyView`)

- **Mount**: `domready` → `ReactDOM.render` into `#root`.
- **Load**: `useEffect` reads `cid` from query string; `StaffAllocationAPI.instance.getCompany(companyId)`; errors via `errorParser` → `fetchError` alert.
- **Company header**: Name links to `/admin/company-overview/?cid=` when `internal_id` exists; otherwise plain text.
- **Edit / save**: `editMode` toggles between read-only summary (reg ID, emails, phones) and `CompanyInfoForm` with `tempData`; **Save** calls `StaffAllocationAPI.instance.updateCompany(company._id, tempData)` (`PATCH /companies/:id`).
- **Delete**: `useDeleteCompany(company)` → `renderDeleteDialog`, **Delete Company** button, `isDeleting` disables edit/delete and passes `disableUpdate` to `StaffAllocation`.
- **Staff block**: `<StaffAllocation company={company} platformConfig={platformConfig} disableUpdate={isDeleting} />` (no `onUpdateCompany` prop).

### `src/views/admin/customer-support/forms/company-info-form.js` (`CompanyInfoForm`)

- Fields: `name`, `registration_id`, `emails` (`TagInput`), `phones` (`TagInput` with numeric `inputProps`).
- `onUpdateEmails` validates each tag with `emailValidationRegex` before calling `onUpdate("emails", values)`.

### `src/views/admin/customer-support/company/staff-allocation.js` (`StaffAllocation`)

- `formatResourceAllocation`: `getActiveRoles(platformConfig)` × `company.resource_allocations` matched by `role_type`; builds rows with `title`, `type`, `email`.
- **Save**: `validateEmails` flags invalid non-empty emails; payload `{ company_id, resource_allocations: [{ email, role_type, group: null }] }` filtered to entries with email; `StaffAllocationAPI.instance.updateResourceAllocationBulk` → `PATCH /companies/allocations/bulk`.

### `src/views/admin/customer-support/hooks/delete-company.js` (`useDeleteCompany`)

- `onDelete` opens Blueprint `Alert`; user must type `company.name` exactly (`deleteConfirmationText`); `StaffAllocationAPI.instance.deleteCompany(company._id)` → `DELETE /companies/:companyId`.
- Success message stored for the parent alert path that calls `redirectToHomePage` on confirm (see parent `fetchError || deleteMessage` alert).

### `src/views/admin/customer-support/utils.js`

- `getActiveRoles`: `getAppFeatureProp(platformConfig.cmsAppFeatures, "companies")` → `overview.props.new_ui.value.new_resource_allocation`, filtered `is_visible_to_staff_assigned_widget === true`.

### `src/utils/api-staff-allocation.js` (`StaffAllocationAPI`)

- Base URL: `API_STAFF_ALLOCATION_URL`, else prod `https://resource-allocator.sleek.sg` or dev `http://localhost:3015`.
- Methods used by this capability: `getCompany`, `updateCompany`, `updateResourceAllocationBulk`, `deleteCompany` (paths as above).
