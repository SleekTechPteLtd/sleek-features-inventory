# Send Xero transfer and user-access onboarding emails

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Send Xero transfer and user-access onboarding emails |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company user (authenticated); company manager for the manual “transfer” send route; system / workflow for the Camunda-driven path |
| **Business Outcome** | Clients get the correct Xero handoff instructions—either inviting Sleek as an adviser (transfer) or granting user access—so onboarding matches how their books are set up and whether the company is a transfer client. |
| **Entry Point / Surface** | Sleek API: `POST /v2/send-transfer-xero-email/company/:companyId` (manager-gated); `POST /v2/send-transfer-xero-email/company/:companyId/send-onboarding-email` (authenticated user); Camunda external task / workflow calls `executeSendTransferXeroToUsEmailFunc` (reads `accountingToolType` from Camunda variables). Customer app surfaces that call these APIs are not named in these files. |
| **Short Description** | Sends transactional emails via `mailerService.sendEmail` using default templates `ACCOUNTING_TRANSFER_XERO_TO_US` or `ACCOUNTING_USER_ACCESS_TO_XERO`, or CMS-overridden template IDs when `transfer_email_templates_enabled` supplies `user_access` / `transfer` map entries. Chooses transfer vs user-access using app feature flags (`accounting_set_up`: `is_user_access_email_transfer_enabled`, `transfer_email_rules_enabled`), company `is_transfer`, questionnaire `accounting_software_type` and company `accounting_tools.accountingLedger`, and loaded accounting-manager / senior-accountant / junior-accountant assignments. Optional “all three resources assigned” rule can block or no-op sends (commented as AU mitigation). Updates `AccountingQuestionnaire.onboarding_email_triggered` to system vs user trigger constants after send. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Mailer (`mailer-service`); app features (`accounting_set_up` / `getAppFeaturesByName`); accounting onboarding questionnaire; company resource allocation (accounting-manager, senior-accountant, junior-accountant); Camunda Pilot API `variable-instance` + `postResource` for workflow-triggered sends; regional post-onboarding accountant notification emails (`NOTIFY_SG_ACCOUNTANTS_VIA_EMAIL`, `NOTIFY_HK_ACCOUNTANTS_VIA_EMAIL`) live in the same handler module but are separate templates and flows. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `accountingquestionnaires`, `companyusers`, `users`, `companies`, `companyresourceusers` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact customer-app screens and copy for triggering `/send-onboarding-email` vs the manager-only route; whether regional SG/HK accountant emails should be a separate inventory feature (same file); per-market rollout is not explicit on the transfer vs user-access routes (feature flags only). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Router (`controllers-v2/accounting-transfer-xero-email.js`)

Mounted at `app-router.js`: `router.use("/v2/send-transfer-xero-email", ...)`.

- **POST** `/company/:companyId` — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")` → `executeSendTransferXeroToUsEmail`. Sends **transfer** template only (`sendTransferXeroToUsEmail`); requires questionnaire `accounting_software == "Xero"` and a `CompanyUser` for the current user.
- **POST** `/company/:companyId/send-onboarding-email` — `userService.authMiddleware` → `sendOnboardingEmail`. Validates company UEN; optional `body.companyUserId` else owner; runs full transfer vs user-access selection and questionnaire update.

### Handler (`controllers-v2/handlers/accounting-transfer-xero-email/sendEmail.js`)

- **`sendTransferXeroToUsEmail` / `sendUserAccessToXeroEmail`** — wrap `mailerService.sendEmail` with optional template override.
- **`setupTransferXeroToUsEmail(query, { accountingToolType }, options)`** — loads `AccountingQuestionnaire`, `User` (if `options.userId`), `CompanyUser`, feature props from `getAppFeatureList` / `getAppFeaturePropByNameAndCategory` (`is_user_access_email_transfer_enabled`, `transfer_email_templates_enabled`, `transfer_email_rules_enabled`), `companyResourceUtil.findCompanyResources` for three accounting roles; resolves `isSendUserAccessEmail()`; may return early when `transfer_email_rules_enabled` rules fail; `AccountingQuestionnaire.updateOne` sets `onboarding_email_triggered: TRIGGER_OPTIONS.SENT_BY_SYSTEM`.
- **`executeSendTransferXeroToUsEmail`** — HTTP handler for simple transfer email path (no user-access branch).
- **`executeSendTransferXeroToUsEmailFunc`** — loads Camunda variable `accountingToolType`, calls `setupTransferXeroToUsEmail` without `userId` in options (owner query path via `is_owner` in nested logic when no user in options—see `setupTransferXeroToUsEmail` branches).
- **`sendOnboardingEmail`** — duplicate feature-flag and template-selection logic for HTTP; `mailerService.sendEmail` with resolved template; `onboarding_email_triggered: TRIGGER_OPTIONS.SENT_BY_USER`; 400-style response when transfer rules require all three accountants assigned and any name is missing.

### External orchestration

- `controllers-v2/handlers/camunda-workflow/external-task-processor.js` imports `executeSendTransferXeroToUsEmailFunc`, `triggerEmailAfterOnboardingForSG`, `triggerEmailAfterOnboardingForHK`.

### Config / constants

- Mailer templates: `config.mailer.templates.ACCOUNTING_TRANSFER_XERO_TO_US`, `ACCOUNTING_USER_ACCESS_TO_XERO`; `TRIGGER_OPTIONS` from `constants/accounting-onboarding-questionnaire-trigger-options`.
