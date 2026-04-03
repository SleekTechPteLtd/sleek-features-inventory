# Force process status via WFE

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Force process status via WFE |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Marketing admin (authenticated staff; intended gate is `manage_workflows === "full"` on comparable admin workflow tables — **Unknown** for this exact view; see Open Questions) |
| **Business Outcome** | Staff can mark a Camunda-backed workflow process as **cancelled** or **done** through the backend workflow-engine admin API when normal task completion is not appropriate. |
| **Entry Point / Surface** | **sleek-website** admin workflow list UI: `src/views/admin/sleek-workflow/components/table.js` — confirmation modals **“Mark as Cancelled”** / **“Mark as Done”** (`ModalForceChangeStatus`). **Note:** This `table.js` wires modals and handlers but does **not** render row action buttons to open them (unlike `src/views/admin/new-workflow/components/table.js`), so the trigger surface for this view may be incomplete or duplicated elsewhere. |
| **Short Description** | From the table, `handleApprove` builds a JSON body with process id, target status (`CANCELED` or `DONE` from `WORKFLOW_CONSTANTS.PROCESS_STATUS`), company id/name, and workflow name, then calls `updateProcessStatusForce` which **PUT**s to `/v2/admin/workflow/api/processes/{processId}/change-status`. On success the row is updated locally (status chip; for DONE, current task title is set to the “all tasks completed” label). |
| **Variants / Markets** | **Multi-tenant** context exists (`tenant` drives workflow-type filters in the same module). Typical Sleek markets **SG, HK, UK, AU**; per-tenant availability of force status — **Unknown** without backend confirmation. |
| **Dependencies / Related Flows** | **Client**: `updateProcessStatusForce` (`src/utils/api-wfe.js`). **Upstream**: user/session via `getDefaultHeaders()` and `checkResponseIfAuthorized` on response. **Downstream**: backend admin workflow API (workflow-engine / sleek-back) applies status change in Camunda or persistence — **not read in this pass**. **Related UI**: `new-workflow` table implements the same pattern with visible IconButton triggers and `manage_workflows` checks. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/components/table.js`, `src/views/admin/sleek-workflow/components/modal-force-change-status.js`, `src/utils/api-wfe.js`, `src/utils/constants.js` (`WORKFLOW_CONSTANTS.PROCESS_STATUS`). **Backend** implementing `PUT …/change-status` — **Unknown** repo name from this pass. |
| **DB - Collections** | **Unknown** from these files (HTTP only; server-side DB/Camunda). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | **sleek-workflow** `table.js` has no per-row controls calling `handleForceCancelChangeStatusToggle` / `handleForceDoneChangeStatusToggle` (contrast `new-workflow` table). Are modals dead code here, or are triggers injected by another wrapper? Exact RBAC on `PUT /v2/admin/workflow/api/processes/:id/change-status` in sleek-back. Whether error feedback to the user is sufficient (`handleApprove` catch only resets loading without `handleAlert` on failure). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/utils/api-wfe.js`

- **`updateProcessStatusForce(params, options)`** — `PUT` `${getBaseUrl()}/v2/admin/workflow/api/processes/${params.processId}/change-status` via `putResource` (uses `getDefaultHeaders()`, JSON handling in `handleResponse`, `checkResponseIfAuthorized`).
- Exported as **“GENERIC ENDPOINTS FOR WFE”** alongside other admin workflow routes.

### `src/views/admin/sleek-workflow/components/table.js`

- Imports **`updateProcessStatusForce`** from `../../../../utils/api-wfe`.
- **`handleApprove(process, approveValue, component)`** — guards concurrent calls with `isModalLoading`; builds `payload.body` as JSON: `id`, `status` (approve value), `company_id`, `company_name`, `workflow_name`; calls `await updateProcessStatusForce({ processId }, payload)`; on success updates local `process.status` for `CANCELED` or `DONE`; for `DONE` sets `process.currentTask.title` to `WORKFLOW_CONSTANTS.COMMON.LIST.ALL_TASK_COMPLETED_CURRENT_TASK`; `finally` clears modal state and `lastSelectedProcess`.
- **`handleForceCancel` / `handleForceDone`** — delegate to `handleApprove` with `WORKFLOW_CONSTANTS.PROCESS_STATUS.CANCELED` / `.DONE`.
- **`ModalForceChangeStatus`** (×2) — titles “Mark as Cancelled” / “Mark as Done”; `handleProceed` maps to `handleForceCancel` / `handleForceDone`; receives `handleAlert` from props (not used in `handleApprove` error path).

### `src/views/admin/sleek-workflow/components/modal-force-change-status.js`

- Material-UI `Dialog` with Cancel / Proceed; **`handleProceed(lastSelectedProcess)`** on Proceed.

### `src/utils/constants.js` (referenced)

- **`WORKFLOW_CONSTANTS.PROCESS_STATUS`**: includes **`CANCELED`**, **`DONE`** (and labels used for UI chips elsewhere).
