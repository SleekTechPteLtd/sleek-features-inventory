# Reassign current task

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Reassign current task |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (staff on **sleek-website** admin **Workflow** list; `sidebarActiveMenuItemKey="camunda-workflow"`) |
| **Business Outcome** | Staff can correct who owns the active Camunda user task from the workflow list so work is routed to a valid user in the workflow engine without opening the task detail view. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow list** (`/admin/sleek-workflow/` — webpack entry `admin/sleek-workflow`) — **Assigned to** column on each row (react-select). |
| **Short Description** | For a selected row, the admin picks another user from grouped options. The app first resolves the user in Camunda via `validateCamundaUser` (email query to `GET /v2/sleek-workflow/user`). If the user exists, it posts `{ userId, taskId }` to `POST /v2/sleek-workflow/task/assignee` and updates local row state (`currentTask.assignee`, `currentTask.email`). If not, it shows a Blueprint alert: *User does not exist in Workflow Engine*. |
| **Variants / Markets** | Tenant-aware labels/filters elsewhere on the page (`tenant` on table); assignee list comes from platform-loaded `assigneeGroups` / `assigneeOptions`. No market hardcoded in assignee flow — **SG, HK, UK, AU** typical for Sleek multi-tenant; exact scoping **Unknown** without backend rules. |
| **Dependencies / Related Flows** | **Camunda** task identity (`row.currentTask.id`). **sleek-back** (or WFE) implements `GET /v2/sleek-workflow/user` and `POST /v2/sleek-workflow/task/assignee`. Parent **WorkFlowList** (`index.js`) loads processes/tasks and passes `updateAssignee` to refresh UI. Related: per-task **Assignee** in `workflow-task/tasks/common/ui/assignee.js` (same API pattern, not this feature’s files). |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/components/assignee.js`, `components/table.js`, `index.js`, `services/api-camunda.js`, `services/services.js`. **Backend**: API host from `getBaseUrl()` — implementation not in this repo. |
| **DB - Collections** | **None in the SPA.** Task assignee persistence is server-side (Camunda / workflow service). MongoDB collections for this path **Unknown** from **sleek-website** code alone. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC for `/v2/sleek-workflow/task/assignee` and user listing; whether `userId` in UI state matches Camunda’s assignee field semantics across all workflow types. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-website — `src/views/admin/sleek-workflow/components/assignee.js`

- **Imports**: `updateAssignee` from `../services/api-camunda`; `validateCamundaUser` from `../services/services`.
- **`handleChange`**: Reads `row.currentTask.id` as `taskId`, selected option `email`; `await validateCamundaUser({email})`.
- **Empty user**: `isEmpty(user)` → `setState` soft alert *User does not exist in Workflow Engine*.
- **Success**: `userId = user[0].id`; `updateAssignee({ body: JSON.stringify({ userId, taskId }) })`; then `this.props.updateAssignee({ email, userId }, index)`.
- **UI**: `react-select` with `assigneeGroups`, value matched to `row.currentTask.email`, placeholder *Select assignee*.

### sleek-website — `src/views/admin/sleek-workflow/services/services.js`

- **`validateCamundaUser`**: Builds query from `options` (e.g. `email=`), calls `getUser(baseQuery)`, returns `get(result, "data", []).filter(camundaUser => camundaUser.email)`.

### sleek-website — `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getUser`**: `GET` `` `${getBaseUrl()}/v2/sleek-workflow/user` `` + query string.
- **`updateAssignee`**: `POST` `` `${getBaseUrl()}/v2/sleek-workflow/task/assignee` `` via `postResource`.

### sleek-website — `src/views/admin/sleek-workflow/components/table.js`

- **Column**: `WORKFLOW_TABLE_HEADERS.ASSIGNED_TO`; header has no filter dropdown on that column (`row.id !== "assigned_to"` for `renderFilterDropDown`).
- **Row**: **Assigned to** `TableCell` renders `<Assignee row={row} updateAssignee={this.updateAssignee} assigneeGroups assigneeOptions />`; `updateAssignee` delegates to `this.props.updateAssignee`.
- **Navigation**: Row click opens `/admin/sleek-workflow/workflow-task/?processId=...&processInstanceId=...` (separate from assignee control).

### sleek-website — `src/views/admin/sleek-workflow/index.js`

- **`WorkFlowList`**: `sidebarActiveMenuItemKey="camunda-workflow"`; loads data then renders `Table` with `updateAssignee={this.updateAssignee}`.
- **`updateAssignee(assignee, index)`**: Updates `taskRows[index].currentTask.assignee` and `.email` from `assignee.userId` / `assignee.email`.

### Build

- Webpack: `paths.js` entry `admin/sleek-workflow` → `./src/views/admin/sleek-workflow/index.js`; HTML `admin/sleek-workflow/index.html`.
