# Filter and sort workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Filter and sort workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Operations and support can narrow the Camunda workflow process list to the right company, status, type, and creation window, and order results by created date so they can triage work efficiently. |
| **Entry Point / Surface** | Sleek Admin > Workflow (Camunda workflow list; `AdminLayout` with `sidebarActiveMenuItemKey="camunda-workflow"`; task drill-down opens `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…`) |
| **Short Description** | Column-header filters on the workflow table drive query params on `GET /v2/sleek-workflow/processes` (`backend_company_id`, `status`, `workflow_type`, `created_from` / `created_to`, `ordering`). The Date created column combines a Blueprint `DateRangeInput` with ascending/descending sort. A breadcrumb link (“Workflow list”) clears the primary filters and refetches. Filter selections for company, status, and workflow type are persisted in `localStorage` under `workflowFilter` (with `fromFilterDetails` used when returning from detail navigation). |
| **Variants / Markets** | Workflow type options are tenant-scoped via `CAMUNDA_WORKFLOW_TABLE_CONSTANTS.WORKFLOW_TYPE` keyed by `tenant` from `getPlatformConfig()` (defaults in constants when tenant key missing); markets as deployed in CMS — Unknown |
| **Dependencies / Related Flows** | `getSleekWorkflowProcesses` / `getSleekWorkflowProcessTasks` (Camunda-backed listing); `api.getCompanies` for company combobox; `api.getGroups` + `api.getAdminsByGroup` for assignee group options; pagination and rows-per-page reset offset and re-call `initialize`; related: per-row assignee updates (`updateAssignee`) and opening workflow tasks in a new tab |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (process state is served by the sleek-workflow API / Camunda; no MongoDB access from these view files) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `clearFilter` resets only `companyName`, `workflowStatus`, and `workflowType` in state and localStorage — not `dateRange`, `assignedTo`, or `currentTask`, so breadcrumb may leave some UI filter state out of sync with the cleared API query. `handleFilterChange` builds the API query from `companyName`, `workflowStatus`, `workflowType`, and `dateRange` only; `assignedTo` / `currentTask` updates from `table.js` are not appended to the process list query string in `index.js`. The current-task column header includes a comment “FILTERING INTEGRATION TO FOLLOW” and references `setFilterState` / `getCommaSeparetedValues` / `getTasksList`, which are not defined on `CustomPaginationActionsTable` in this file — verify runtime behavior. The Assigned To column explicitly omits a header filter (`row.id !== "assigned_to"`). `localStorage.setItem("workflowFilter", …)` only stores three fields, so date and multi-select filters may not restore after reload. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/index.js` (`WorkFlowList`)

- **Breadcrumb reset**: `<a className={"pt-breadcrumb"} onClick={this.clearFilter}>Workflow list</a>`; `clearFilter` sets `defaultFilterValues` to nulls for company, status, and type, writes `workflowFilter` to localStorage, and calls `initialize(10, 0, "", this.state.ordering)` (lines 115–125, 186–190).
- **Filter → API query**: `handleFilterChange` merges `defaultFilterValues`, then builds `filter` with `&backend_company_id=`, `&status=`, `&workflow_type=`, `&created_from=` / `&created_to=` (lines 160–179).
- **List fetch**: `initialize` calls `getSleekWorkflowProcesses` with `query: \`limit=${limit}&offset=${offset}${filter}${ordering}&need_task_obj=false\`` (lines 242–246).
- **Sort**: `handleOrderChange` passes `ordering` through to `initialize` (lines 181–184).
- **Filtered state flag**: `getFilterString` sets `isFiltered` from company, status, or workflow type only (lines 199–202).

### `src/views/admin/sleek-workflow/components/table.js` (`CustomPaginationActionsTable`)

- **Header filter row**: `headRows` defines Status, Workflow, Company name, Current task, Assigned to, Date created; filter dropdowns render for every column except Assigned to (`row.id !== "assigned_to"`) (lines 456–463, 1067–1079).
- **Date column**: Popover with `DateRangeInput`, `handleDateRangeChange` → `handleFilterChange("dateRange", …)`; `sortByDateCreated` → `handleOrderChange(\`&ordering=${sortOrder}\`)` with `"asc"` / `"desc"` (lines 733–779, 776–854).
- **Single-select filters**: Status, workflow type, and company use `react-select` with `getFilterFieldName` mapping to `workflowStatus`, `workflowType`, `companyName` (lines 636–731, 883–906).
- **Company search**: `onInputChange` calls `getCompanies` with `name` when the user types (lines 758–766).

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **Processes endpoint**: `getSleekWorkflowProcesses` → `GET ${getBaseUrl()}/v2/sleek-workflow/processes` with optional `query` string (lines 126–128).
