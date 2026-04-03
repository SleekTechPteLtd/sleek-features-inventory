# Assign internal owners on selected workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Assign internal owners on selected workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / corpsec admin (staff working Camunda-backed workflows in Sleek admin) |
| **Business Outcome** | For deadlines, AGM/annual return, and UK incorporation flows, internal work is mapped to the right admin groups and individual users so each task has a clear owner and sensitive actions (for example Companies House submission) stay restricted to the correct team. |
| **Entry Point / Surface** | **sleek-website** admin: **Sleek workflow task** at `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…` — `WorkFlowList` in `src/views/admin/sleek-workflow/workflow-task/index.js` with `AdminLayout` (`sidebarActiveMenuItemKey="workflow-task"`, `isSleekWorkflow={true}`). |
| **Short Description** | On initialize, when the process `workflowType` is Deadlines, AGM/AR, or UK incorporation, the page loads all admin groups and members (`getGroups`, `getAdminsByGroup`) and builds grouped and flat assignee pickers. Those props feed deadline steps (task-level assignee updates), AGM/AR tasks (`updateAssignee` + `updateProcessTask`), and UK incorporation (group membership gates who may submit to Companies House). |
| **Variants / Markets** | **SG** (deadlines and related corpsec flows), **UK** (UK incorporation, Companies House). AGM/AR is tied to annual compliance for the company’s jurisdiction as modeled in Camunda (typically **SG** context in this codebase; confirm per tenant). |
| **Dependencies / Related Flows** | **Admin groups API**: `GET /admin/groups`, `GET /admin/users/admins?group_id=…` (`api.getGroups`, `api.getAdminsByGroup` in `utils/api.js`). **Camunda**: `getTaskList` / `getTaskVariables` (`services/api-camunda.js`); `POST /v2/sleek-workflow/task/assignee` (`updateAssignee`) for AGM/AR; `updateProcessTask` for persisting task/process data. **Company/process**: `api.getCompany`, `api.getCompanyUsers`, `getProcessSavedData` (`api-wfe`). **Related**: [Tenant workflow types and assignee directory](../admin-sleek-workflow/tenant-workflow-types-and-assignee-directory.md) (list-level directory); [Validate and update task assignee](../admin-sleek-workflow/validate-and-update-task-assignee.md). |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/workflow-task/index.js`, `src/utils/api.js`, flows `deadlines-process-instance.js`, `agm-ar-process-instance.js`, `uk-incorporation-process-instance.js`, tasks under `tasks/deadlines/`, `tasks/agm-ar/`, `tasks/uk-incorporation/submit-to-companies-house.js`, `src/views/admin/sleek-workflow/services/api-camunda.js`. **Backend** serving admin groups and sleek-workflow assignee endpoints — not fully enumerated here. |
| **DB - Collections** | Unknown from these views (assignees and groups via REST; Camunda/process persistence on server). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `SG_TRANSFER` receives populated `assigneeGroups` (it is passed through from state but `initializeAssigneesLookup` only runs for Deadlines, AGM/AR, UK incorporation — may be empty). Exact tenant rules for which companies see AGM/AR vs deadlines. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/workflow-task/index.js`

- **State**: `assigneeGroups`, `assigneeOptions`, `assignedToFlatList` (initialised empty in `constructor`).
- **Conditional load**: In `initialize()`, after loading tasks and company data, if `processVariables.workflowType` is one of `DEADLINES`, `AGM_AR`, or `UK_INCORPORATION` (`CAMUNDA_WORKFLOW_CONSTANTS`), calls `initializeAssigneesLookup()`.
- **`initializeAssigneesLookup`**: `getAssignees()` then `initAssignedToFlatList()`.
- **`getAssignees` / `getGroupWithUsers`**: `api.getGroups()`; for each group, `api.getAdminsByGroup({ query: { group_id: group._id } })`; builds `assigneeGroups` as `{ label: group.name, options: [{ value, label, first_name, last_name, email }, …] }` and a flat `assigneeOptions`.
- **Pass-through**: `assigneeGroups`, `assigneeOptions`, and `assignedToFlatList` are passed to `DeadlinesProcessInstance` and `AgmArProcessInstance`; `assigneeGroups` only to `UKIncorporationProcessInstance` (used on the Submit to Companies House step).

### `src/views/admin/sleek-workflow/workflow-task/flows/deadlines-process-instance.js`

- Mirrors assignee props into local state; **`updateAssignee`** mutates the current task’s `email` and `assignee` id in the task list for UI consistency.

### `src/views/admin/sleek-workflow/workflow-task/tasks/agm-ar/annual-general-meeting.js`, `annual-return.js`

- Merge options from `assigneeGroups`; on assignee change call **`updateAssignee`** (`POST /v2/sleek-workflow/task/assignee`) and **`updateProcessTask`** to persist.

### `src/views/admin/sleek-workflow/workflow-task/tasks/uk-incorporation/submit-to-companies-house.js`

- **`getCorpsecUser`**: Checks whether `user._id` appears under groups labelled `SLEEK_GROUP_NAMES.CORP_SEC` or `CORP_SEC_ADMIN` in `assigneeGroups`; disables “Send application” for others with an explanatory tooltip.

### `src/utils/api.js`

- **`getGroups`**: `GET ${getBaseUrl()}/admin/groups`.
- **`getAdminsByGroup`**: `GET ${getBaseUrl()}/admin/users/admins` with `group_id` query parameter.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`updateAssignee`**: `POST ${getBaseUrl()}/v2/sleek-workflow/task/assignee`.
