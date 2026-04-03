# Manage unpaid incomplete orders queue

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage unpaid incomplete orders queue |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (authenticated Sleek admin users) |
| **Business Outcome** | Draft companies that have not yet paid can stall in onboarding; operations can search, sort, and page that backlog, assign the right sales owner, record contact follow-up, and jump to company context—so unpaid signups are triaged and progressed without losing visibility. |
| **Entry Point / Surface** | **sleek-website** admin: **Unpaid Incomplete Orders** — React view mounted on `#root` from `src/views/admin/incomplete-orders/index.js` (exact public route not asserted in file; typically an admin route serving this bundle). **Back** navigates to `/admin/dashboard`. Company name links to `/admin/company-overview/?cid=…&currentPage=Overview`; comment icon to same with `openCommentHistory=true`. |
| **Short Description** | Lists companies in status `draft` (with `removeEmptyNames`, pagination, optional name search, sortable columns). For **GB** tenant, queries also require `appOnboardingVersion: Beta`. Operators assign a **Sales** or **Sales Admin** staff member via resource allocation key `sales-in-charge` (`PUT /companies/:id/company-resource-allocations`), which triggers `updateExistingDeadlineAssigneesViaStaffAssigned` to sync active **deadlines** Camunda workflow task assignees (accounting / tax steps) from company resource allocation. Contact follow-up is tracked with `contact_status` (`PUT /companies/:id` with admin). Latest inline comment preview with link to full history on company overview. |
| **Variants / Markets** | **GB** tenant: extra filter `appOnboardingVersion: "Beta"`. Multi-tenant platform elsewhere; typical Sleek markets **SG, HK, UK, AU** — exact RBAC and company-data rules per tenant **Unknown** without backend review. |
| **Dependencies / Related Flows** | **sleek-back** (or API host): `GET /company-data` (via `retrieveCompanyData` with `admin: true` → admin-prefixed path per client), `PUT /companies/:companyId`, `PUT /companies/:companyId/company-resource-allocations`, `GET …/admin/groups`, `GET …/admin/users/admins` (by `group_id`). **Sleek workflow / Camunda**: `getSleekWorkflowProcesses`, `getProcessTaskList`, `updateAssignee`, `getUser` (from `views/admin/sleek-workflow/services/api-camunda.js`) for deadline assignee sync after allocation changes. **Session**: `getUser` for auth. Downstream: **Company overview** for detail and comment history. |
| **Service / Repository** | **sleek-website** (admin view, `api.js`, workflow `services.js`). **sleek-back** (REST implementation; not read in this pass). |
| **DB - Collections** | **Unknown** from these view files (persistence is server-side). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Sorting invokes `fetchCompanies(page, "", sortByToUse, currentSortOrder)` — the search term is always cleared when changing sort; confirm whether active name search should be preserved. Exact webpack public path for this admin page is **Unknown** from the view file alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/incomplete-orders/index.js` (`IncompleteOrdersView`)

- **Bootstrap**: `domready` → `ReactDOM.render` → `AdminLayout` with `hideDrawer={true}`, `sidebarActiveMenuItemKey="dashboard"`.
- **Queue load**: `retrieveCompanyData({ query, admin: true })` with `status: "draft"`, `removeEmptyNames: true`, `skip`, `sortBy`, `sortOrder`, `requestFrom: "unpaidIncompleteOrderPage"`, optional `name` (search), and for `platformConfig.tenant === "gb"` → `appOnboardingVersion: "Beta"`.
- **Directory for agents**: `getGroups` → filter groups named in `UNPAID_INCOMPLETE_ORDER_AGENT_GROUP` (**Sales**, **Sales Admin**); `getAdminsByGroup` with `group_id` per group; flattened user list for `MaterialSelect` options.
- **Agent assignment**: `updateCompanyResourceAllocation(company._id, { body: JSON.stringify({ resourceAllocation: { [UNPAID_INCOMPLETE_ORDER_AGENT]: event.value } }) })` where `UNPAID_INCOMPLETE_ORDER_AGENT` is `"sales-in-charge"` from `src/utils/company-order-constants/incomplete-order.js`.
- **Deadline side effect**: After allocation update, `updateExistingDeadlineAssigneesViaStaffAssigned(company, platformConfig)`.
- **Contact status**: `editCompany(company._id, { admin: true, body: JSON.stringify({ contact_status: event.value }) })`; options from `UNPAID_INCOMPLETE_ORDER_CONTACT_STATUS`.
- **Comments**: `getCompanyLatestComment` uses `company.comments[0]` as latest; `viewCompanyComment` builds company overview URL with `openCommentHistory=true`.
- **Pagination / search**: 20 per page; search on Enter / button sets `beginDataFetch` to refetch with `name` query.

### `src/utils/company-order-constants/incomplete-order.js`

- **Unpaid queue contact statuses**: `notContacted`, `leftMessage`, `callBackAnotherTime`, `customerWentElsewhere`, `others` with display labels.
- **Unpaid queue agent scope**: `UNPAID_INCOMPLETE_ORDER_AGENT_GROUP = ["Sales", "Sales Admin"]`, `UNPAID_INCOMPLETE_ORDER_AGENT = "sales-in-charge"` (resource allocation type key for the dropdown).

### `src/views/admin/sleek-workflow/services/services.js` (`updateExistingDeadlineAssigneesViaStaffAssigned`)

- Loads active deadline processes: `getSleekWorkflowProcesses` with `workflow_type=deadlines`, `backend_company_id`, `status=active`; filters workflows in `NEW` or `ACTIVE` state.
- For each process: `getProcessTaskList` by `businessKey`; drops tasks with `deleteReason`.
- Resolves assignee emails from `setResourceAllocationValues` → `companyStaff` keys (`accounting-team-leader`, `accounting-bookkeeper`, `tax-executive`) matched to Camunda users (`validateCamundaUser`), then `updateTaskAssignee` for tasks whose names fall under `DEADLINES.DESIGNATED_STEPS` accountant or tax paths (subset compared to `initializeDeadlineAssignees` — no XBRL/AGM/annual-return branches in this function).

### `src/utils/api.js`

- **Company list**: `retrieveCompanyData` → `GET ${getBaseUrl()}/company-data` (admin flows use `admin: true` where passed through options for URL rewrite).
- **Resource allocation**: `updateCompanyResourceAllocation` → `PUT ${getBaseUrl()}/companies/${companyId}/company-resource-allocations`.
- **Company patch**: `editCompany` → `PUT ${getBaseUrl()}/companies/${companyId}` (admin flows use `admin: true` where passed through options).
- **Groups / admins**: `getGroups` → `GET …/admin/groups`; `getAdminsByGroup` → `GET …/admin/users/admins` with query `group_id`.
