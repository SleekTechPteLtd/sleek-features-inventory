# Operate Camunda workflow processes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Operate Camunda workflow processes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated company users, Operations User, Sleek Admin (staff); system callers via the same HTTP surface where applicable |
| **Business Outcome** | Staff and clients can list and inspect Camunda-backed company workflows, move work forward by assigning tasks and updating variables, audit activity history, recover external-task failures, and discover which companies match workflow criteria—keeping incorporation, compliance, and operational flows visible and actionable. |
| **Entry Point / Surface** | Sleek Back HTTP API under `/v2/sleek-workflow` (router mounted in `app-router.js`); GET routes for process/task discovery use `userService.authMiddleware` plus `getWorkflowMiddleware()` for company association checks. Representative paths: `GET /processes`, `GET /processes/count`, `GET|POST /processes/tasks`, `GET /tasks/:taskId/variables`, `POST /processes/:rootProcessInstanceId/variables`, `POST /task/assignee`, `POST /variable-instance`, `GET /activity-instance`, `POST /getProcessTaskList`, `GET /company-workflows/:companyWorkflowId`, `POST /processes/delete`, `GET /workflow-finder`, `POST /external-task`, `PUT /external-task/retries`, `GET /external-task/:workerId/:topicName`, `GET /user`. |
| **Short Description** | Proxies process, task, variable, activity-history, and external-task operations to the Camunda Pilot service (`config.sleekCamundaPilotBaseApiUrl`), enriches responses with Mongo data (company workflows, users, company names), and on bulk process deletion updates `CompanyWorkflow` status, may close Zendesk tickets, and clears company remediation links when relevant. Workflow discovery aggregates `CompanyWorkflow` with `companies`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | External **Camunda Pilot** REST API; MongoDB via `CompanyWorkflow`, `Company`, `CompanyUser`; Zendesk ticket closure for CDD/KYC on process deletion (`zendesk-ticket-service`); tenant workflow constants (`config/shared-data.json`); access control for admin-only routes elsewhere in the same router (not these handlers). Downstream UIs and automations that consume `/v2/sleek-workflow` APIs. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows`, `companies`, `companyusers` (and reads that join company name onto task variables) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether every POST body is validated for company scope when `getWorkflowMiddleware` is not applied (GET routes use it; many POST routes use auth only). Exact product surface (internal admin vs client app) per endpoint is not named in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/camunda-workflow.js`

- Registers authenticated routes; **`buildAuthenticatedGetRoute`** wraps `userService.authMiddleware`, **`getWorkflowMiddleware()`**, then handler—used for listing/inspecting processes, tasks, variables, history, workflow finder, external-task fetch by worker, Camunda user lookup, and company workflow by id.
- **`buildAuthenticatedPostRoute` / Put** use **`userService.authMiddleware`** only (no workflow middleware on these lines)—handlers include `updateProcessVariables`, `updateAssignee`, `getProcessTasks` (POST), `getVariableInstance`, `getProcessTaskList`, external-task POST/PUT, `deleteProcessInstances`.
- Maps URL paths above to handlers imported from `./handlers/camunda-workflow/all` (see exports used at lines 4–21).

### `controllers-v2/handlers/camunda-workflow/all.js`

- **`getAllProcess` / `getAllProcessRequest`**: `GET` Camunda Pilot `/camunda/processes/` and `/camunda/processes/count/` with query filters (`company_id`, status, workflow type, dates, ordering, financial year); adjusts display state for active processes with zero finished tasks using `/camunda/processes/tasks/count`; loads **`CompanyWorkflow`** by `business_key` and enriches with price/nominee flags and KYC **`CompanyUser`** when needed.
- **`getCamundaWorkflowProcesses`**: Mongo **`CompanyWorkflow.aggregate`** with `$lookup` into **`companies`**, optional filters (`workflowType`, `workflowTask`, `queryName` e.g. `active_biz_profile`).
- **`getProcessTasks` / `getProcessTasksRequest`**: Camunda Pilot `/camunda/processes/tasks` with process/business key and variables; enriches task variables with **`Company.findById`** for `company_name`.
- **`getTaskVariables`**: `/camunda/tasks/:taskId/variables`.
- **`getExternalTaskByProcessInstanceId`**: POST `/camunda/external-task` with `processInstanceId`.
- **`retryExternalTaskByExternalId`**: PUT `/camunda/external-task/:externalTaskId/retries` with `retries` body.
- **`getExternalTaskByAssignedWorker`**: GET `/camunda/external-task/:workerId/:topicName`.
- **`updateAssignee` / `updateTaskAssignee`**: POST `/camunda/task/assignee`.
- **`updateProcessVariables` / `updateProcessVariablesAPI`**: POST `/camunda/processes/:rootProcessInstanceId/variables`.
- **`getVariableInstance`**: POST `/camunda/variable-instance` with `processInstanceId` from body.
- **`getHistoryActivityInstance` / `getAllActivityInstance`**: GET `/camunda/activity-instance` with pagination and `processInstanceId`.
- **`getUser`**: GET `/camunda/user` with forwarded query string.
- **`getProcessTaskList`**: POST `/camunda/getProcessTaskList` with optional `businessKey`.
- **`deleteProcessInstances`**: POST `/camunda/processes/delete` with `deleteReason`, `processInstanceIds`, etc.; then **`CompanyWorkflow.find`** by `data.processInstanceId`, sets **`workflow_status`** to **`WorkflowStatus.CANCELLED`**, appends **`workflow_status_event_history`**, **`closeCDDWorkflowZendeskTicket`** / **`closeKYCRefreshZendeskTicket`** by workflow type, may **`$unset`** `cdd_remediation_workflow` on **`Company`** when applicable.
- **`getCompanyWorkflowById`**: **`CompanyWorkflow.findById`** for `companyWorkflowId` path param.
- Shared HTTP helpers: **`getResource`**, **`postResource`**, **`putResource`** from `../../utlities/request-helper-camunda-pilot`.

### `controllers-v2/utlities/workflow-middleware.js`

- **`getWorkflowMiddleware`**: After auth, allows **Sleek Admin**; otherwise loads **`CompanyUser`** for `req.user`, builds allowed company id list, requires **`backend_company_id`** (query), **`companyId`** (params), or **`company_id`** (body) to match a user company—otherwise **401**. Used on GET routes in `camunda-workflow.js` to scope general process/task reads to the caller’s company context.
- Exports **`workflowMiddleware`** (role- and URL-based checks for named workflow segments)—not wired in `camunda-workflow.js` for the generic routes in this feature line; listed for context on how workflow authorization is modeled in-repo.

### `app-router.js`

- `router.use("/v2/sleek-workflow", require("./controllers-v2/camunda-workflow"))` — base path for all routes above.
