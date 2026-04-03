# Force-validate workflow tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Force-validate workflow tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / Operations User (requires Manage Workflows at full level) |
| **Business Outcome** | Lets authorized staff mark a workflow step as completed without going through the normal task completion path, so incorporation and related flows can be unblocked or corrected when the standard route is impractical or stuck. |
| **Entry Point / Surface** | Sleek Admin — legacy workflow instance viewer: `/admin/workflow/?instanceId={workflowInstanceId}` with optional `&taskId={taskId}`. Per-task **Force Validate** control appears in the right-hand sidebar task list (not on the main task content area). Linked from company overview and corpsec workflow entry points that open this URL pattern. |
| **Short Description** | For each non-completed task in the instance sidebar, operators with `manage_workflows` permission set to `full` see a **Force Validate** button (except for tasks named `User Validation` or `KYC Overview`). Confirming the dialog calls the backend to mark the step done; the view then reloads instance and task data. Errors from the API are shown in an alert. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | **HTTP**: `api.forceValidateWorkflowTask` → `PUT {base}/admin/workflow-tasks/{taskId}/force-validate` (`src/utils/api.js`). Complements **normal completion** via `completeWorkflowTask` → `POST .../admin/workflow-tasks/{taskId}/complete-task` used from `task-viewer.js`. **Related surface**: Camunda Sleek Workflow task drawer uses a separate “FORCE VALIDATE” path (`updateProcessTask` with `is_force_validated: true` in `sleek-workflow/components/drawer.js`) — same business intent, different stack. **Upstream**: `getWorkflowInstance`, `getWorkflowTask`, `getUser` on page load. |
| **Service / Repository** | sleek-website (admin UI); backend API that implements `PUT /admin/workflow-tasks/:id/force-validate` not in this repo |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Server-side enforcement of `manage_workflows` and persistence model for `force-validate` are not visible from this repo. Whether additional markets or workflow types are restricted beyond the two client-side task name exclusions. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page & shell**: `src/views/admin/workflow/index.js` mounts `WorkflowInstanceViewer` into `#root` for the admin workflow bundle (`webpack/paths.js` entry `admin/workflow/index`).
- **Permission gate & sidebar UI**: `src/views/admin/workflow/workflow-instance-viewer.js` — `renderSidebar` shows **Force Validate** only when `user.permissions.manage_workflows === "full"`, task name is not in `HAVE_FORCE_VALIDATE_EXCEPT` (`["User Validation", "KYC Overview"]`), and `task.status` is not `completed`. `shouldDisableTask` still greys out `unavailable` tasks but the **Force Validate** button is rendered for incomplete tasks regardless of that disabled styling on the row (same file).
- **Dialog & action**: `handleForceValidateDialog` / `SleekDialog` copy: “By clicking this, the workflow step will be marked as Done. Would you like to proceed?” — `handleForceValidate` calls `api.forceValidateWorkflowTask(taskId)`, then `fetchBodyData()` on success; `renderErrorMessage` on `Error` with `response.data.message`.
- **API client**: `src/utils/api.js` — `forceValidateWorkflowTask(taskId)` → `putResource(\`${getBaseUrl()}/admin/workflow-tasks/${taskId}/force-validate\`)` (HTTP PUT).
- **RBAC label**: `src/utils/constants.js` — `manage_workflows` permission labeled “Manage Workflows”, associated with workflow sidebar keys including `new-workflow` and `camunda-workflow`.
