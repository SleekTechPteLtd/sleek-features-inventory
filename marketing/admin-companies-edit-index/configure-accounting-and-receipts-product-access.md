# Configure accounting and receipts product access

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Configure accounting and receipts product access |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / support staff (Sleek Admin users editing a company with accounting visibility) |
| **Business Outcome** | A client company’s accounting onboarding data, receipt capture setup, dashboard access visibility, and internal accounting team assignment are configured so Sleek can deliver accounting and receipts services consistently. |
| **Entry Point / Surface** | **sleek-website** admin: **Company edit** (`/admin/companies/edit/?cid={companyId}`) — accounting-related cards when `showAccountingInfo` is true and the relevant CMS feature flags are enabled (see Evidence). |
| **Short Description** | On the company edit screen, operations staff can: maintain the accounting onboarding questionnaire (view/edit answers, send the questionnaire to a company user with optional access-page selection, open linked Camunda accounting-onboarding tasks when configured); manage the receipt system (Hubdoc address, active/inactive status, list and CRUD actions on receipt users via parent handlers); view which emails hold accounting dashboard privileges; and assign Accounting group staff to Acct Manager, Senior Accountant, Junior Accountant, and Auditor roles (persisted as company resource allocation, with deadline assignee sync). |
| **Variants / Markets** | Multi-tenant via `platformConfig` / CMS (`onboarding_meta.accounting_onboarding_workflow`, `sleek_receipts_settings`, `accounting_dashboard_settings`, `accounting_team_roles`). Jurisdiction-specific behaviour appears in questionnaire sending rules (e.g. AU send override), HK Camunda workflow type, and copy (UEN label). **SG, HK, UK, AU** as typical Sleek markets; exact enablement per tenant is CMS-driven — treat per-market matrix as **Unknown** without backend confirmation. |
| **Dependencies / Related Flows** | **API (sleek-back)**: questionnaire `GET/POST` company questionnaire endpoints; `POST` send questionnaire; receipt users and config; company privilege for dashboard group; groups + admins-by-group; `PUT` company resource allocations. **Workflow**: WFE `getWorkflowProcesses`; Camunda `getSleekWorkflowProcesses` / `getTaskList` for HK accounting-onboarding-hk; navigation to `/admin/sleek-workflow/workflow-task/`. **Sleek workflow service**: `updateExistingDeadlineAssigneesViaStaffAssigned` after resource allocation save. **Related**: accounting services subscription gate (`hasAccountingServices`), `AccountingTools` embed when `show_accounting_tools_settings` applies. |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/edit/index.js` (composition, flags, data load, receipt actions), `accounting-onboarding-questionnaire-answers.js`, `accounting-receipt-user-management.js`, `accounting-dashboard-user-management.js`, `accounting-team-roles.js`, `src/utils/api.js`. **sleek-back** (API implementation, persistence): not in this repo. |
| **DB - Collections** | **Unknown** — collections are owned by sleek-back (company, questionnaire, receipt users, privileges, resource allocations, groups/users). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High (UI and API client paths are explicit); **Medium** for exact backend schema and all edge cases. |
| **Disposition** | Unknown |
| **Open Questions** | Whether deadline assignee sync failures are surfaced to the user beyond console logging. Exact MongoDB collections and RBAC rules on each endpoint in sleek-back. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Parent composition — `src/views/admin/companies/edit/index.js`

- **Onboarding questionnaire**: Rendered when `accounting_onboarding_workflow` from `onboarding_meta` is enabled — `<AccountingOnboardingQuestionnaireAnswers … showAccountingInfo hasAccountingServices company companyUsers user />`.
- **Receipt system**: When `cmsGeneralFeatureList.sleek_receipts_settings.enabled`, loads `api.getCompanyReceiptUsers(company._id)`; renders `<AccountingReceiptUserManagement />` with `sleekReceiptsSettingsEnabled && showAccountingInfo`.
- **Dashboard users**: When `cmsAppFeatures.accounting_dashboard_settings.enabled`, loads `api.getCompanyPrivilege(company._id, ACCOUNTING_DASHBOARD.GROUP_NAME)` and maps emails for `<AccountingDashboardUserManagement dashboardUsers />`.
- **Staff assigned**: When `cmsAppFeatures.accounting_team_roles.enabled`, renders `<AccountingTeamRoles company platformConfig />`.

### `src/views/admin/companies/edit/accounting-onboarding-questionnaire-answers.js`

- Loads `api.getAccountingOnboardingQuestionnaireAnswers(company._id)`; saves via `api.postAccountingOnboardingQuestionnaire`; sends link via `api.sendAccountingOnboardingQuestionnaire` with `companyUserId`, `isNewAccountingSetup`, `accessPage`.
- Optional Camunda: `getSleekWorkflowProcesses` (`workflow_type=accounting-onboarding-hk`), `getTaskList`; opens admin workflow task in a new tab. WFE: `wfApi.getWorkflowProcesses` for accounting onboarding flow class.
- Embeds `AccountingTools` when `show_accounting_tools_settings` and `showAccountingToolsInOnboarding` pass.

### `src/views/admin/companies/edit/accounting-receipt-user-management.js`

- Presentational: Hubdoc address, `receipt_system_status` select, receipt users table; actions delegate to parent — `handleEditReceiptUser`, `handleRemoveReceiptUser`, `handleClickCreateReceiptUser`, `updateCompanyReceiptConfig`, `handleReceiptSystemOnChange`.

### `src/views/admin/companies/edit/accounting-dashboard-user-management.js`

- Read-only textarea listing `dashboardUsers` emails (populated by parent).

### `src/views/admin/companies/edit/accounting-team-roles.js`

- `getGroups` → `GET ${getBaseUrl()}/admin/groups`; for Accounting group, `getAdminsByGroup` → `GET ${getBaseUrl()}/admin/users/admins` with `group_id`.
- Load: `api.getCompanyResourceAllocation(companyId)` → `GET …/companies/${companyId}/company-resource-allocation`.
- Save: `api.updateCompanyResourceAllocation(companyId, { resourceAllocation })` → `PUT …/companies/${companyId}/company-resource-allocations`; then `updateExistingDeadlineAssigneesViaStaffAssigned({ _id: companyId }, platformConfig)`.

### `src/utils/api.js` (representative endpoints)

- Questionnaire: `GET …/companies/${companyId}/accounting-questionnaire-answers`; `POST …/companies/${companyId}/accounting-questionnaire`; `POST …/companies/${companyId}/send-accounting-onboarding-questionnaire`.
- Receipts: `GET …/companies/${companyId}/receipt-users`; `POST …/admin/companies/${companyId}/update-receipt-config` (and receipt-user update paths used from parent).
- Dashboard privilege: `GET …/admin/companies/${companyId}/privilege/${groupName}`.
