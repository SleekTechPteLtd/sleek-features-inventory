# Manage risk assessment form approvals

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage risk assessment form approvals |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / company user (requestor); internal user acting as approver; Sleek Admin (bypasses workflow membership checks via `getWorkflowMiddleware`); Compliance (email recipients) |
| **Business Outcome** | Captures who requested and who approved or rejected RAF customer-acceptance for incorporation and SBA (pre- or post-onboarding) workflows, preserves an audit trail, keeps workflow data in sync, and triggers compliance notifications so regulated onboarding decisions are traceable and acted on. |
| **Entry Point / Surface** | Authenticated API: `POST /v2/risk-assessment-form-approval/:business_key` (create/update approval by Camunda `business_key`); `GET /v2/risk-assessment-form-approval/:id` (read approval by Mongo `_id`). GET uses `authMiddleware` plus `getWorkflowMiddleware()` (company/workflow access); POST is auth-only. Embedded in company workflow tasks (Sleek Admin workflow URL built into email variables). |
| **Short Description** | Creates or updates `RiskAssessmentFormApproval` records per `approval_type` and `CompanyWorkflow`, tracks status (`pending`, `need_more_info`, `approved`, `rejected`), requestor vs approver, optional file attachments, and append-only history. Updates `CompanyWorkflow.data.<approval_type>.raf_approval` with the approval id. For `sba_raf_pre_onboarding`, syncs `Company.sba_application_status` and timestamp. Sends template-based emails via `kyc-risk-assesment-form` (incorporation vs SBA templates, including post-onboarding variants). |
| **Variants / Markets** | SG (SBA and incorporation RAF paths evidenced); HK, UK, AU — Unknown |
| **Dependencies / Related Flows** | `CompanyWorkflow` / Camunda workflows (`business_key`); `kyc_raf` app features (`raf_customer_acceptance`, templates); mailer (`mailer-vendor`); `File` + `file-service` for attachments; SBA onboarding and risk-assessment Camunda handlers also reference `RiskAssessmentFormApproval` |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `riskassessmentformapprovals` (Mongoose model `RiskAssessmentFormApproval`); `companyworkflows`; `companies` (`sba_application_status`, `sba_application_status_updated_at` when type is `sba_raf_pre_onboarding`); `files` (referenced attachment ids) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Schema allows `cdd_incorporation_raf`, `cdd_sba_raf`, and `transfer_raf` approval types, but the v2 handler constants only name incorporation and SBA pre/post types — confirm whether those extra enum values are written via this API or other paths. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Router (`controllers-v2/risk-assessment-form-approval.js`)

- **Routes:** `POST /:business_key` → `createAndUpdateRAFApproval` with `userService.authMiddleware` only. `GET /:id` → `getRAFApproval` with `authMiddleware` and `getWorkflowMiddleware()`.
- **Mount:** `app-router.js` — `/v2/risk-assessment-form-approval`.

### Handler (`controllers-v2/handlers/risk-assessment-form-approval/risk-assessment-form-approval.js`)

- **Workflow resolution:** `CompanyWorkflow.findOne({ business_key }).populate("company")`.
- **Upsert:** `RiskAssessmentFormApproval.findOne({ company_workflow, approval_type })`; create on first write with `files`, `message`, `status`, `company`, `company_workflow`, empty `history`.
- **Status / roles:** On `pending`, sets `requestor` and `approver` (array from body); otherwise sets `approverUser` to current user. Pushes `history` entries (`remarks`, `user`, `status`, `approvers`).
- **Emails (`_handleSendEmails`):** Uses `appFeatureUtil` `kyc_raf` / `raf_customer_acceptance` for default approver CC logic. Pending → `sendEmailNotificationToComplianceCustomerAcceptance` with `KYC_RAF_REQUEST_FORM_APPROVAL` or `SBA_REQUEST_FORM_APPROVAL`. SBA approved/rejected → `sendSBAEmailNotificationToCompliance`; other transitions → customer-acceptance templates including `SBA_RAF_SBA_APPLICATION_PENDING_PRE_ONBOARDING` / `POST_ONBOARDING` vs `KYC_RAF_CUSTOMER_ACCEPTANCE_PENDING`.
- **Workflow linkage:** `CompanyWorkflow.findByIdAndUpdate` sets `data.${approval_type}.raf_approval` to the approval document id.
- **SBA sync:** If `approval_type === sba_raf_pre_onboarding`, `Company.updateOne` sets `sba_application_status` and `sba_application_status_updated_at`.
- **Read:** `getRAFApproval` — `findById` with populate on `requestor`, `approverUser`, `history.user`.

### Service (`services/kyc-risk-assesment-form.js`)

- **`sendEmailNotificationToComplianceCustomerAcceptance`:** Builds Sleek Admin workflow task URL from `companyWorkflow.business_key` and `data.processInstanceId`; loads files for attachments; sends via `mailerVendor.sendEmail` with CC to `config.compliance.emails` and template map by status (overridable per call).
- **`sendSBAEmailNotificationToCompliance`:** Templates `KYC_RAF_SBA_PRE_ONBOARDING_APPROVED` / `REJECTED`, `KYC_RAF_SBA_POST_ONBOARDING_REVOKED` / `APPROVED`; links to company overview or workflow task; recipients include `config.business_account.emails` and requestor when present.

### Schema (`schemas/risk-assessment-form-approval.js`)

- **Model:** `RiskAssessmentFormApproval`; subdocument logs with `user`, `status`, `approvers`, timestamps.
- **Fields:** `approval_type` (enum includes incorporation, SBA pre/post, CDD, transfer variants), `status`, `approver` (array), `requestor` / `approverUser` refs, `files`, `message`, `company`, `company_workflow`, `history`.

### Other references

- Aggregation / scripts use collection name `riskassessmentformapprovals` (e.g. `scripts/company-workflow/syncSBAApplicationStatus.js`).
