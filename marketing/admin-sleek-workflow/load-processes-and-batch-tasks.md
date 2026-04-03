# Load processes and batch tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Load processes and batch tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Operations staff get a paginated Camunda workflow list where each row includes the current task, assignee, and company fields by batching task fetches instead of per-process calls. |
| **Entry Point / Surface** | Sleek Admin > Workflow (`/admin/sleek-workflow/`); `WorkFlowList` loads on mount, filter change, sort, and pagination via `initialize` |
| **Short Description** | Calls `GET /v2/sleek-workflow/processes` with limit, offset, optional filters, and `need_task_obj=false`, builds table rows from process metadata, then calls `GET /v2/sleek-workflow/processes/tasks` with `processIds` and `withVariables=true`. Merges each process row with matching task list, variables, current task (`getCurrentTask`), assignee, and `company_name` / `company_id` from variables. |
| **Variants / Markets** | Tenant from platform config (default `sg` in `WorkFlowList`); API base URL follows env (production `https://api.sleek.sg` vs local) |
| **Dependencies / Related Flows** | Sleek API v2 sleek-workflow processes and tasks endpoints; Camunda/workflow backend; downstream: workflow task detail (`/admin/sleek-workflow/workflow-task/`); related: `getCompanies`, `getUser`, assignee groups for table UI |
| **Service / Repository** | sleek-website; Sleek API (`/v2/sleek-workflow/*`) |
| **DB - Collections** | Unknown (persistence and Camunda state in backend API) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `fetchProcessTasks` uses fixed `limit=100` and `offset=0`; behaviour if more than 100 processes match a page is unclear without backend contract — verify whether tasks call must be chunked for large pages |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/index.js` (`WorkFlowList`)

- **`initialize`**: Builds `requestData.query` with `limit`, `offset`, optional `filter` (company, status, workflow type, date range), `ordering`, and `need_task_obj=false` (lines 242–245). Calls `getSleekWorkflowProcesses(requestData)`, maps `response.data.processes` into row objects with status, workflow name, dates, `processId`, `processInstanceId`, `companyUser`, empty `currentTask`/`tasks` (lines 246–275). Sets `total` from `data.count` and `rows` (lines 277–277).
- **Batch tasks**: Collects `processIds` from rows (lines 279–281), awaits `fetchProcessTasks(100, 0, processIds)` (lines 283–284).
- **Merge**: For each row, finds matching entry in `workflowTasks` by `processId`, sets `currentTask` via `getCurrentTask`, `tasks`, `tasksVariables`, `assignee`, `companyName`, `companyId` from variables (lines 285–296). Second `setState` updates `rows` (lines 298–300).
- **`getCurrentTask`**: Picks first active non-hidden task (`startTime`, no `endTime`), else last completed (lines 204–219).
- **`fetchProcessTasks`**: Query `limit`, `offset`, `processIds` (comma-separated from array), `withVariables=true` (lines 304–314).
- **Triggers**: `initialize` from `componentDidMount`, `handlePaginationClick`, `handleRowsPerPageChange`, `handleFilterChange`, `handleOrderChange`, `clearFilter` (various lines).

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getSleekWorkflowProcesses`**: `GET ${getBaseUrl()}/v2/sleek-workflow/processes` with query string from options (lines 126–128).
- **`getSleekWorkflowProcessTasks`**: `GET ${getBaseUrl()}/v2/sleek-workflow/processes/tasks` (lines 131–133).
- **`getBaseUrl`**: `API_BASE_URL` env, else production `https://api.sleek.sg` or `http://localhost:3000` (lines 7–14).
