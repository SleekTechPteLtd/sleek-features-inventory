# Operate Sleek workflow backlog

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Operate Sleek workflow backlog |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (authenticated Sleek admin staff) |
| **Business Outcome** | Operations can see Camunda-backed workflow instances across clients, narrow them to the right company and situation, move ownership of active work, and correct process outcome when exceptions require it—keeping incorporation, compliance, and related flows visible and under control. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow list** at `/admin/sleek-workflow/` — `AdminLayout` with `sidebarActiveMenuItemKey="camunda-workflow"`; row click opens `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…` in a new tab. |
| **Short Description** | Loads and paginates process instances via `GET /v2/sleek-workflow/processes`, enriches rows with tasks and variables from `GET /v2/sleek-workflow/processes/tasks`, and renders status, workflow name (with tenant-specific labelling), company, current task, assignee, and created date. Column filters and sorting drive query params (`backend_company_id`, `status`, `workflow_type`, `created_from`/`created_to`, `ordering`). Operators reassign the current task through `POST /v2/sleek-workflow/task/assignee` after resolving the user in Camunda, and may force a process to **Cancelled** or **Done** via `PUT /v2/admin/workflow/api/processes/:processId/change-status` (`updateProcessStatusForce`). Assignee options come from admin groups (`getGroups`, `getAdminsByGroup`). |
| **Variants / Markets** | Multi-tenant: workflow-type filter options use `WORKFLOW_TYPE` keyed by `tenant` from `getPlatformConfig()`; typical Sleek markets **SG, HK, UK, AU**. Exact RBAC and API rules per tenant **Unknown** without sleek-back review. |
| **Dependencies / Related Flows** | **sleek-back** (or workflow service): `/v2/sleek-workflow/processes`, `/v2/sleek-workflow/processes/tasks`, `/v2/sleek-workflow/task/assignee`, `/v2/sleek-workflow/user`; **WFE admin**: `/v2/admin/workflow/api/processes/:processId/change-status`. **Camunda** (via backend). **Session / directory**: `api.getUser`, `api.getCompanies`, `api.getGroups`, `api.getAdminsByGroup`. Downstream: workflow task UI at `/admin/sleek-workflow/workflow-task/`. Related inventory: browse/filter/assign/force-status split docs under `marketing/admin-sleek-workflow/`. |
| **Service / Repository** | **sleek-website** (views, `api-camunda.js`, `api-wfe.js`). **sleek-back** (implements REST surfaces; not read in this pass). |
| **DB - Collections** | **Unknown** from these view files (all data via REST; persistence is server-side / Camunda and app DB). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `Filter` (`filter.js`) is imported in `index.js` and exposed from `renderPrimaryToolbarContent`, but `render()` only supplies `renderBodyContent()` to `AdminLayout`, so the toolbar filter may be unused in the live tree—confirm whether another route wraps it. `handleFilterChange` in `index.js` only appends company, status, type, and date range to the processes query; table UI also references `assignedTo` / `currentTask` filter keys that may not reach `initialize` (see `filter-and-sort-workflows.md`). `localStorage` `workflowFilter` omits date range and multi-select fields. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/index.js` (`WorkFlowList`)

- **Layout**: Renders into `#root`; `AdminLayout` with `sidebarActiveMenuItemKey="camunda-workflow"`, `hideDrawer={true}`.
- **List load**: `initialize(limit, offset, filter, ordering)` → `getSleekWorkflowProcesses` with `need_task_obj=false` and optional `backend_company_id`, `status`, `workflow_type`, `created_from`, `created_to`, `ordering`.
- **Task merge**: `fetchProcessTasks` → `getSleekWorkflowProcessTasks` with `processIds`, `withVariables=true`; `getCurrentTask` picks active task or last completed; merges `companyName` / `companyId` from variables.
- **Filters / storage**: `handleFilterChange`, `clearFilter`, `workflowFilter` / `fromFilterDetails` in `localStorage`.
- **Directory**: `getAssignees` → `getGroupWithUsers` → `api.getGroups`, `api.getAdminsByGroup`; `getCompanies` for company options.
- **Tenant**: `getPlatformConfig()` → `tenant` in state (passed to table for workflow-type options).

### `src/views/admin/sleek-workflow/components/table.js`

- **Navigation**: `handleOpen` → `/admin/sleek-workflow/workflow-task/?processId=&processInstanceId=` in new tab.
- **Filters**: Column-header `Select` / `DateRangeInput` for status, workflow type, company, date range, sort; uses `CAMUNDA_WORKFLOW_TABLE_CONSTANTS`, tenant-scoped `WORKFLOW_TYPE`.
- **Force status**: `updateProcessStatusForce` from `api-wfe` with body `id`, `status`, `company_id`, `company_name`, `workflow_name`; `ModalForceChangeStatus` for cancel vs done; `handleApprove` maps UI to `WORKFLOW_CONSTANTS.PROCESS_STATUS`.
- **Assignee column**: Renders `Assignee`; pagination (`material-ui-flat-pagination`), rows-per-page.

### `src/views/admin/sleek-workflow/components/filter.js`

- **Controls**: React-select for company (with `getCompanies` typeahead), `tasksStatus`, and `flowClasses` — parallel to list filtering concerns; wiring to parent `handleFilterChange` uses keys `companyName`, `tasksStatus`, `flowClass` (differs from `index.js` `workflowStatus` / `workflowType` naming).

### `src/views/admin/sleek-workflow/components/assignee.js`

- **Reassign**: `validateCamundaUser({email})` → `getUser` on sleek-workflow API; on success `updateAssignee` with `{userId, taskId}` JSON body; `props.updateAssignee` updates local row state.

### `src/views/admin/sleek-workflow/components/modal-force-change-status.js`

- **UX**: Material-UI `Dialog`; **Proceed** calls `handleProceed(lastSelectedProcess)` (wired to force cancel/done in table).

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **Listing**: `getSleekWorkflowProcesses` → `GET ${base}/v2/sleek-workflow/processes`; `getSleekWorkflowProcessTasks` → `GET …/processes/tasks`.
- **Assignee**: `updateAssignee` → `POST ${base}/v2/sleek-workflow/task/assignee`.
- **User lookup**: `getUser` → `GET ${base}/v2/sleek-workflow/user` + query string.

### `src/utils/api-wfe.js`

- **Force status**: `updateProcessStatusForce(params, options)` → `PUT ${base}/v2/admin/workflow/api/processes/${processId}/change-status`.
