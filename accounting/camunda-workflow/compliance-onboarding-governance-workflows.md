# Compliance, onboarding, and governance workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Compliance, onboarding, and governance workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / company operator (forms and submissions); Operations User and Admin (task completion, bulk CDD, Corp Pass session coordination); Compliance (SBA application review and overrides) |
| **Business Outcome** | Lets clients and staff complete regulated onboarding and company lifecycle steps (identity, CDD, accounting setup, risk and SBA decisions, statutory deadlines) while keeping process state in Camunda and MongoDB. |
| **Entry Point / Surface** | Customer app and onboarding flows (KYC, CDD remediation, accounting questionnaire); Admin / operations tools for workflow tasks, bulk CDD, Corp Pass, and SBA decisions — backed by v2 Camunda workflow HTTP handlers (`sleek-back` Camunda pilot integration). |
| **Short Description** | Starts and advances multiple Camunda process types: per–company-user KYC (with refresh and auto-verify paths), company-level customer due diligence (including bulk upload and chasers), accounting onboarding (via shared questionnaire util), incorporation/transfer risk-assessment regeneration with SBA outcomes, standalone SBA onboarding RAF tasks, AGM/annual return and statutory deadline workflows, Corp Pass credential session markers, and admin APIs to inspect or override SBA application status after RAF. |
| **Variants / Markets** | SG (primary in evidence); HK (KYC post-completion behaviour); other markets Unknown |
| **Dependencies / Related Flows** | Sleek Camunda Pilot (`sleekCamundaPilotBaseApiUrl`); `camunda-workflow-service`, `kyc-refresh-service`, `cdd-refresh-chaser-service`, `company-risk-rating-service`, `business-account-service`, mailer, Zendesk tickets, `sleek-auditor-node`, incorporation RAF automation and `agm-ar` / deadlines linkage |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `company-workflows`, `companies`, `company-users`, `users`, `user-data-source-histories`, `bulk-cdd-upload-histories`, `bulk-cdd-upload-companies`, `risk-assessment-form-approvals`, `corp-pass-credentials` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### KYC (`kyc.js`)

- **Exports:** `start`, `taskAction`, `sectionAction`, `saveKycRejectionsToCamunda`, `sendMessageToCamunda`, `startKycRefresh`, `resendKYCRefreshEmail`, `getTaskRejections`, `initiateKYCForCamunda`, `handleAutoCompleteCamundaKYC`.
- **Camunda:** `POST` `${sleekCamundaPilotBaseApiUrl}/kyc/start?processType=kyc`, `POST` `/kyc/complete-task`, `PUT` `/camunda/processes/{processInstanceId}/variables/rejections`, `POST` `/camunda/send-message`.
- **MongoDB:** `CompanyWorkflow` (workflow_type KYC, sections, business_key), `CompanyUser` (kyc_status, kyc_workflow, kyc_refresh), `User`, `UserDataSourceHistory`, `Company`.
- **Integrations:** KYC refresh service, Zendesk (tickets / logs), risk RAF scoring on reset, incorporation name-reservation auto-trigger, document analyzer, workflow automation entrypoint `USER_KYC_COMPLETED`, auditor v2 on profile verified.

### Customer due diligence (`customer-due-diligence.js`)

- **Process key:** `customer-due-diligence`.
- **Camunda:** `POST` `/{customer-due-diligence}/start?processType=...`, complete-task via `complete-task-actions`.
- **Exports:** `start`, `taskAction`, `initiateWorkflow`, reminders and emails, **bulk CDD** (`bulkCddUpload`, `getBulkCddBatches`, `getBulkCddUploadByBatchId`, `getBulkCddOngoingUploads`, `retryBatchFailedItems`, `processBulkCddByBatchId`), `getCompaniesCddWorkflows`, CDD refresh chaser/resend.
- **MongoDB:** `CompanyWorkflow`, `Company` (`cdd_remediation_workflow`), `BulkCddUploadHistory`, `BulkCddUploadCompany`, `CompanyUser` (emails).
- **Other:** Access control for remind (`companies` edit), auditor, KYC refresh auto-trigger on initiate, company risk rating on RAF steps, duplicate company profile for remediation.

### Accounting onboarding (`accounting-onboarding.js`)

- **Exports:** `start`, `taskAction` (including Camunda `send-message` path).
- **Implementation:** Delegates start to `ACCOUNTING_QUESTIONNAIRE_UTILS.startCamundaWorkflowInstance` in `utils/accounting-questionnaire-util.js`, which builds payload (Xero, ecommerce, transfer, payroll, webinar, accounting tool type, staff emails) and calls Camunda `${sleekCamundaPilotBaseApiUrl}/{workflowType}/start?processType=...`.

### Risk assessment (`risk-assessment.js`)

- **Exports:** `regenerate` — runs `incorporationRafAutomation.generateAnswers`, then may call `approveSbaApplicationIfPossible` or reject SBA / send pre-onboarding rejection email via `sba-onboarding`.

### SBA onboarding (`sba-onboarding.js`)

- **Process key:** `sba-onboarding`.
- **Camunda:** start and complete-task for `sba_raf_pre_onboarding` / `sba_raf_post_onboarding`; automation entry `triggerAutomationSBARaf`.
- **MongoDB:** `CompanyWorkflow`, `Company`, `CompanyUser`, `RiskAssessmentFormApproval`.
- **Side effects:** Compliance email on create, risk rating updates, consent reminders, pre-onboarding rejection email, auditor logs.

### AGM and annual return (`agm-ar.js`)

- **Process key:** `agm-ar`.
- **Links:** Resolves deadline workflow via `getDeadlineWFBusinessKeyAndProcessInstanceByFYE`; stores `deadline_wf_*` on workflow; updates deadline workflow with `agm_ar_wf`.
- **Tasks:** `annual_general_meeting`, `annual_return` — assignee sync via `getProcessTasksRequest` / `updateTaskAssignee`.

### Statutory deadlines (`deadlines.js`)

- **Workflow type:** `DEADLINES` from tenant constants.
- **Camunda:** `/deadlines/start`, `/deadlines/complete-task` for human tasks (management accounts, XBRL, ECI, FS, AGM, AR, tax filing, etc.).
- **Rules:** Skips sole proprietorship when configured; blocks duplicate active deadline process per FY unless `skip_validation`; optionally chains `initiateAgmARWorkflow` when `corpsec_squad` AGM/AR feature enabled.

### Corp Pass (`corp-pass.js`)

- **MongoDB:** `CorpPassCredentials` — `getCorpPassStatus`, `setCorpPassStatus`, `deleteCorpPassStatus` to coordinate workflow bot sessions (avoid concurrent login invalidation).

### SBA application (`sba-application.js`)

- **Exports:** `getSbaApplicationDetails`, `overrideSbaAutomatedApproval`, `approveSbaApplicationIfPossible` (used from risk-assessment).
- **Logic:** Force-reject rules (compliance A5 override, crypto B10), automated approval override for low/medium RAF with audit and FinOps email when business accounts exist; integrates `businessAccountService`, `RiskAssessmentFormApproval`, `Company` SBA status fields.
