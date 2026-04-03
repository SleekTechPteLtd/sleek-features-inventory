# Manage paid incomplete orders queue

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage paid incomplete orders queue |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (authenticated Sleek admin users) |
| **Business Outcome** | After payment, companies can still lack complete company details; operations can prioritize and work that backlog, assign the right Corp Sec owner, record contact status, and jump to context—so paid signups are progressed without losing visibility. |
| **Entry Point / Surface** | **sleek-website** admin: **Paid Incomplete Orders** — React view mounted on `#root` from `views/admin/paid-incomplete-orders/index.js` (exact public path not asserted in file; typically an admin route serving this bundle). **Back** navigates to `/admin/dashboard`. Company name links to `/admin/company-overview/?cid=…&currentPage=Overview`; comment icon to same with `openCommentHistory=true`. |
| **Short Description** | Lists companies in status `paid_and_awaiting_company_detail` (with `removeEmptyNames`, pagination, optional name search, sortable columns). For **GB** tenant, queries also require `appOnboardingVersion: Beta`. Operators assign a **Corp Sec** staff member via resource allocation key `sales-backup` (`PUT /companies/:id/company-resource-allocations`), which triggers `updateExistingDeadlineAssigneesViaStaffAssigned` to sync active **deadlines** Camunda workflow task assignees. Contact follow-up is tracked with `contact_status` (`PUT /companies/:id` with admin). Latest inline comment preview with link to full history on company overview. |
| **Variants / Markets** | **GB** tenant: extra filter `appOnboardingVersion: "Beta"`. Multi-tenant platform elsewhere; typical Sleek markets **SG, HK, UK, AU** — exact RBAC and company-data rules per tenant **Unknown** without backend review. |
| **Dependencies / Related Flows** | **sleek-back** (or API host): `GET /admin/company-data` (via `retrieveCompanyData` with `admin: true`), `PUT /companies/:companyId`, `PUT /companies/:companyId/company-resource-allocations`, `GET /admin/groups`, `GET /admin/users/admins` (by `group_id`). **Sleek workflow / Camunda**: `getSleekWorkflowProcesses`, `getProcessTaskList`, `updateAssignee`, `getUser` (from `views/admin/sleek-workflow/services/api-camunda.js`) for deadline assignee sync. **Session**: `getUser` for auth. Downstream: **Company overview** for detail and comment history. |
| **Service / Repository** | **sleek-website** (admin view, `api.js`, workflow `services.js`). **sleek-back** (REST implementation; not read in this pass). |
| **DB - Collections** | **Unknown** from these view files (persistence is server-side). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `handleClickTableHeader` calls `fetchCompanies(page, sortByToUse, currentSortOrder)` but `fetchCompanies`’s second parameter is **search** (`name`), not `sortBy` — sorting may be incorrect when used (confirm intended argument order vs search flow). Whether a dedicated webpack route path exists for this page is **Unknown** from the view file alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/paid-incomplete-orders/index.js` (`PaidIncompleteOrdersView`)

- **Bootstrap**: `domready` → `ReactDOM.render` → `AdminLayout` with `hideDrawer={true}`, `sidebarActiveMenuItemKey="dashboard"`.
- **Queue load**: `retrieveCompanyData({ query, admin: true })` with `status: "paid_and_awaiting_company_detail"`, `removeEmptyNames: true`, `skip`, `sortBy`, `sortOrder`, `requestFrom: "paidIncompleteOrderPage"`, optional `name` (search), and for `platformConfig.tenant === "gb"` → `appOnboardingVersion: "Beta"`.
- **Directory for agents**: `getGroups` → filter groups named in `PAID_INCOMPLETE_ORDER_AGENT_GROUP` (**Corp Sec**); `getAdminsByGroup` with `group_id` per group; flattened user list for `MaterialSelect` options.
- **Agent assignment**: `updateCompanyResourceAllocation(company._id, { body: JSON.stringify({ resourceAllocation: { [PAID_INCOMPLETE_ORDER_AGENT]: event.value } }) })` where `PAID_INCOMPLETE_ORDER_AGENT` is `"sales-backup"` from constants.
- **Deadline side effect**: After allocation update, `updateExistingDeadlineAssigneesViaStaffAssigned(company, platformConfig)`.
- **Contact status**: `editCompany(company._id, { admin: true, body: JSON.stringify({ contact_status: event.value }) })`; options from `PAID_INCOMPLETE_ORDER_CONTACT_STATUS`.
- **Comments**: `getCompanyLatestComment` uses `company.comments[0]` as latest; `viewCompanyComment` builds company overview URL with `openCommentHistory=true`.
- **Pagination / search**: 20 per page; search on Enter / button sets `beginDataFetch` to refetch with `name` query.

### `src/utils/company-order-constants/incomplete-order.js`

- **Paid queue contact statuses**: `pendingCustomer`, `pendingSleek`, `partialPayment`, `blockedByWf` with display labels.
- **Paid queue agent scope**: `PAID_INCOMPLETE_ORDER_AGENT_GROUP = ["Corp Sec"]`, `PAID_INCOMPLETE_ORDER_AGENT = "sales-backup"` (resource allocation type key for the dropdown).

### `src/views/admin/sleek-workflow/services/services.js` (`updateExistingDeadlineAssigneesViaStaffAssigned`)

- Loads active deadline processes: `getSleekWorkflowProcesses` with `workflow_type=deadlines`, `backend_company_id`, `status=active`; filters workflows in `NEW` or `ACTIVE` state.
- For each process: `getProcessTaskList` by `businessKey`; drops tasks with `deleteReason`.
- Resolves assignee emails from `setResourceAllocationValues` → `companyStaff` keys (`accounting-team-leader`, `accounting-bookkeeper`, `tax-executive`) matched to Camunda users (`validateCamundaUser`), then `updateTaskAssignee` for tasks whose names fall under `DEADLINES.DESIGNATED_STEPS` accountant or tax paths.

### `src/utils/api.js`

- **Company list**: `retrieveCompanyData` → `GET ${getBaseUrl()}/company-data` (admin prefix → `/admin/company-data` when `admin: true`).
- **Resource allocation**: `updateCompanyResourceAllocation` → `PUT ${getBaseUrl()}/companies/${companyId}/company-resource-allocations`.
- **Company patch**: `editCompany` → `PUT ${getBaseUrl()}/companies/${companyId}` (admin flows use `admin: true` where passed through options for URL rewrite).
- **Groups / admins**: `getGroups` → `GET …/admin/groups`; `getAdminsByGroup` → `GET …/admin/users/admins` with query `group_id`.
