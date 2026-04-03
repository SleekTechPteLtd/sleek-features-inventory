# Work client Camunda workflows from admin

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Work client Camunda workflows from admin |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin |
| **Business Outcome** | Lets internal staff open a Camunda-backed workflow instance, work through the task list with correct context and saved state, complete steps including uploads and SleekSign, and move client company processes forward (KYC, incorporations, director and share-structure changes, accounting onboarding, compliance deadlines, AGM/AR, transfers, CDD, SBA onboarding, and related flows). |
| **Entry Point / Surface** | Sleek Admin > Workflow list (Camunda) — deep-link to `/admin/sleek-workflow/workflow-task/?processId={businessKey}&processInstanceId={processInstanceId}` with optional `taskId`, `taskViewOnly`, `taskSpecific`, `fromKYCRefresh` / `companyId` / `companyUserId` for KYC refresh handoff. Breadcrumbs: Workflows → optional “Filtered list” → current workflow title from `CAMUNDA_WORKFLOW_CONSTANTS`. |
| **Short Description** | Shell page `WorkFlowList` loads the process task list and variables via the Sleek Workflow API, hydrates company, saved process data, and per-task variables, then switches on `processVariables.workflowType` to the matching process-instance flow (KYC, SG/HK/UK incorporation, accounting onboarding variants, deadlines, AGM/AR, share-structure amendments, SG transfer, template, director flows, CDD, SBA onboarding, etc.). Supports task selection and URL updates, reload after document changes, SleekSign send confirmation, assignee directory for selected flows, and KYC drawer data when applicable. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | **HTTP**: `api-camunda.js` — `POST /v2/sleek-workflow/task-list` (task list + variables + process metadata), `GET /v2/sleek-workflow/tasks/{taskId}/variables`, plus broader Camunda workflow routes (start/update task, SleekSign, processes/tasks, external tasks, assignee, UK/SG/HK helpers, etc.). **WFE**: `api-wfe.js` — `getProcessSavedData` (`GET /v2/admin/workflow/api/company/{companyId}/processes/{processId}`), `getKycCompanyWorkflows` (`/v2/workflow/api/company-workflows/...`), SleekSign under `/v2/admin/workflow/api/sleeksign/...`, shared with legacy admin workflow surfaces. **Upstream**: opening the task page from the Camunda workflow list or other deep links (`marketing/admin-sleek-workflow/open-workflow-task-detail.md`). **Related**: legacy WFE “new workflow” task shell (`marketing/admin-new-workflow-workflow-task/run-admin-workflow-processes.md`) uses different URLs and `flow_class`; this feature is the Camunda (`sleek-workflow`) stack. |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Full backend persistence and Camunda deployment topology are not visible from these client modules alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Shell & routing**: `src/views/admin/sleek-workflow/workflow-task/index.js` — `WorkFlowList` mounts with `AdminLayout` (`sidebarActiveMenuItemKey="workflow-task"`, `isSleekWorkflow={true}`), reads `processId` / `processInstanceId` / `taskId` via `WORKFLOW_CONSTANTS` and `getQueryStringValue`. `initialize()` calls `getTaskList({ body: JSON.stringify({ businessKey, processInstanceId, withVariables: true }) })` from `@/views/admin/sleek-workflow/services/api-camunda`, then loads `getProcessSavedData` and `getTaskVariables` when `companyId` is present. `renderWorkflowName()` maps `processSavedData.workflow_type` to human-readable names (director changes, incorporations, accounting onboarding variants, KYC, deadlines, AGM/AR, HK/UK/SG flows, CDD, SBA, template, transfer, etc.). `renderBodyContent()` switches on `processVariables.workflowType` to the corresponding `*ProcessInstance` components (e.g. `KYCProcessInstance`, `SGIncorporationProcessInstance`, `AccountingOnboardingV2ProcessInstance`, `DeadlinesProcessInstance`, `AgmArProcessInstance`, `SGTransferProcessInstance`, `CustomerDueDiligenceProcessInstance`, …).
- **Task navigation & reload**: `reloadTasks`, `onTaskClick`, and `initialize` update the browser URL with `history.pushState` for `processId`, `processInstanceId`, and `taskId`; `reloadTaskVariables` uses `getTaskVariables({ taskId })`. `onItemSentToSleekSign` shows a dialog and opens the SleekSign document URL in a new window. `reloadSavedProcessData` re-fetches saved process data via `getProcessSavedData`.
- **KYC refresh path**: `perfromStartKYC` / `updateWorkflowURl` — when `fromKYCRefresh=true` and CMS `kyc_refresh` is enabled, may call `handleStartKyc` and `apiWfe.getKycCompanyWorkflows` to align the URL with the active KYC workflow instance. `initializeKycDrawerData` loads KYC company workflow tasks for rejected-task highlighting in the drawer.
- **Assignee lookup**: `initializeAssigneesLookup` (for deadlines, AGM/AR, UK incorporation) uses `api.getGroups` / `api.getAdminsByGroup` to build `assigneeGroups` / `assigneeOptions` / `assignedToFlatList`.
- **Camunda API client**: `src/views/admin/sleek-workflow/services/api-camunda.js` — `getTaskList`, `getTaskVariables`, `startProcess`, `updateProcessTask`, SleekSign create/send, `getSleekWorkflowProcesses`, `getSleekWorkflowProcessTasks`, `updateSection`, document fetch helpers, external task fetch/retry, `updateAssignee`, `updateProcessVariables`, `deleteProcesses`, `documentsRecirculate`, region-specific routes (e.g. UK/HK/SG), `sendRemindEmailForCddFormSubmission`, SBA helpers — all against `${getBaseUrl()}/v2/sleek-workflow/...` with `checkResponseIfAuthorized` on JSON responses.
- **WFE shared client**: `src/utils/api-wfe.js` — `getProcessSavedData`, `getKycCompanyWorkflows`, legacy `getWorkflowTasks` / `updateProcessTask` under `/v2/admin/workflow/api/...`, SleekSign and KYC-related admin endpoints used alongside Camunda routes for saved state and some cross-cutting workflow actions.
