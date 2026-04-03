# Force cancel or complete workflow

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Force cancel or complete workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (staff with workflow management access; see Evidence for permission pattern in parallel admin list) |
| **Business Outcome** | Staff can override a workflow process’s terminal state to cancelled or completed when the normal path is not appropriate, so operational issues can be cleared without leaving the admin workflow list flow. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow list** (`/admin/sleek-workflow/`) — `WorkFlowList` in `src/views/admin/sleek-workflow/index.js` renders `components/table`; `AdminLayout` uses `sidebarActiveMenuItemKey="camunda-workflow"`. |
| **Short Description** | Two confirmation dialogs (“Mark as Cancelled” / “Mark as Done”) call `updateProcessStatusForce` with a JSON body (`id`, `status`, `company_id`, `company_name`, `workflow_name`). On success, the table row is updated locally (status + current task title when done). `ModalForceChangeStatus` is a Material-UI dialog with Cancel / Proceed. |
| **Variants / Markets** | Multi-tenant via `tenant` on the table (`initWorkflowTypes`). Exact market list not hardcoded — **SG, HK, UK, AU** typical for Sleek; treat others as **Unknown** unless confirmed. |
| **Dependencies / Related Flows** | **sleek-website** `PUT` via `api-wfe.updateProcessStatusForce` → `PUT /v2/admin/workflow/api/processes/:processId/change-status` (backend workflow engine / Camunda). **Parallel UI**: `src/views/admin/new-workflow/components/table.js` and `new-table.js` expose row **IconButton** actions for the same modals and gate with `user.permissions.manage_workflows === "full"` and row status. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/components/table.js`, `modal-force-change-status.js`, `src/utils/api-wfe.js` (`updateProcessStatusForce`). Backend implementation lives outside this repo (WFE admin API). |
| **DB - Collections** | **Unknown** from SPA — persistence is enforced by the workflow backend; **not** inferred here. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | **Medium** — API and modal flow are clear; **sleek-workflow** list table does **not** wire row actions to open the modals in the current file (handlers exist but are unused in `render()`). **High** confidence for the same pattern in **new-workflow** tables where buttons call `handleForceCancelChangeStatusToggle` / `handleForceDoneChangeStatusToggle`. |
| **Disposition** | Unknown |
| **Open Questions** | Whether **sleek-workflow** list intentionally omitted action buttons (legacy vs new-workflow). Whether `WorkFlowList` should pass `handleAlert` into `Table` (modals pass it but it is unused in `modal-force-change-status.js`). Exact RBAC on `PUT .../change-status` (backend). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-website — `src/views/admin/sleek-workflow/components/table.js`

- **Imports**: `updateProcessStatusForce` from `../../../../utils/api-wfe`; `ModalForceChangeStatus`; `WORKFLOW_CONSTANTS` from `../../../../utils/constants`.
- **`handleApprove`**: builds `payload.body` with `id`, `status`, `company_id`, `company_name`, `workflow_name`; calls `updateProcessStatusForce({ processId }, payload)`, then updates local `process.status` for `CANCELED` or `DONE` (and sets `currentTask.title` to “all tasks completed” string when done).
- **State**: `openModalForceCancelChangeStatus`, `openModalForceDoneChangeStatus`, `lastSelectedProcess`, `isModalLoading`.
- **Handlers**: `handleForceCancel`, `handleForceDone` → `handleApprove` with `WORKFLOW_CONSTANTS.PROCESS_STATUS.CANCELED` / `DONE`.
- **Modals** (two instances): titles “Mark as Cancelled” / “Mark as Done”; explanatory copy references platform marking the workflow CANCELLED or DONE.
- **Row UI**: `renderRows()` does not render action buttons that call `handleForceCancelChangeStatusToggle` or `handleForceDoneChangeStatusToggle` (no `actionsColumn` / `IconButton` in this file). Compare `src/views/admin/new-workflow/components/table.js` (~lines 533+) for the same handlers with visible controls and `manage_workflows` permission `full`.

### sleek-website — `src/views/admin/sleek-workflow/components/modal-force-change-status.js`

- Material-UI `Dialog`; **Cancel** closes via `toggleModal`; **Proceed** calls `handleProceed(lastSelectedProcess)`.

### sleek-website — `src/utils/api-wfe.js`

- **`updateProcessStatusForce`**: `PUT` `${getBaseUrl()}/v2/admin/workflow/api/processes/${params.processId}/change-status` via `putResource`.

### sleek-website — `src/utils/constants.js`

- **`WORKFLOW_CONSTANTS.PROCESS_STATUS`**: `DONE`, `CANCELED`, etc., used as API `status` values.

### sleek-website — `src/views/admin/sleek-workflow/index.js`

- Mounts workflow list at admin sleek-workflow entry; passes `Table` props for pagination, filters, rows — **does not** pass `handleAlert` to `Table` (optional for current modal code).
