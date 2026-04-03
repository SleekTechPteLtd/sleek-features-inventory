# Assign staff roles to customer companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Assign staff roles to customer companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / Support staff |
| **Business Outcome** | Ensures each customer company has named staff emails in the right operational role slots so relationships and handoffs are owned by the correct people. |
| **Entry Point / Surface** | Sleek Admin > Customer Support > open a company (`/admin/customer-support/company/?cid={customCompanyId}`) — **Staff Assigned** card below company overview; **Update Staff Allocation** enters edit mode. |
| **Short Description** | Reads role definitions from platform CMS (`companies.overview.new_ui.new_resource_allocation`), shows only roles marked `is_visible_to_staff_assigned_widget`, and maps `company.resource_allocations` by `role_type` to display or edit staff emails per slot. Saving calls the Staff Allocation API bulk patch to persist non-empty assignments. Client-side email validation runs before submit. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Same page as **Customer support company detail** (`index.js`); company payload from `GET /companies/:id` includes `resource_allocations`. **StaffAllocationAPI** → resource-allocator (`API_STAFF_ALLOCATION_URL` or prod `https://resource-allocator.sleek.sg`). CMS-driven role list via `getAppFeatureProp` / `getActiveRoles`. |
| **Service / Repository** | sleek-website; resource-allocator (Staff Allocation API backend, not in this repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether parent page should refresh company state after bulk save (`onUpdateCompany` is optional and not wired from `index.js`); exact MongoDB collections remain in resource-allocator. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Embed point**: `src/views/admin/customer-support/company/index.js` — renders `<StaffAllocation company={company} platformConfig={platformConfig} disableUpdate={isDeleting} />` below the company card.
- **Role list source**: `src/views/admin/customer-support/utils.js` — `getActiveRoles(platformConfig)` reads `platformConfig.cmsAppFeatures` → `companies` → `overview` → `new_ui` → `new_resource_allocation`, filtered with `is_visible_to_staff_assigned_widget === true`.
- **UI / state**: `src/views/admin/customer-support/company/staff-allocation.js` — `formatResourceAllocation` merges each active role with `company.resource_allocations` by `role_type`; displays **Staff Assigned** with per-role title and email or `-`. Edit mode uses text inputs (placeholder “Staff Email”); `validateEmails` uses `emailValidationRegex` from `@/utils/user-validation`. `updateResourceAllocation` builds payload `{ company_id, resource_allocations: [{ email, role_type, group: null }] }` (omits empty emails) and calls `StaffAllocationAPI.instance.updateResourceAllocationBulk(payload)`.
- **HTTP**: `src/utils/api-staff-allocation.js` — `updateResourceAllocationBulk(dto)` → `PATCH /companies/allocations/bulk`; JSDOM typedefs document `role_type` (e.g. `kyc-in-charge`, `accounting-team-leader`) and `resource_allocations` on `CustomCompany`. Base URL from `API_STAFF_ALLOCATION_URL`, else prod `https://resource-allocator.sleek.sg` or local `http://localhost:3015`.
- **Related API surface (not used by this widget but same client)**: `createStaffAllocation`, `updateResourceAllocation`, `deleteResourceAllocation` on `/companies/allocations` — single-allocation flows; this feature uses bulk patch only.
