# Run KYC verification workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Run KYC verification workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin (users with `manage_workflows` read/edit on admin workflow APIs) |
| **Business Outcome** | Lets staff start and progress per–company-user KYC: collect and approve documents, run AML checks and escalations, record compliance-related audit events, and remind customers or corporate shareholders to submit materials. |
| **Entry Point / Surface** | Sleek Admin workflow tooling (`/admin/new-workflow/…` links in notifications); authenticated admin API routes under `/api/tasks/kyc/…` and related process endpoints mounted from `new-workflow-controller`. |
| **Short Description** | Starts the KYC process via the external workflow engine, auto-assigns tasks to the company’s `kyc-in-charge` resource role where configured, persists workflow data on `CompanyWorkflow`, drives document approval posts and AML decision posts back to WFE, fires customer upload/reminder emails via store commands, and writes structured audit lines to the auditor service for key KYC actions. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek WFE (`sleekWfeBaseUrl` — start, task updates, verification detail, AML endpoints); mailer/partner domains for customer and secretary notifications; `sleek-auditor` HTTP API for audit logs; `doUpdateProcessSavedData` / `CompanyWorkflow`; broader Camunda/KYC compliance flows elsewhere in `sleek-back` |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `company-workflows`, `companies`, `company-users`, `company-resource-users`, `resource-allocation-roles` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `getKycCompanyWorkflows` (exported from `kyc.js` but not registered on this router) is exposed on another route; exact market-specific KYC rules not fully visible in these two files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Router (`controllers/admin/new-workflow-controller.js`)

- **Guards:** `userService.authMiddleware` plus `accessControlService.can("manage_workflows", "read")` or `"edit"` depending on method.
- **KYC routes:**
  - `POST /api/tasks/kyc/start` → `kyc.startKyc`
  - `GET /api/tasks/kyc/:processId/verification-process/:taskId/detail` → `kyc.verificationProcess`
  - `POST /api/tasks/kyc/:processId/:taskName/:taskId` → `kyc.kycTaskDocuments`
  - `POST /api/tasks/kyc/customer-document-upload` → `kyc.updateCustomerDocumentUploadStatus`
  - `POST /api/tasks/kyc/logs` → `kyc.kycRecordAuditLogs`
  - `POST /api/tasks/kyc/admin/send-customer-reminder` → `kyc.sendCustomerReminder`
  - `POST /api/tasks/kyc/aml-check` → `kyc.amlCheck`
  - `POST /api/tasks/kyc/aml-escalation` → `kyc.amlEscalation`
  - `POST /api/tasks/kyc/admin/send-corporate-shareholder-reminder` → `kyc.sendCorporateShareholderReminder`
- **Related process read:** `GET /api/processes/:workflowInstanceId/company-user/:companyUserId/kyc` → `getKycProcessSavedData` from `controllers-v2/handlers/workflow/all.js` (loads KYC-aligned `CompanyWorkflow` rows via `retrieveKycProcessSavedData` in `store-commands/workflow/common/workflow-processes.js`).

### Handlers (`controllers-v2/handlers/workflow/kyc.js`)

- **Start:** `startKyc` → `POST ${sleekWfeBaseUrl}/workflow/api/tasks/kyc/start/`, then `startKycSideEffect`: `autoAssignProcessAndTask` (queries `ResourceAllocationRole` type `kyc-in-charge`, `CompanyResourceUser`, uses `allStoreCommands.getTasksCommand` / `assignTaskCommand`), `doUpdateProcessSavedData`, `sendCustomerDocumentInitialised.send`.
- **WFE delegation:** `verificationProcess` (GET verification detail), `kycTaskDocuments` (document-type approval flags), `amlCheck`, `amlEscalation` — all call `${sleekWfeBaseUrl}/workflow/api/tasks/kyc/...`.
- **Customer upload status:** `updateCustomerDocumentUploadStatus` → `sendCustomerDocumentUploadStatus.send` (async notify path).
- **Reminders:** `sendCustomerReminder` → `sendKYCAdminManualRemind.send`; `sendCorporateShareholderReminder` → `sendKYCCorporateShareholderRemind.send`.
- **Audit:** `kycRecordAuditLogs` loads `Company` by `companyId`, builds comment via `buildAuditLog`, `auditorService.saveAuditLog` (external auditor service, not Mongo in this path).
- **Mongo imports used in this file:** `Company`, `CompanyResourceUser`, `ResourceAllocationRole`, `CompanyWorkflow`, `CompanyUser` (e.g. `getKycCompanyWorkflows` helper — not wired on this controller).

### Supporting implementation (not in feature line but called)

- `store-commands/workflow/common/workflow-processes.js` — `retrieveKycProcessSavedData` uses `CompanyWorkflow.find` with `data.request_information` filters.
- `store-commands/workflow/kyc/send-customer-document-initialised.js` (and related) — mailer templates, partner-aware customer links, secretary/admin notification URLs pointing at admin workflow UI.
