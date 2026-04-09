# Process Camunda automation integrations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process Camunda automation integrations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (Camunda pilot / workflow callbacks); authenticated users for workflow email actions (`sendWorkflowEmails` uses `userService.authMiddleware`). Pilot callback routes use `camundaPilotMiddleware`: in `development` requests pass without auth; otherwise `userService.authMiddleware` applies. |
| **Business Outcome** | Automated workflows can generate or recirculate incorporation documents, execute Camunda external-task side effects (incorporation steps, ERP setup, accounting tool updates, company go-live, receipt activation, transfer/onboarding emails, and more), push completion data to analytics via the Camunda pilot API, mark company workflows complete, and send templated workflow emails (e.g. HK NNC1 instructions) without manual glue at each engine step. |
| **Entry Point / Surface** | Sleek Back HTTP API under `/v2/sleek-workflow` (router in `app-router.js`). **POST** `/generate-documents`, `/data-streamer-update-on-end-process`, `/external-task-processor` with `camundaPilotMiddleware` then handler. **POST** `/send-workflow-emails` with `userService.authMiddleware` only (no `getWorkflowMiddleware` on this line). |
| **Short Description** | Four handlers back Camunda pilot automation: (1) trigger SG incorporation document generation or delegate recirculation; (2) resolve external-task `action` values to domain services (incorporation completion, share info, Xero transfer emails, accountant notifications, ERPNext initiate/monitor, accounting tool updates, company status live, receipt activation, etc.); (3) on process end, call Camunda pilot `getProcessTasksRequest` with `isDataAnalyticsEnabled: true` then set `CompanyWorkflow.workflow_status` to `COMPLETED`; (4) send workflow emails by `action` (e.g. `form-nnc1-send-email-instruction` for HK) via `mailerVendor`, updating `CompanyWorkflow.data` timestamps/history. |
| **Variants / Markets** | SG, HK (explicit in external-task actions and HK email constants); other markets may appear in shared incorporation/transfer flows — **Unknown** for full matrix |
| **Dependencies / Related Flows** | **Camunda Pilot** REST API (`config.sleekCamundaPilotBaseApiUrl`, `getProcessTasksRequest` → `/camunda/processes/tasks`); incorporation document analyzer/generator (`sg-incorporation/.../incorporation-document-generator`, `incorporation-document-analyzer-multitenant`); `sg-incorporation` handler; company secretaries and share-info services; accounting transfer/Xero email handlers; ERPNext handlers; `update-accounting-tool-camunda`; `company-service`; receipt system activation; **mailer** vendor; HK incorporation constants (`HK_INCORPORATION_WORKFLOW`). Related: broader `/v2/sleek-workflow` operations in `operate-camunda-workflow-processes.md`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows` (`CompanyWorkflow`: status on completion, `data` for email history); `companyusers` (directors/shareholders, owner for NNC1); `companies` (via populate in workflow emails). Additional collections touched indirectly through external-task branches (e.g. `companies` via `companyService.setToLiveViaCamunda`, receipt/ERP paths) — not exhaustively listed per action. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-dev callers of pilot middleware use a service user JWT or human session; `sendWorkflowEmails` uses HTTP **402** for validation/API errors (unusual vs 400). Whether `getProcessTasksRequest` side effects when `isDataAnalyticsEnabled` are fully defined server-side on Camunda pilot. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/camunda-workflow.js`

- **POST** `/generate-documents`: `camundaPilotMiddleware`, `handleDocumentGeneration` from `handlers/camunda-workflow/generate-document.js`.
- **POST** `/data-streamer-update-on-end-process`: `camundaPilotMiddleware`, `dataStreamerOnEndProcess` from `data-streamer.js`.
- **POST** `/external-task-processor`: `camundaPilotMiddleware`, `externalTaskProcessor` from `external-task-processor.js`.
- **POST** `/send-workflow-emails`: `buildAuthenticatedPostRoute` → `userService.authMiddleware`, `sendWorkflowEmails` from `workflow-emails.js`.
- Router mounted at **`/v2/sleek-workflow`** in `app-router.js`.

### `controllers-v2/handlers/camunda-workflow/generate-document.js`

- **`camundaPilotMiddleware`**: `NODE_ENV === "development"` → `next()`; else **`userService.authMiddleware`**.
- **`handleDocumentGeneration`**: Body `documentsToBeGenerated`, `companyId` (required); **`IncorporationDocumentGenerator.generateDocument(companyId, documentsToBeGenerated)`**; 200 / 400.
- Exports **`handleRecirculateDocuments`** (used on `/documents/recirculate` in same router file, not this feature’s file list but same module): **`recirculateDocuments`** from incorporation document generator.

### `controllers-v2/handlers/camunda-workflow/external-task-processor.js`

- **`externalTaskProcessor`**: Body `businessKey`, `companyId`, `processInstanceId`, `action` (all required); dispatches **`_processExternalTaskByAction`** switch including: `analyzeDocumentForSending` (name reservation); **`triggerIncorporationStepCompletion`** / **`updateOnRegistersCompleted`** (`./sg-incorporation`); **`autoAssignSleekSecretaries`**; **`autoCompleteShareInfo`** (SG/HK); **`executeSendTransferXeroToUsEmailFunc`**; **`triggerEmailAfterOnboardingForSG`**, **`triggerEmailAfterOnboardingForHK`**; **`initiateERP`** / **`monitorERP`** (`erpnextHandler`); **`updateAccountingTool`** (`../company/update-accounting-tool-camunda`); **`companyService.setToLiveViaCamunda`**; **`receiptActivationHandler.createIntialReceiptUser`** / **`receiptSystemActivation`**; default throws if `action` unknown. 200 / 400.

### `controllers-v2/handlers/camunda-workflow/data-streamer.js`

- **`dataStreamerOnEndProcess`**: Body `businessKey`, `companyId`, `processInstanceId`; **`getProcessTasksRequest`** from `./all` with `{ businessKey, isDataAnalyticsEnabled: true, processInstanceId }` (proxies to Camunda pilot **`/camunda/processes/tasks`** with analytics flag). **`finally`**: **`CompanyWorkflow.updateOne({ business_key }, { $set: { workflow_status: "COMPLETED" } })`** (errors logged, non-fatal). 200 / 400.

### `controllers-v2/handlers/camunda-workflow/all.js`

- **`getProcessTasksRequest`**: Builds query for **`${config.sleekCamundaPilotBaseApiUrl}/camunda/processes/tasks`**; supports `isDataAnalyticsEnabled`; enriches task variables with **`Company.findById`** for `company_name` when variables present.

### `controllers-v2/handlers/camunda-workflow/workflow-emails.js`

- **`sendWorkflowEmails`**: Body `company_id`, `action` required; uses **`req.user`** for logging and **`_updateTimestampSendingEmail`**; **`form-nnc1-send-email-instruction`** → **`sendNNC1EmailForInstruction`** (`CompanyWorkflow.findOne` + populate `company`, **`CompanyUser`** query directors/shareholders, **`calculateTotalIssuedShareCapital`**, **`mailerVendor.sendEmail`** with `HK_INCORPORATION_WORKFLOW` template tags / CC); updates **`CompanyWorkflow.data.${taskDefinitionKey}`** send history. Unknown actions skipped with log. 200 / 402 on errors.
