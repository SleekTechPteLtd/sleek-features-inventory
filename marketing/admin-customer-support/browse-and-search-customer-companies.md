# Browse and search customer companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Browse and search customer companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Support / operations staff (Sleek Admin users with access to Customer Support) |
| **Business Outcome** | Operators can find the correct **custom company** (staff-allocation) account by contact details, registration ID, and dates so they can open the right record for follow-up. |
| **Entry Point / Surface** | **sleek-website** admin: **Customer Support** (`/admin/customer-support/`) — `AdminLayout` with `sidebarActiveMenuItemKey="customer-support"`, primary toolbar title “Customer Support”, **Company List** section with `CustomCompanyTable`. |
| **Short Description** | Loads a paginated, sortable table of custom companies via the **Staff Allocation** API. Users filter with debounced search on **customer email**, **customer phone**, **staff email**, **company name**, and **registration ID**; they sort by **name**, **updated_at**, or **created_at** (default sort `_id` descending). Pagination is 20 rows per page with previous/next and a direct page number field. Each row links to the company detail screen. The same page also exposes bulk upload, template download, and create-company actions (separate capabilities). |
| **Variants / Markets** | Unknown — no market branching in these views; API host defaults to SG in production (`resource-allocator.sleek.sg`). |
| **Dependencies / Related Flows** | **`StaffAllocationAPI.instance.getCompanies`** → `GET {base}/companies` with query params: `limit`, `skip`, `sort_option`, `sort_order`, plus flattened **filter** keys (`email`, `phone`, `staff_email`, `name`, `registration_id`, etc.). Base URL from `API_STAFF_ALLOCATION_URL` or **resource-allocator** (`https://resource-allocator.sleek.sg` in production). Response shape `{ result, count }` after axios unwrap of `response.data.data`. Downstream: **resource-allocator** service (not in this repo). Related UI: **Company** detail (`/admin/customer-support/company/?cid=`), **Create Company**, bulk upload — same module. |
| **Service / Repository** | **sleek-website**: `src/views/admin/customer-support/index.js`, `src/views/admin/customer-support/custom-list/custom-company-table.js`, `src/views/admin/customer-support/custom-list/custom-company-row.js`, `src/views/admin/customer-support/hooks/custom-companies.js`, `src/utils/api-staff-allocation.js`. **resource-allocator** (external): implements `/companies`. |
| **DB - Collections** | Unknown from this frontend — custom company storage is behind **resource-allocator**; not referenced in sleek-website. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `useCustomCompanies` exposes `isLoadingCompanies` and `fetchCompaniesError`, but `CustomCompanyTable` does not surface loading or error UI — confirm whether that is intentional. Whether filter matching semantics (partial vs exact) are defined only server-side. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/customer-support/index.js` (`CustomerSupportView`)

- **Mount**: `domready` → `ReactDOM.render` into `#root`.
- **Layout**: `AdminLayout` `hideDrawer={true}`, `sidebarActiveMenuItemKey="customer-support"`, toolbar “Customer Support”.
- **Body**: “Company List” heading; actions **Create Company** (`/admin/customer-support/create-company`), **Bulk Upload**, **Download Template**; **`CustomCompanyTable`** with `ref` for `refreshTable()` after bulk upload success.
- **User session**: `useUser()` passed into layout (auth surface for admin).

### `src/views/admin/customer-support/custom-list/custom-company-table.js` (`CustomCompanyTable`)

- **State**: `options` with `filter`, `limit: 20`, `skip`, `sort_option` (default `_id`), `sort_order` (default `-1`).
- **Data**: `useCustomCompanies(options)` → `companies`, `total`.
- **Sort**: Header links toggle `sort_order` for `name`, `updated_at`, `created_at`; chevron icon reflects direction.
- **Filter**: `onFilterSearch` (lodash `debounce` 250ms) merges `{ [field]: value }` into `filter`, resets `skip` to 0.
- **Pagination**: `getCurrentPage`, `onPreviousPage`, `onNextPage`, `onChangePage`; `canNavigateNext` uses `total > skip + limit`.
- **Imperative**: `useImperativeHandle` → `refreshTable()` bumps a `__ref` timestamp on `options` to force refetch.

### `src/views/admin/customer-support/hooks/custom-companies.js` (`useCustomCompanies`)

- **Fetch**: `StaffAllocationAPI.instance.getCompanies({ limit, skip, sort_order, sort_option, filter })` → sets `companies` from `result`, `total` from `count`.
- **Errors**: `errorParser` on failure; `fetchCompaniesError` state (not consumed by `CustomCompanyTable`).

### `src/utils/api-staff-allocation.js` (`StaffAllocationAPI`)

- **`getCompanies`**: `GET /companies` with `params`: `limit`, `skip`, `sort_option`, `sort_order`, and **spread `...filter`** into query string.
- **Base URL**: `API_STAFF_ALLOCATION_URL`, else production `https://resource-allocator.sleek.sg`, else `http://localhost:3015`.
- **JSDoc** `CustomCompany`: includes `_id`, `name`, `registration_id`, `internal_id`, emails/phones, `resource_allocations`, timestamps, etc.

### `src/views/admin/customer-support/custom-list/custom-company-row.js` (`CustomCompany`)

- **Row**: row index, linked **name** (truncated) → `/admin/customer-support/company/?cid={_id}`, `registration_id`, formatted `updated_at` / `created_at`.

### `src/components/new-admin-side-menu.js`

- Nav item `key="customer-support"`, `href="/admin/customer-support/"`.
