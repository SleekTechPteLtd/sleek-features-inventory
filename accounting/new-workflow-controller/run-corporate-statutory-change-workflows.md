# Run corporate statutory change workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Run corporate statutory change workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (authenticated admin with `manage_workflows` policy: read for GET, edit for POST/PUT) |
| **Business Outcome** | Internal operators progress statutory corporate-secretarial filings and related tasks (address, directors, shareholders, company name, activities, FYE, extension of time, nominee director, new shareholders) with tasks assigned to company secretarial staff and orchestration delegated to the legacy Sleek workflow engine. |
| **Entry Point / Surface** | Sleek Back HTTP API under `/v2/admin/workflow` (`app-router.js`). Representative `POST` paths (all behind `userService.authMiddleware` + `accessControlService.can("manage_workflows", …)`): start flows — `/api/tasks/change-of-address/start`, `/api/tasks/changeoffinancialyearend/start`, `/api/tasks/resignationofdirector/start`, `/api/tasks/appointmentofdirector/start`, `/api/tasks/applicationofextensionoftime/start`, `/api/tasks/changeofdirector/start`, `/api/tasks/appointmentofnomineedirector/start`, `/api/tasks/changeofofficersparticulars/start`, `/api/tasks/changeofshareholdersparticulars/start`, `/api/tasks/changeofcompanyname/start`, `/api/tasks/changeofbizact/start`, `/api/tasks/additionofnewshareholder/start`; task steps — `/api/tasks/<process>/<processId>/<taskName>/<taskId>` (and `additionofnewshareholder/save-details`, `save-shares`); `GET` `/api/processes/applicationofextensionoftime/:processId` for process payload. |
| **Short Description** | Handlers start WFE processes via `config.sleekWfeBaseUrl` (`/workflow/api/tasks/.../start/` and task completion POSTs), auto-assign non-system tasks to the company’s `cs-in-charge` (or `css-in-charge` for addition of shareholder) using `ResourceAllocationRole` + `CompanyResourceUser`, send operational emails through store-commands, persist draft workflow data on **`CompanyWorkflow`** (`doUpdateProcessSavedData` where used), and run side effects (e.g. update registered address from change-of-address proof step). |
| **Variants / Markets** | SG (ACRA-, board-resolution-, and register-oriented task names across handlers) |
| **Dependencies / Related Flows** | **Sleek WFE** (`sleekWfeBaseUrl`) for process lifecycle; **`store-commands/workflow/*`** for emails and rejection/completion paths; **`allStoreCommands`** (`getTasksCommand`, `assignTaskCommand`) for task assignment; sibling **Camunda / v2 sleek-workflow** flows in `controllers-v2/camunda-workflow.js` cover overlapping director/share topics with a different engine—see inventory `accounting/camunda-workflow/run-director-and-share-structure-changes.md`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows` (process saved data via `doUpdateProcessSavedData` / reads in change-of-address); `companyresourceusers`, `resourceallocationroles` (resolve `cs-in-charge` / `css-in-charge`); `companies` (e.g. registered address update in change-of-address) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-SG tenants still route these WFE process names; overlap vs Camunda flows for the same business intent is not fully disambiguated in-repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/new-workflow-controller.js`

- Builds routes with `buildAuthenticatedGetRoute` / `Post` / `Put`: `userService.authMiddleware`, `accessControlService.can("manage_workflows", "read"|"edit")`.
- Imports and mounts statutory workflow handlers: `change-of-address`, `resignation-of-director`, `appointment-of-director`, `application-of-extension-of-time`, `change-of-director`, `change-of-fye`, `appointment-of-sleek-nd`, `change-of-officers-particulars`, `change-of-shareholders-particulars`, `change-of-company-name`, `change-of-biz-act`, `addition-of-new-shareholder` (lines 22–33, 89–158).

### `controllers-v2/handlers/workflow/change-of-address.js`

- `PROCESS_NAME`: `changeofaddress`; `postResource` to `${sleekWfeBaseUrl}/workflow/api/tasks/changeofaddress/...`; `CompanyWorkflow.findOne`, `Company.findById`, `updateCompanyRegisteredAddress`, `sendProofToCustomer`; `autoAssignProcessAndTask` → `ResourceAllocationRole` `cs-in-charge`, `CompanyResourceUser`, `allStoreCommands.assignTaskCommand`.

### `controllers-v2/handlers/workflow/resignation-of-director.js`

- `PROCESS_NAME`: `resignationofdirector`; WFE start + task mapping (`validate_resignation_of_director`, `acra_resignation_of_director`, etc.); rejection/completion via `startRejectedProcess`, `sendCompletionOfResignation`.

### `controllers-v2/handlers/workflow/appointment-of-director.js`

- `PROCESS_NAME`: `appointmentofnewdirector`; WFE start; `taskAction` maps tasks including `kyc`, `corpsec_validation`, `notice_by_nominee_director`; `appointmentOfDirectorStoreCommands` for emails and completion.

### `controllers-v2/handlers/workflow/application-of-extension-of-time.js`

- `PROCESS_NAME`: `applicationofextensionoftime`; `getProcess` GETs WFE process; `start` calls `doUpdateProcessSavedData` with `company_workflow_data`; task flow includes `validation_application_of_eot`, `acra`, `proof_of_request_submission`.

### `controllers-v2/handlers/workflow/change-of-director.js`

- `PROCESS_NAME`: `changeofdirector`; passes `director_type`, resigning/appointed company user IDs; tasks include `kyc_overview`, `form_45`, `acra`, `directors_information`; `changeOfDirectorStoreCommands` for completion and rejection.

### `controllers-v2/handlers/workflow/change-of-fye.js`

- `PROCESS_NAME`: `changeoffinancialyearend`; `changeOfFyeStoreCommands` for client/admin emails and task progression.

### `controllers-v2/handlers/workflow/appointment-of-sleek-nd.js`

- `PROCESS_NAME`: `appointmentofnomineedirector`; `appointmentOfSleekNdStoreCommands` with `isNomineeDirector: true`.

### `controllers-v2/handlers/workflow/change-of-officers-particulars.js` & `change-of-shareholders-particulars.js`

- `PROCESS_NAME`: `changeofofficersparticulars` / `changeofshareholdersparticulars`; `doUpdateProcessSavedData`; shared store-command module for initial emails with `type`: `OFFICERS` vs `SHAREHOLDERS`.

### `controllers-v2/handlers/workflow/change-of-company-name.js`, `change-of-biz-act.js`

- `PROCESS_NAME`: `changeofcompanyname`, `changeofbizact`; `doUpdateProcessSavedData` + respective store-command email flows.

### `controllers-v2/handlers/workflow/addition-of-new-shareholder.js`

- `PROCESS_NAME`: `additionofnewshareholder`; `autoAssignProcessAndTask` uses `css-in-charge`; `addNewShareholderCommand.saveShareholderDetails` / `saveShareholderShares`; `doUpdateProcessSavedData` on start.

### `store-commands/workflow/common/workflow-processes.js`

- `doUpdateProcessSavedData` reads/writes **`CompanyWorkflow`** by `company` + `workflow_process_id` or `business_key`.

### `app-router.js`

- `router.use("/v2/admin/workflow", require("./controllers/admin/new-workflow-controller.js"))`.
