# Browse paginated workflow list

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Browse paginated workflow list |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Marketing admin (authenticated staff using the Sleek admin area) |
| **Business Outcome** | Staff can see Camunda-backed workflow instances at a glance, filter and page through them, and open a specific process to work tasks without guessing IDs or status. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow list** at `/admin/sleek-workflow/` — `AdminLayout` with `sidebarActiveMenuItemKey="camunda-workflow"`; row click opens `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…` in a new tab. |
| **Short Description** | Loads a paginated list of process instances via `GET /v2/sleek-workflow/processes`, then enriches each row with task details from `GET /v2/sleek-workflow/processes/tasks`. Renders a Material-UI table with status, workflow name (with tenant-specific label tweaks), company name, current task title, assignee controls, and created date; supports filters (company, status, workflow type, date range, ordering), rows-per-page, and offset-based pagination. |
| **Variants / Markets** | **Multi-tenant**: `tenant` from `getPlatformConfig()` drives workflow-type filter options (`WORKFLOW_TYPE` by tenant in table). Typical Sleek markets **SG, HK, UK, AU**; treat exact RBAC and API availability per tenant as **Unknown** unless confirmed in sleek-back. |
| **Dependencies / Related Flows** | **API**: `getSleekWorkflowProcesses`, `getSleekWorkflowProcessTasks` (`api-camunda.js` → `/v2/sleek-workflow/processes`, `/v2/sleek-workflow/processes/tasks`). **Session**: `api.getUser()`, `checkResponseIfAuthorized`. **Assignee picker**: `api.getGroups()`, `api.getAdminsByGroup()`. **Companies filter**: `api.getCompanies()`. **Downstream**: workflow task UI at `/admin/sleek-workflow/workflow-task/`. **Force status** (table): `updateProcessStatusForce` from `api-wfe` for cancel/done modals — adjacent to list browsing. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/index.js`, `src/views/admin/sleek-workflow/components/table.js`, `src/views/admin/sleek-workflow/services/api-camunda.js`, `src/utils/api.js`, `src/utils/config-loader.js`. **sleek-back** (or workflow service): implements `/v2/sleek-workflow/*` — **not read in this pass**. |
| **DB - Collections** | **Unknown** from these views (all data via REST). Persistence for processes/tasks is **server-side** (likely Camunda + app DB); no MongoDB references in the listed files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which sleek-back routes and permissions guard `GET /v2/sleek-workflow/processes` and `…/tasks`? Whether `need_task_obj=false` omits nested task payloads by design and task fetch always batches `processIds` (limit 100 in `fetchProcessTasks`). Whether filters for current task / assigned-to in `table.js` are fully wired to `index.js` query params (some branches reference `handleFilterChange` keys not present in `defaultFilterValues` in `index.js`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-website — `src/views/admin/sleek-workflow/index.js`

- **Shell**: `domready` renders `WorkFlowList` into `#root`; `AdminLayout` hides drawer, sets `sidebarActiveMenuItemKey="camunda-workflow"`.
- **Pagination state**: `limit` (default 10), `offset`, `total`; `handlePaginationClick` / `handleRowsPerPageChange` call `initialize` with updated offset/limit.
- **Data load**: `initialize(limit, offset, filter, ordering)` calls `getSleekWorkflowProcesses` with query `limit`, `offset`, optional filter string (`backend_company_id`, `status`, `workflow_type`, `created_from`/`created_to`), `ordering`, and `need_task_obj=false`.
- **Row shape**: Maps each process to `status` (via `CAMUNDA_WORKFLOW_CONSTANTS.PROCESS_STATUS_LABELS`), `workflow` (`processDefinitionName`), `created` / `finished` (formatted), `processId`, `processInstanceId`, `companyUser`.
- **Task enrichment**: `fetchProcessTasks(100, 0, processIds)` calls `getSleekWorkflowProcessTasks` with `processIds` and `withVariables=true`; `getCurrentTask` picks active task or last completed; merges `companyName` / `companyId` from task variables.
- **Filters**: `handleFilterChange` builds filter query; `localStorage` keys `workflowFilter`, `fromFilterDetails`; `clearFilter` resets and reloads.
- **Other loads**: `getPlatformConfig` → `tenant`; `getUser` (redirect unverified to `/verify/`); `getCompanies` for company filter; `getGroupWithUsers` for assignee metadata.

### sleek-website — `src/views/admin/sleek-workflow/components/table.js`

- **Columns** (`headRows`): Status, Workflow, Company name, Current task, Assigned to, Date created — matches `WORKFLOW_TABLE_HEADERS` from `camunda-workflow-constants`.
- **Rendering**: Status as colored `Chip`; workflow name via `getWorkflowName` (strips `[PR]`, special cases for deadlines, AGM/AR, CDD); company user suffix; `Assignee` component for assignment; date created column; loading spinners while `companyName` or `currentTask` missing.
- **Pagination UI**: `material-ui-flat-pagination` `Pagination` with `limit`, `offset`, `total`; `NativeSelect` for rows per page (5, 10, 25); displays range `offset+1`–`offset+limit` of `total`.
- **Filters in header**: react-select and Blueprint `DateRangeInput` for date range and sort; filter dropdowns per column (workflow types tenant-scoped via `this.props.tenant`).
- **Navigation**: `handleOpen` → `window.open` workflow-task URL with `processId` and `processInstanceId`.

### sleek-website — `src/views/admin/sleek-workflow/services/api-camunda.js`

- `getSleekWorkflowProcesses`: `GET ${base}/v2/sleek-workflow/processes?${query}`.
- `getSleekWorkflowProcessTasks`: `GET ${base}/v2/sleek-workflow/processes/tasks?${query}`.
