# Run admin workflow processes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Run admin workflow processes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets internal operations staff execute engine-assigned workflow tasks for a company process (KYC, corporate secretarial changes, bank and accounting onboarding, and related flows) using persisted process data, document handling, and SleekSign where applicable. |
| **Entry Point / Surface** | Sleek Admin > New Workflow — open a process (e.g. from workflow list or My Tasks) to `/admin/new-workflow/workflow-task/?processId=…` (optional `taskId`, `isTask` / view-only flags); breadcrumbs show “Workflow list” → “{workflow title} details”. |
| **Short Description** | Loads tasks and saved process state from the WFE admin API, renders the correct flow component from `process.flow_class` (KYC, change of address, director/shareholder changes, bank account opening, accounting onboarding, SleekSign handoffs, etc.), and supports task switching via the sidebar drawer, reload after document upload, and optional KYC UI v2 via CMS feature flags. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Backend: Sleek API `/v2/admin/workflow/api/tasks`, `/v2/admin/workflow/api/company/{companyId}/processes/{processId}` (saved data), task-type-specific POST/PUT under `/v2/admin/workflow/api/tasks/...`, SleekSign (`/v2/admin/workflow/api/sleeksign/...`, `/v2/sleek-sign/api/...`). Upstream entry from `new-workflow` tables, `my-tasks`, company edit, incorporation/KYC surfaces that deep-link to this URL. Related inventory: admin-sleek-workflow (Camunda list vs this WFE “new workflow” stack). |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact market scope (SG vs multi-region) for each `flow_class` is not determined from these files alone; persistence model is server-side only here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Shell & routing**: `src/views/admin/new-workflow/workflow-task/index.js` — `WorkFlowList` mounts under `#root` with `AdminLayout` (`sidebarActiveMenuItemKey="workflow-task"`), reads `processId` / `taskId` / task-view-only from query (`WORKFLOW_CONSTANTS`), calls `getWorkflowTasks({ query: process_id=… })` and `getProcessSavedData({ companyId, processId })`, derives `flow_class` from `tasks[0].process.flow_class` and switches to flow components (KYC, change of address, resignation/appointment of director, extension of time, change of director, nominee director, officers/shareholders particulars, FYE, company name, business activity, bank account opening, accounting onboarding, addition of shareholder). `reloadTasks` re-fetches tasks and updates URL to latest task. `onItemSentToSleekSign` opens confirmation dialog then `window.open` on returned URL.
- **KYC branch**: `src/views/admin/new-workflow/workflow-task/flows/kyc-flow.js` — dispatches by `task.flow_task` to NRIC/FIN/passport/proof of residence, AML check/escalation, customer acceptance form, corporate shareholder supporting docs, risk assessment, or default `DocumentUpload`; toggles v1 vs v2 task components from CMS `new_workflow_view` → `kyc_ui.enabled` and gates edits with `user.permissions.perform_kyc === "full"`. Records audit via `kycRecordAuditLog` on view when `companyId` present.
- **WFE HTTP client**: `src/utils/api-wfe.js` — `getWorkflowTasks`, `getProcessSavedData` / `updateProcessSavedData`, KYC helpers (`startKyc`, `kycTaskDocuments`, `documentValidation`, `amlCheck`, `amlEscalation`, …), accounting onboarding and addition-of-shareholder endpoints, generic `updateProcessTask` / `resetProcessTask`, SleekSign `createSleekSignDocument` / `sendToSleekSign`, questionnaires, `getCompanyWorkflows`, etc., all targeting `${getBaseUrl()}/v2/admin/workflow/api/...` (and shared Sleek Sign routes).
- **Admin chrome & access**: `src/layouts/new-admin.js` — requires `user.profile === "admin"`; `checkUserAccess` redirects to `/admin/` when the sidebar’s resource permission is missing; for default (non–sleek-workflow) task pages renders `TaskDrawer` from `views/admin/new-workflow/components/drawer` with `tasks`, `processSavedData`, `onTaskClick`, `onAdminDashboardClick`.
