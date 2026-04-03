# Track company deadlines and compliance workflow

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Track company deadlines and compliance workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Internal staff can see a company’s compliance-related deadlines, Camunda-driven deadline and AGM/AR workflows, and the full set of company-linked workflows in one admin context so regulatory and operational work stays coordinated. |
| **Entry Point / Surface** | **Sleek Admin** → **Company overview** at `/admin/company-overview/?cid=<companyId>` — **Deadlines** side-nav tab (`Deadlines` / `deadlines.js` v2 when `new_deadlines` CMS is on). **Workflows** card/list on the overview **Company info** area via `GetWorkflowRelatedToCompany` (embedded from `company-info.js`). Deep links from deadline cards open **`/admin/sleek-workflow/workflow-task/`** in a new tab. |
| **Short Description** | The **Deadlines** view loads Camunda **deadlines** process instances (`getSleekWorkflowProcesses`, `workflow_type=deadlines`), merges **company workflow** saved data and **Camunda task** lists, and computes **Report**, **ACRA**, and **IRAS** deadline rows (internal vs regulatory dates, status, filing completion). It supports FYE selection across instances, starting the deadlines and **AGM & AR** Camunda processes, **resource allocation** defaults for assignees, dormancy and subscription context, and ACRA dates from the **Sleek Deadline service** plus legacy **`getAGMDeadlines`**. **`GetWorkflowRelatedToCompany`** lists workflows for the company (Camunda plus legacy when enabled), sorts by status, and routes staff to view or create flows (incorporation, transfer, SBA onboarding, KYC, etc.) including **`startProcess`** and **`api.createWorkflowInstance`**. |
| **Variants / Markets** | **SG** (ACRA/IRAS copy and tenant checks in workflow list — e.g. `sg`, `hk`, `gb` for incorp/transfer stubs); **HK**, **UK** paths in Camunda start handlers. Broader **SG, HK, UK, AU** where Sleek Admin is used; exact deadline tables are Singapore-oriented in labels (ACRA/IRAS). |
| **Dependencies / Related Flows** | **Camunda** (`api-camunda.js`): `getSleekWorkflowProcesses`, `getTaskList`, `getProcessTaskList`, `startProcess`, `getCompanyWorkflowById` — deadlines and AGM/AR process keys from `CAMUNDA_WORKFLOW_CONSTANTS`. **WFE** (`api-wfe.js`): `getProcessSavedData` → `GET /v2/admin/workflow/api/company/:companyId/processes/:processId`; `getCompanyWorkflows` → `GET /v2/admin/workflow/api/company/:companyId/company-workflows`. **Sleek API** (`api.js`): `getAGMDeadlines` → `GET /admin/companies/:id/get-agm-deadlines`; **`getCompanyDeadlines`** → deadline service `…/deadlines/company/:companyId`. **Config / features**: `getAuthenticatedAppFeature` default assignees, `setResourceAllocationValues` / `initializeDeadlineAssignees`, `camunda_workflow.deadlines` CMS flag. **Related**: company edit **Deadlines** (`marketing/admin-companies-edit-index` inventory), **workflow task** UI (`admin/sleek-workflow/workflow-task`). |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/deadlines.js`, `src/views/admin/company-overview/GetWorkflowRelatedToCompany.js`, `src/views/admin/company-overview/company-info.js` (embeds workflow list). **sleek-back**, **workflow engine**, **deadline microservice**, **Camunda** — REST behind the above paths (not defined in this repo). |
| **DB - Collections** | Unknown (no Mongo usage in these views; persistence is server-side). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `new_deadlines` is fully rolled out for all tenants; exact RBAC on company overview vs workflow start; full backend schema for deadline service vs company deadline records. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-overview/deadlines.js` (`Deadlines`)

- **Mount**: `fetchInitialDeadlineWfData` → `getDeadlinesProcessWorkflow` → `getCamundaDeadlineWorkflows` (`getSleekWorkflowProcesses` with `workflow_type=deadlines&backend_company_id=…`) + `apiWfe.getProcessSavedData` per process; attaches `getWorkflowTasks` / `getTaskList` per `businessKey`. Then `selectLatestWorkflow`, `computeDeadlines`, `fetchNonWorkflowDeadlines`, `finalizeDormancy`, `setResourceAllocationValues` / accounting services.
- **Deadline computation**: `DEADLINE_INCREMENTS` groups — **Report** (management accounts, unaudited FS, XBRL), **ACRA** (AGM, AR, extended AGM/AR from workflow or `getAGMDeadlines`), **IRAS** (ECI, Form C-S/C). Uses `getDeadline` / `getDeadlineAGMorARdate` with FYE from active Camunda company workflow or `formValueFinancialYear`; `getACRADeadlineFromDeadlineService` via **`api.getCompanyDeadlines(companyId)`**.
- **UI**: FYE dropdown (`MaterialSelect`), tables with regulatory due date, status (OVERDUE / DUE SOON / DONE), completion/filing column; override when **`activeAgmArWf`** exists for AGM/AR rows. Right panel: **About** (dormant), **Deadlines Workflow** card (Start now / VIEW / status chip), **AGM & AR Workflow** card, **Subscription** (accounting + corpsec services).
- **Actions**: `startWorkflow` → `startProcess` with `CAMUNDA_WORKFLOW_CONSTANTS.DEADLINES.PROCESS_INSTANCE_KEY`, `getProcessTaskList`, `initializeDeadlineAssignees`. `startAgmARWorkflow` → `CAMUNDA_WORKFLOW_CONSTANTS.AGM_AR.PROCESS_INSTANCE_KEY`. `redirectToWorkflow` → `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…`.

### `src/views/admin/company-overview/GetWorkflowRelatedToCompany.js`

- **Mount**: `getPlatformConfig`; **`apiWfe.getCompanyWorkflows({ companyId, includedWorkflows })`** — default `["camunda"]`, plus `new_workflow` / `old_workflow` when `workflow_list.enabled`. Adjusts HK **[PR] Incorporation** status for KYC RAF; conditionally appends **Incorporation**, **Transfer**, **SBA Onboarding** placeholder rows for eligible companies.
- **UI**: Renders cards per workflow with `processTitle` (e.g. AGM & AR FYE suffix), status badge, **view** / **create** / **start** → `redirectToWorkflow`: may call `handleStartIncorpCamundaWorkflow`, `handleStartTransferCamundaWorkflow`, `handleStartSBAOnboardingWorkflow`, `handleStartWorkflow` (`api.createWorkflowInstance`), then `window.open` URL and refresh. Share-allocation guard dialog for certain Camunda incorp flows.
- **Sorting**: `sortWorkflowsByStatus` — NOT STARTED → … → DONE / CANCELED.
