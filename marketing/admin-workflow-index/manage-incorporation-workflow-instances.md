# Manage incorporation workflow instances

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage incorporation workflow instances |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin |
| **Business Outcome** | Lets operations staff open a legacy workflow instance for client incorporation and related onboarding, move through sectioned tasks, complete or force-validate steps, and advance the case without using the Camunda “sleek-workflow” or WFE `new-workflow` task shells. |
| **Entry Point / Surface** | Sleek Admin — workflow instance viewer at a page that mounts `WorkflowInstanceViewer` (e.g. incorporation/transfer workflow entry; layout uses `sidebarActiveMenuItemKey="incorp-transfer-workflow"`). URL query: `?instanceId={workflowInstanceId}` and optional `taskId={workflowTaskId}`; sidebar links and navigation update `history.pushState` with the same query shape. |
| **Short Description** | Loads workflow instance metadata and tasks via admin workflow APIs, hydrates optional WFE process metadata (`getProcessSavedDataByWorkflowInstanceId`, `getWorkflowProcesses`), renders a sectioned sidebar (presentation sections and tasks with completion icons), and embeds `TaskViewer` to dispatch by task `type` into incorporation-specific containers (KYC overview, user validation, ACRA name and incorporation steps, SleekSign send/signature, share checks, post-incorporation, etc.). Supports completing tasks (`completeWorkflowTask`), advancing to next/previous available tasks, optional **Force Validate** for users with `manage_workflows` full (with exceptions for named tasks), and KYC-overview completion side effects (customer acceptance form generation). |
| **Variants / Markets** | SG (ACRA- and SleekSign-oriented task types dominate); other markets not confirmed from these modules alone. |
| **Dependencies / Related Flows** | **HTTP (Sleek API)**: `GET /admin/workflow-instances/{id}/get-data`, `GET /admin/workflow-tasks/{id}/get-data`, `POST /admin/workflow-tasks/{id}/complete-task`, `PUT /admin/workflow-tasks/{id}/force-validate`, `POST /admin/companies/{companyId}/generate-customer-acceptance-form` (KYC overview path). **WFE**: `GET /v2/admin/workflow/api/processes/{workflowInstanceId}`, `GET /v2/admin/workflow/api/processes` (lookup by `process_id`). Shared file/company helpers via `api` (`getAllFiles`, `findFolder`, etc.) from task subtrees. **Related inventory**: Camunda-backed admin (`admin-sleek-workflow-workflow-task`), WFE class-based `new-workflow` shell (`admin-new-workflow-workflow-task`) — different URLs and APIs; this feature is the **presentation-driven workflow instance** stack under `views/admin/workflow`. |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact marketing route or menu path that lands on this viewer is not defined in these three files; whether non-SG incorporation variants reuse the same task map is not determined here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Entry shell**: `src/views/admin/workflow/index.js` — mounts `WorkflowInstanceViewer` under `#root` and loads `admin/workflow/index.scss`.
- **Instance shell & data**: `src/views/admin/workflow/workflow-instance-viewer.js` — `fetchBodyData` reads `instanceId` / `taskId` from the query string; `api.getWorkflowInstance`, `api.getWorkflowTask` (default first task if no `taskId`), `api.getUser`; `getWorkflowProcess` loads WFE saved process row and `apiWfe.getWorkflowProcesses` for `process_id`; sidebar from `instance.presentation.sections` with task links, disabled styling for `unavailable`, tick for `completed`; `handleForceValidate` → `api.forceValidateWorkflowTask`; passes `instance`, `task`, `user`, `process`, `lastTaskId`, and refresh handlers into `TaskViewer`.
- **Task routing & completion**: `src/views/admin/workflow/task-viewer.js` — `taskViews` maps `type` strings (e.g. `user-validation`, `kyc-overview`, `check-acra-name`, `acra-incorporation`, `send-to-sleeksign`, `signature-status`, …) to incorporation container components under `incorporation/container/tasks/`; `handleCompleteStep` → `api.completeWorkflowTask` with JSON body; auto-advance via `handleChangeTask` / `getNextTaskId` unless skipped or types that suppress auto-next; KYC overview all-users triggers `api.generateCompanyCustomerAcceptanceForm` when appropriate; `TaskHeader` for prev/next navigation.
- **API clients**: `src/utils/api.js` — `getWorkflowInstance`, `getWorkflowTask`, `completeWorkflowTask`, `forceValidateWorkflowTask`, `generateCompanyCustomerAcceptanceForm` (paths as in master sheet). `src/utils/api-wfe.js` — `getProcessSavedDataByWorkflowInstanceId`, `getWorkflowProcesses`.
- **Shared task utilities**: `src/views/admin/workflow/utility.js` — file preview/download, folder helpers, form helpers used by incorporation task UIs (not exclusive to this feature but supporting evidence).
