# Manage workflow processes and tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage workflow processes and tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin staff with `manage_workflows` read/edit) |
| **Business Outcome** | Internal operators can list, filter, and drill into client workflow processes and tasks, assign work, persist and adjust saved process data and forced status, reset tasks, and see aggregated company workflow overviews alongside name-check evidence—so client workflows stay serviced consistently across the ViewFlow/WFE-backed pipeline. |
| **Entry Point / Surface** | Sleek Admin App > Workflows — HTTP API mounted at `/v2/admin/workflow` (`app-router.js`). Representative routes: `GET /api/processes`, `GET /api/tasks`, `GET /api/all-tasks`, `GET /api/flows/`, `GET /api/processes/:processName/:processId`, `GET|PUT /api/company/:companyId/processes/:processId`, `PUT /api/processes/:processId/change-status`, `POST /api/tasks/.../assign`, `POST /api/tasks/.../reset-task`, `GET /api/company/:companyId/company-workflows`, `GET /api/get-name-check/:companyId/:userId`. |
| **Short Description** | Authenticated admin routes delegate process listing, task listing, flow discovery, assignment, and task reset to the Sleek Workflow Engine (WFE) HTTP API; persisted per-process form/state lives in MongoDB `CompanyWorkflow` (and related) via `workflow-processes` store commands. Updates to saved data can sync risk assessment reports and auditor logs; forced status changes can update linked bank-account progress. Company workflow overview merges Camunda, legacy CS, and new WFE ViewFlow slices by query. Name-check results for a company user are read from `NameCheckResult` with file population. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek WFE** (`config.sleekWfeBaseUrl`) — `/workflow/api/processes`, `/workflow/api/tasks`, `/workflow/api/flows`, assign and reset endpoints; **ViewFlow** aggregation via `getViewFlowWorkflow` + `getProcessesService` when `company-workflows` includes `new_workflow`; **Camunda** / **old_workflow** CS paths when requested on same overview endpoint. **Company risk rating** service on RAF-related saved-data updates. **Auditor** (legacy + v2) for audit lines on edits and share-info/name-reservation completion. **Sleek auditor** modules. **Tenant** `sharedData.workflows` and `general.new_workflow_view` for filtering and list behaviour. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows`, `pendingcompanyworkflows` (read), `namecheckresults`, `files` (populate on name check), `riskassessmentreports` (conditional update), `companyopenbankaccounts` (conditional update on force status), `companies`, `companyusers` (reads / populate) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact product labels for “company workflows” filters (`camunda`, `old_workflow`, `new_workflow`) in the admin UI; whether all markets expose the same flow list (`sharedData.workflows` + tenant flags). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/new-workflow-controller.js`

- Router builds **`buildAuthenticatedGetRoute`** / **`Post`** / **`Put`** with **`userService.authMiddleware`** and **`accessControlService.can("manage_workflows", "read")`** (GET) or **`"edit"`** (POST/PUT).
- Imports **`getProcesses`**, **`getTasks`**, **`getAllTasks`**, **`getAllFlows`**, **`assignTask`**, **`getProcessDetails`**, **`getProcessSavedData`**, **`getProcessSavedDataByWorkflowInstanceId`**, **`getKycProcessSavedData`**, **`updateProcessSavedData`**, **`updateProcessStatusForce`**, **`resetProcessTask`**, **`getCompanyWorkflows`** from **`controllers-v2/handlers/workflow/all`**; **`getNameCheck`** from **`name-check`**.
- Maps paths listed in the Entry Point row to those handlers (plus many workflow-specific task routers for KYC, accounting onboarding, change-of-address, etc. — this feature line focuses on the shared process/task/saved-data/name-check/company-overview surface).

### `controllers-v2/handlers/workflow/all.js`

