# Monitor and manage client workflow operations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Monitor and manage client workflow operations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (Sleek Admin users); force **Cancel** / **Done** on a process requires `user.permissions.manage_workflows === "full"` |
| **Business Outcome** | Internal teams can see all client company workflow processes in one place, narrow work by company, status, flow type, task, assignee, and dates, hand tasks to the right admins, and open a process to continue work so client workflows keep moving. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflows** — `/admin/new-workflow/` — `AdminLayout` with `sidebarActiveMenuItemKey="new-workflow"` and primary title “Workflows” or “Workflow” depending on CMS feature `new_workflow_view` → `view_list.enabled`. Optional deep link: query `companyId` and `workflow` seed filters then clear the URL. Row navigation opens **`/admin/new-workflow/workflow-task/?processId={id}`**. |
| **Short Description** | Loads paginated workflow processes from the WFE admin API, enriches rows with per-process tasks, and supports two UIs behind a feature flag: **legacy** (`Table` + toolbar `Filter`) with company / status / flow-class filters and sortable columns; **new** (`NewTable`) with inline column filters (multi-select for status, workflow name, current task, assignee; company typeahead; date range + sort on created). Assignee dropdowns are grouped by admin **groups**; changing assignee calls task assignment for non-system tasks. Admins with full workflow permission can force process status to **Cancelled** or **Done** via modals. Filter state persists in `localStorage` (`workflowFilter`, `fromFilterDetails`). |
| **Variants / Markets** | Unknown — no market dimension in this view; Sleek commonly **SG, HK, UK, AU**; confirm if WFE filters processes by tenant. |
| **Dependencies / Related Flows** | **WFE / workflow API** (`/v2/admin/workflow/api/...`): `getWorkflowProcesses`, `getWorkflowTasks`, `assignTask`, `updateProcessStatusForce`. **Core API**: `getUser`, `getCompanies`, `getCompany`, `getFlowClasses`, `getGroups`, `getAdminsByGroup`. **Downstream**: admin workflow task detail at `workflow-task` (separate capability). Task filter options from `WORKFLOW_TASKS_FILTER_OPTIONS` + flow classes. |
| **Service / Repository** | **sleek-website**: `src/views/admin/new-workflow/index.js`, `components/filter.js`, `components/table.js`, `components/new-workflow/new-table.js`, `components/assignee.js`, `src/utils/api-wfe.js`, `src/utils/api.js`. **Backend** (not in repo): workflow engine service exposing `/v2/admin/workflow/api/*`; user/group/company APIs on main API. |
| **DB - Collections** | Unknown — **sleek-website** is a client; process/task persistence is in backend services (not evidenced here). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend collections and indexing; whether `getWorkflowTasks` batching behaves correctly for all `count` edge cases; full RBAC matrix for `/v2/admin/workflow/api/processes` beyond session + `manage_workflows`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/new-workflow/index.js` (`WorkFlowList`)

- **Mount**: `domready` → `#root`; `hideDrawer={true}`; loads platform config from `store` for `new_workflow_view` / `view_list.enabled`.
- **Data**: `initialize(limit, offset, filter, ordering)` → `getWorkflowProcesses({ query: \`limit=…&offset=…${filter}${ordering}&need_task_obj=false\` })` → maps `results` to table rows (company, status, workflow title, user name/roles, dates, `processId`, owner); then `fetchProcessTasks` → `getWorkflowTasks` with `process_id` list to attach `currentTask` and `tasks`.
- **Filters** (`handleFilterChange`): builds query segments `backend_company_id`, `status`, `flow_class`, `multi_flow_task`, `assigned_to`, `created_from`/`created_to`; persists to `localStorage`; resets pagination; calls `initialize`.
- **Sort** (`handleOrderChange`): passes `ordering` query (legacy table).
- **Assignee catalog**: `getGroupWithUsers` → `api.getGroups()` then per group `api.getAdminsByGroup({ query: { group_id } })` → `assigneeGroups` / `assigneeOptions`.
- **Supporting**: `getCompanies`, `getFlowClasses`, `getUser` (redirect unverified to `/verify/`); `getFilterDefaultValue` restores filters from URL or `localStorage`.
- **State update on assign**: `updateTaskAssignee` patches `rows[index].tasks[0].owner` after child assignment.

### `src/views/admin/new-workflow/components/filter.js`

- **Legacy toolbar filters** (when new workflow list disabled): react-select for **Company name** (with `getCompanies` typeahead), **Status** (`NEW`, `IN PROGRESS`, `DONE`, …), **Workflow Name** (`flowClasses`).

### `src/views/admin/new-workflow/components/table.js`

- **Legacy table**: Sortable headers (`status`, `title`, `company_name`, `current_task`, `assigned_to`, `created`, `actions`); row click → `workflow-task` with `processId`; `Assignee` on current task; `updateProcessStatusForce` from **Mark as Cancelled** / **Mark as Done** modals (`manage_workflows` full); chips for process status.

### `src/views/admin/new-workflow/components/new-workflow/new-table.js`

- **New table**: Extended columns — user name, user role; inline **Filter** controls per column (multi-select with checkboxes for status, workflow, current task, assignee; company select; date range popover with **Sort ascending/descending** on created); uses `WORKFLOW_TABLE_HEADERS`, `WORKFLOW_TASKS_FILTER_OPTIONS`, `WORKFLOW_CONSTANTS`; same row navigation, assignee, and force status actions as legacy.

### `src/views/admin/new-workflow/components/assignee.js`

- **Assignment**: react-select grouped by `assigneeGroups`; on change, for each task (skip `is_system_task` in task `description` JSON), calls `assignTask(processId, taskId, taskType, taskName, options)` with body `backend_id`, name, email, `is_process: true`; `updateTaskAssignee` for optimistic UI.

### `src/utils/api-wfe.js`

- `getWorkflowProcesses` → `GET ${base}/v2/admin/workflow/api/processes`
- `getWorkflowTasks` → `GET ${base}/v2/admin/workflow/api/tasks`
- `assignTask` → `POST ${base}/v2/admin/workflow/api/tasks/{taskType}/{processId}/{taskName}/{taskId}/assign`
- `updateProcessStatusForce` → `PUT ${base}/v2/admin/workflow/api/processes/{processId}/change-status`

### `src/utils/api.js`

- `getUser` → `GET ${base}/admin/users/me`
- `getCompanies` → `GET ${base}/companies`
- `getGroups` → `GET ${base}/admin/groups`
- `getAdminsByGroup` → `GET ${base}/admin/users/admins` (query `group_id`)
- `getFlowClasses` → `GET ${base}/v2/admin/workflow/api/flows/`
