# Request Xero transfer-to-Sleek email

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Request Xero transfer-to-Sleek email |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company user (authenticated, with permission to manage the company); System (Camunda workflow / external task) |
| **Business Outcome** | Clients receive transfer instructions and Sleek accounting contact details so they can hand Xero administration or access over to Sleek. |
| **Entry Point / Surface** | API: `POST /v2/send-transfer-xero-email/company/:companyId` and `POST /v2/send-transfer-xero-email/company/:companyId/send-onboarding-email`; Camunda-driven send via `executeSendTransferXeroToUsEmailFunc` (exact in-app navigation path not determined from these files). |
| **Short Description** | For companies on Xero (per accounting questionnaire and, where applicable, company accounting tool metadata), the backend sends a transactional email through the mailer using templates such as transfer-to-Sleek or user-access-to-Xero. Payload includes addressee and company context plus support identities from config (`support.xeroTransferAccount`). Feature flags under app feature `accounting_set_up` can switch templates, enforce rules (e.g. all assigned accountants present), and choose user-access vs transfer copy for transfer clients. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Transactional email (`mailerService.sendEmail`); accounting onboarding questionnaire (`AccountingQuestionnaire`, `onboarding_email_triggered`); company user and company records; optional Camunda Pilot variable fetch (`accountingToolType`) for workflow sends; app-features CMS (`accounting_set_up`); company resource users (accounting manager / senior / junior) for conditional templates and AU-style rule mitigation; separate SG/HK onboarding accountant notification emails in same handler module. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `AccountingQuestionnaire`, `User`, `CompanyUser`, `Company`, `CompanyResourceUsers` (and company resource lookup via `companyResourceUtil` where used) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which product screens call each route; whether market-specific behaviour is enforced outside this module; full mapping of mailer template IDs to customer-visible copy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** (`sleek-back/app-router.js`): Router mounted at `/v2/send-transfer-xero-email` → `controllers-v2/accounting-transfer-xero-email.js`.
- **HTTP surface** (`controllers-v2/accounting-transfer-xero-email.js`):
  - `POST /company/:companyId` — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`, handler `executeSendTransferXeroToUsEmail`.
  - `POST /company/:companyId/send-onboarding-email` — `userService.authMiddleware`, handler `sendOnboardingEmail`.
- **Manual transfer email** (`sendEmail.js` — `executeSendTransferXeroToUsEmail`): Validates `companyId`; loads `AccountingQuestionnaire` for company; proceeds only if `accounting_software == "Xero"`; loads requesting `User` and `CompanyUser` (user + company populated); builds `emailPayLoad` with `addressee_name`, `department_name`, and `support.xeroTransferAccount` fields (`first_name`, `last_name`, `fromEmail`, `enquiry_email`, `adviser_email`); calls `sendTransferXeroToUsEmail` → `mailerService.sendEmail` with template `config.mailer.templates.ACCOUNTING_TRANSFER_XERO_TO_US` (default), `fromEmail` / `replyTo` from same config namespace.
- **Workflow / richer logic** (`setupTransferXeroToUsEmail`, `executeSendTransferXeroToUsEmailFunc`): Matches Xero-related questionnaire and tool types (`Xero`, `Xero (client)`, `Xero (Sleek)`); may send `ACCOUNTING_TRANSFER_XERO_TO_US` or `ACCOUNTING_USER_ACCESS_TO_XERO` based on `accounting_set_up` props (`is_user_access_email_transfer_enabled`, `transfer_email_templates_enabled`, `transfer_email_rules_enabled`, `company.is_transfer`); optional Camunda variable `accountingToolType` via `postResource` to `${config.sleekCamundaPilotBaseApiUrl}/camunda/variable-instance`; updates questionnaire `onboarding_email_triggered` to `TRIGGER_OPTIONS.SENT_BY_SYSTEM` when sent from this path.
- **Send onboarding email route** (`sendOnboardingEmail`): Requires company `uen`; optional `companyUserId` in body or defaults to owner; validates Xero-related software types including `company.accounting_tools.accountingLedger`; applies same template/rule logic as above; `mailerService.sendEmail` with resolved template; sets `onboarding_email_triggered` to `SENT_BY_USER`.
- **Camunda integration** (`controllers-v2/handlers/camunda-workflow/external-task-processor.js`): Invokes `executeSendTransferXeroToUsEmailFunc` with `companyId`, `businessKey`, `processInstanceId`.
- **Internal helpers**: `sendTransferXeroToUsEmail` / `sendUserAccessToXeroEmail` wrap `mailerService.sendEmail` with optional CMS-overridden template names.
