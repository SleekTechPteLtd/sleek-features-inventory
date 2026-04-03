# Validate and update task assignee

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Validate and update task assignee |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (Camunda task ownership updates); **Admin** triggers the same validate-and-POST path from the workflow list **Assigned to** control |
| **Business Outcome** | Task assignee changes only apply when the target user exists in the workflow engine, and the Camunda task is updated through a single backend contract (`userId` + `taskId`). |
| **Entry Point / Surface** | **Manual:** **sleek-website** admin **Workflow** list (`/admin/sleek-workflow/`) — **Assigned to** column (`Assignee` react-select). **System-driven:** `services.js` — `updateTaskAssignee` (used after resolving users via `validateCamundaUser` / `getCamundaDetailsViaEmail`, e.g. deadline initialization and staff-based deadline reassignment). |
| **Short Description** | Resolves a user in the workflow engine, then posts the assignee update. **Lookup:** `validateCamundaUser` builds a query string, calls `GET /v2/sleek-workflow/user`, and returns Camunda users that have an `email`. **Update:** `updateAssignee` sends `POST /v2/sleek-workflow/task/assignee` with JSON `{ userId, taskId }`. The admin UI path requires a non-empty match before calling update; otherwise it alerts that the user does not exist in the workflow engine. |
| **Variants / Markets** | **Unknown** for assignee rules in code; Sleek admin is multi-tenant. API base URL is env-based (`getBaseUrl()` — production `https://api.sleek.sg`, else `http://localhost:3000`). |
| **Dependencies / Related Flows** | **Sleek API** `GET /v2/sleek-workflow/user`, `POST /v2/sleek-workflow/task/assignee`. **Camunda** task id and workflow-engine user id. **Related:** workflow list row refresh (`updateAssignee` prop from parent), **deadline** flows (`initializeDeadlineAssignees`, `updateExistingDeadlineAssigneesViaStaffAssigned`) that call `updateTaskAssignee` with pre-validated assignees. |
| **Service / Repository** | **sleek-website:** `src/views/admin/sleek-workflow/components/assignee.js`, `src/views/admin/sleek-workflow/services/services.js`, `src/views/admin/sleek-workflow/services/api-camunda.js`. **Backend** implementing the v2 routes: **Unknown** repo name from this codebase (not in **sleek-website**). |
| **DB - Collections** | **None in the SPA.** Assignee persistence is server-side (Camunda / workflow service). MongoDB collections for this path **Unknown** from **sleek-website** alone. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High (API paths and payloads in repo); **Medium** for all call sites of `updateTaskAssignee` across product areas without full repo scan |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC and session requirements for `/v2/sleek-workflow/user` and `/v2/sleek-workflow/task/assignee`; whether `memberOfGroup` and other query params on user lookup are enforced server-side. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/components/assignee.js`

- **Imports:** `updateAssignee` from `../services/api-camunda`; `validateCamundaUser` from `../services/services`.
- **`handleChange`:** Reads `row.currentTask.id` as `taskId` and selected option `email`; `await validateCamundaUser({ email })`.
- **Validation failure:** `isEmpty(user)` → Blueprint `Alert`: *User does not exist in Workflow Engine*.
- **Success:** `userId = user[0].id`; `await updateAssignee({ body: JSON.stringify({ userId, taskId }) })`; then `this.props.updateAssignee({ email, userId }, index)` for local row state.

### `src/views/admin/sleek-workflow/services/services.js`

- **`validateCamundaUser(options)`:** Builds `?key=value` from `options`, calls `getUser(baseQuery)`, returns `get(result, "data", []).filter(camundaUser => camundaUser.email)` (only users with an email).
- **`updateTaskAssignee(assignee, task)`:** If `assignee` is non-empty, takes `userId` from `assignee.id`, `taskId` from `task.id`, then `await updateAssignee({ body: JSON.stringify({ userId, taskId }) })`. Used when assignee is already a resolved Camunda user object (e.g. deadline flows).
- **Other usages of `validateCamundaUser`:** With `memberOfGroup: "deadlines"` for deadline user lists; without args in `updateExistingDeadlineAssigneesViaStaffAssigned` to load Camunda users for matching by email.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getUser(options)`:** `GET` `` `${getBaseUrl()}/v2/sleek-workflow/user` `` + query string (`options` is the query suffix, e.g. `?email=...`).
- **`updateAssignee(options)`:** `POST` `` `${getBaseUrl()}/v2/sleek-workflow/task/assignee` `` with `postResource` (JSON body supplied by caller).
- **Shared client behaviour:** `getDefaultHeaders()`, `handleResponse` / `checkResponseIfAuthorized` on JSON responses.
