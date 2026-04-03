# Work assigned operational portfolio in My Tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Work assigned operational portfolio in My Tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operations staff (corpsec, sales, compliance, customer success, accounting groups); Sleek Admin and Sleek Super Admin (member selector enabled to view or act as another user’s portfolio) |
| **Business Outcome** | Staff can see companies and active workflows tied to their resource allocations, narrow by company lifecycle status, and page through the list so day-to-day operational work stays visible and actionable. |
| **Entry Point / Surface** | **sleek-website** admin: **My Tasks** at `/admin/my-tasks/` — `AdminLayout` with `sidebarActiveMenuItemKey="my-tasks"` (drawer hidden on this view). |
| **Short Description** | Loads the signed-in user and a merged member list from key operational groups; Sleek Admin / Super Admin can switch the portfolio to another member. For the selected user, fetches paginated resource allocations from the admin API with optional `company_status` filter, then enriches each company row with active workflow processes from the workflow engine. Presents an expandable table (company name, CMS company status, transfer flag, workflow summary) with rows-per-page and offset pagination; workflow rows open the new-workflow task UI in a new tab. |
| **Variants / Markets** | Company status labels from CMS `admin_constants.COMPANY_STATUSES`. Multi-tenant behaviour follows platform config and backend allocation rules; exact market-specific rules not expressed in these views — **Unknown** without backend review. |
| **Dependencies / Related Flows** | **`api.getUserAllResourceAllocations`** → `GET /admin/user/{userId}/resource-allocation-role` (query: `offset`, `limit`, optional `company_status`). **`getWorkflowProcesses`** (`api-wfe`) → `GET /v2/admin/workflow/api/processes` with `limit`, `offset`, `backend_company_id`. **`api.getAdminsByGroup`** for member dropdown population. Deep link to **`/admin/new-workflow/workflow-task/?processId=…`**. Related: corpsec **My Tasks** (`/admin/corpsec/my-tasks/`) and new-workflow **My Tasks** are separate surfaces. |
| **Service / Repository** | **sleek-website**: `src/views/admin/my-tasks/*`. **sleek-back** (admin user resource allocation APIs; not read here). **Workflow engine / API** (`/v2/admin/workflow/api/processes`). |
| **DB - Collections** | **Unknown** in this repo; allocation and process data are served by backend services (likely MongoDB collections for companies, allocations, and workflow state — confirm in sleek-back / WFE). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `components/filter.js` implements react-select filters (company, workflow status, flow class) but is **not imported** by admin My Tasks in this repo — legacy or future use? `RoleAllocation` passes `handleOrderChange` and `loadingFromFilter` into `Table` but does not define `handleOrderChange` and never sets `loadingFromFilter` (sort UI is commented out in `table.js`). Select markup in `roleAllocation.js` uses `options = {[…]}` as text inside `<select>`; confirm in browser whether options render correctly or need JSX fix. Exact backend collections and RBAC for `GET /admin/user/.../resource-allocation-role`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/my-tasks/index.js` (`MyTasksView`)

- **Mount**: `componentDidMount` — `getPlatformConfig()`, `getUser()` (from `views/admin/common`), then parallel `getAdminsByGroup` for Corp Sec, Sales, Compliance, Customer Success, Accounting (failures logged, non-blocking); merges and `uniqBy` members; fetches Sleek Admin and Sleek Super Admin lists; sets `forceEnableMemberSelection` when current user is in either group; ensures current user appears in dropdown if not in any listed group.
- **Render**: `COMPANY_STATUSES` from `getAppFeatureProp(platformConfig.cmsGeneralFeatureList, "admin_constants").props`; passes `pageTitle="My Tasks"`, `user`, `members`, `companyStatuses`, `forceEnableMemberSelection` to `RoleAllocation`.

### `src/views/admin/my-tasks/roleAllocation.js` (`RoleAllocation`)

- **Data**: `getUserAllocationRoles` → `api.getUserAllResourceAllocations` with `offset`, `limit`, optional `company_status` (`common.js`).
- **Workflow enrichment**: `fetchActiveCompanyWorkflows` → `getWorkflowProcesses` with query `limit`, `offset`, `backend_company_id`; maps process fields to row DTOs including `currentTask` from unfinished tasks or `WORKFLOW_CONSTANTS.COMMON.LIST.ALL_TASK_COMPLETED_CURRENT_TASK`.
- **Handlers**: `handleSelectChange` (member), `handleCompanyStatusChange`, `handlePaginationClick`, `handleRowsPerPageChange` reset offset where appropriate and call `fetchComponentData`.
- **UI**: Native `<select>` for member and company status (intended options built from `members` and `companyStatuses` — see Open Questions for JSX). Renders `Table` with pagination props.

### `src/views/admin/my-tasks/common.js`

- **`getUserAllocationRoles`**: sets `options.query` to `offset`, `limit`, and `company_status` when set; calls `getUserAllResourceAllocations`.
- **`getUserResourceAllocations` / `getUserAllocationRolesByType`**: typed allocation path (not used by main `RoleAllocation` flow in this file).
- **`getCompanies`**: corpsec-style company listing helper with `admin: true` (not invoked by `index` / `RoleAllocation` in this feature path).

### `src/views/admin/my-tasks/components/table.js` (`CustomPaginationActionsTable`)

- **Columns**: Company name (expand), status label from `companyStatuses` + `row.company.status`, transfer yes/no, active workflows count ratio (DONE/REJECTED vs total) or full nested workflow table.
- **Expand**: `openedRowIndex` toggles chevron; expanded row shows `renderActiveWorkflows` full table or spinner while workflows load.
- **Workflow row actions**: `handleOpenWorkflowProcess` → `window.open('/admin/new-workflow/workflow-task/?processId=' + id, '_blank')`.
- **Pagination**: `material-ui-flat-pagination` `Pagination` with `limit`, `offset`, `total`; `NativeSelect` for rows per page 5 / 10 / 25.

### `src/views/admin/my-tasks/components/filter.js` (`Filter`)

- **Behaviour**: `react-select` for company name (with `getCompanies` typeahead), workflow status, and flow class; builds query fragment for `handleFilterChange`. **No import** from `index.js` or `roleAllocation.js` in this module — not part of the shipped My Tasks bundle as wired today.

### `src/utils/api.js`

- **`getUserAllResourceAllocations(userId, options)`**: `GET ${getBaseUrl()}/admin/user/${userId}/resource-allocation-role` with serialized query.

### `src/utils/api-wfe.js`

- **`getWorkflowProcesses`**: `GET ${getBaseUrl()}/v2/admin/workflow/api/processes` with `options.query` string (e.g. `limit`, `offset`, `backend_company_id`).