- **`getProcessesService` / `getProcesses`**: **`getResource`** to WFE **`${sleekWfeBaseUrl}/workflow/api/processes/`** with query params (pagination, `backend_user_id`, `backend_company_id`, `status`, `ordering`, `flow_class`, `process_id`, `multi_flow_class`, `multi_flow_task`, date filters, `assigned_to` when tenant **`new_workflow_view`** is on). Optionally enriches each process with tasks from **`/workflow/api/tasks/?process_id=`** and, in new view, **`CompanyUser.findById`** for `company_user_obj`.
- **`getTasks`**: **`allStoreCommands.getTasksCommand`** → WFE tasks by `process_id` (see **`store-commands/workflow/common/all.js`**).
- **`getAllTasks`**: **`GET`** WFE **`/workflow/api/tasks/`** with filters.
- **`getAllFlows`**: **`GET`** WFE **`/workflow/api/flows/`**, then filters out test titles and non-allowed **`sharedData.workflows`** flow classes; may hide accounting onboarding flow per tenant flag.
- **`assignTask`**: **`assignTaskCommand`** → WFE **`.../tasks/{taskType}/{processId}/{taskName}/{taskId}/assign/`**.
- **`getProcessDetails`**: **`GET`** WFE **`/workflow/api/processes/:processName/:processId/`**.
- **`getProcessSavedData`**, **`getProcessSavedDataByWorkflowInstanceId`**, **`getKycProcessSavedData`**: **`retrieve*`** helpers from **`store-commands/workflow/common/workflow-processes.js`**.
- **`updateProcessSavedData`**: **`doUpdateProcessSavedData`**; may **`RiskAssessmentReport.updateOne`**, **`companyRiskRatingService.updateCompanyRiskRating`** for RAF-related paths; **`auditorService.saveAuditLog`** / **`saveAuditLogV2`** for optional `logUpdate` and share-info / name-reservation completion.
- **`updateProcessStatusForce`**: **`allStoreCommands.doUpdateProcessStatusForce`** (WFE **`PUT`** `.../api/processes/:processId/change-status/`); **`CompanyWorkflow.findOne`** by `workflow_process_id`; may **`CompanyOpenBankAccount.updateOne`**; auditor log for forced status.
- **`resetProcessTask`**: **`postResource`** to WFE **`/workflow/api/tasks/{processName}/{processId}/{taskName}/{taskId}/`** with body mapping approval flags.
- **`getCompanyWorkflows`**: **`Company.findById`**; builds parallel calls for **`getCamundaWorkflow`**, **`getCSWorkFlow`**, **`getViewFlowWorkflow(getProcessesService(...))`** based on **`req.query.workflow`** array; **`compact`** merge of results.

### `controllers-v2/handlers/workflow/name-check.js`

- **`getNameCheck`**: **`NameCheckResult.find({ company, user })`**, **`File.populate`** with **`NAME_CHECK_FILE_FILES.FILE_REPORT`**.

### `store-commands/workflow/common/workflow-processes.js`

- **`retrieveProcessSavedData`**: **`CompanyWorkflow.findOne`** by company + `business_key` or `workflow_process_id` (from **`buildQueryPayload`** / **`lookForBusinessKey`**); creates document if missing.
- **`retrieveProcessSavedDataByWorkflowInstanceId`**: **`CompanyWorkflow.find`** by **`data.request_information.cs_workflow_instance`**.
- **`retrieveKycProcessSavedData`**: **`CompanyWorkflow.find`** by **`requested_for_companyuser_id`** and optional **`cs_workflow_instance`**.
- **`doUpdateProcessSavedData`**: **`CompanyWorkflow.findOne`**, merge or replace **`data`**, **`save`**.

### `store-commands/workflow/common/all.js`

- **`getTasksCommand`**, **`assignTaskCommand`**, **`doUpdateProcessStatusForce`** — HTTP to WFE endpoints as summarized above.

### `app-router.js`

- **`router.use("/v2/admin/workflow", require("./controllers/admin/new-workflow-controller.js"))`** — base path for admin workflow API.
