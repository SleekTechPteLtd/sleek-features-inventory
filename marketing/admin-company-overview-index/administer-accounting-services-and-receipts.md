# Administer accounting services and receipts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Administer accounting services and receipts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | A client company’s accounting subscriptions, onboarding questionnaire, receipt capture setup, accounting dashboard access visibility, and internal accounting team assignment are configured from the company overview so Sleek can deliver accounting and receipts services consistently. |
| **Entry Point / Surface** | **sleek-website** admin: **Company overview** — **Accounting** tab (`/admin/company-overview/?cid={companyId}&currentPage=Accounting`). Renders after company data load when the Accounting page is selected; legacy vs microservice UI is chosen by `company.microservice_enabled` (see Evidence). |
| **Short Description** | Operations staff manage the full accounting tab: accounting subscription context (including upgrade signals where shown), onboarding questionnaire (load/edit/save, send questionnaire or onboarding email, tax info updates), finance/payroll/previous-accountant contacts, currencies, payroll and bank details, invoice setup, resource allocation for accounting roles (with deadline assignee sync), receipt users (CRUD, email-in validation, optional WhatsApp resend on microservice), Hubdoc/receipt system fields persisted via parent `updateCompanyReceiptConfig`, and read-only visibility of accounting dashboard user emails when the CMS feature is enabled. Microservice companies use a variant that adds Sleek Billings config, BSM company info for questionnaire context, document submission, and billing-style upgrade UI where applicable. |
| **Variants / Markets** | Multi-tenant via CMS (`onboarding_meta.accounting_onboarding_workflow`, `sleek_receipts_settings`, `accounting_dashboard_settings`, `accounting_questionnaire`, migration and BSM flags). Typical Sleek markets **SG, HK, UK, AU**; exact enablement per tenant is CMS-driven — treat full per-market matrix as **Unknown** without backend confirmation. |
| **Dependencies / Related Flows** | **Parent** `company-overview/index.js`: loads `dashboardUsers` via `api.getCompanyPrivilege(…, ACCOUNTING_DASHBOARD.GROUP_NAME)` when `accounting_dashboard_settings` enabled; `handleReceiptSystemUpdate` → `api.updateCompanyReceiptConfig`; passes `receiptUsers`, `groups`, `groupUsers`, subscriptions. **API (sleek-back)**: questionnaire `getAccountingOnboardingQuestionnaireAnswers`, `postAccountingOnboardingQuestionnaire`, `sendAccountingOnboardingQuestionnaire`, `sendOnboardingEmail`, `putAccountingQuestionaireTaxInfo`; receipt users `getCompanyReceiptUsers`, `updateReceiptUser`, `createReceiptUser`; `validateEmailInAddress`; resource allocation `getCompanyResourceAllocation`, `updateCompanyResourceAllocation`. **Sleek workflow**: `updateExistingDeadlineAssigneesViaStaffAssigned` after resource allocation save. **Microservice-only**: `sleekBillingsAPI.getSleekBillingsConfig`, `bankStatementEngineAPI.getBsmCompanyInfo`, `api.generateEmailInAddress`, `api.resendWhastappActivationToReceiptUser`. Legacy path: `api.runUpgradeOrDowngrade` where triggered. **Related**: Company edit accounting configuration (`admin-companies-edit-index`) overlaps capability but uses a different admin route. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/accounting.js`, `accounting.microservice.js`, parent `index.js` (receipt config, dashboard users). **sleek-back** (API persistence): not in this repo. Optional **Sleek Billings** / **BSM** clients in microservice path. |
| **DB - Collections** | Unknown — persistence is in sleek-back (company, questionnaire, receipt users, privileges, resource allocations, etc.). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High for UI and client API paths; Medium for exact backend schema and all edge cases. |
| **Disposition** | Unknown |
| **Open Questions** | Full parity list between legacy `accounting.js` and `accounting.microservice.js` beyond imports and the calls noted in Evidence (e.g. all conditional UI branches). Exact RBAC on each endpoint in sleek-back. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routing and composition — `src/views/admin/company-overview/index.js`

- Accounting content mounts when `isCurrentPage(PAGES.ACCOUNTING)` and `isDataLoaded`; `PAGES.ACCOUNTING` is `"Accounting"` (see `constants.js`), aligned with `currentPage=Accounting` in the query string.
- **Variant selection**: `company.microservice_enabled ? <AccountingMicroservice … /> : <Accounting … />` — shared props include `dashboardUsers`, `accountingDashboardSettingsEnabled`, `subscriptions`, `receiptUsers`, `handleReceiptSystemOnChange`, `handleReceiptSystemUpdate`, `getGroupsAndUsers`, `setAccountingBreadCrumbText`, `getCompanySubscriptions`, etc.

### Receipt system and dashboard users (parent)

- **Dashboard emails**: When `accounting_dashboard_settings` enabled, `api.getCompanyPrivilege(company._id, ACCOUNTING_DASHBOARD.GROUP_NAME)` → maps to `dashboardUsers` passed into both Accounting components (read-only display in tab).
- **Receipt config save**: `handleReceiptSystemUpdate` builds JSON with `hubdoc_address`, `receipt_system_status`, `allow_mass_update: true` → `api.updateCompanyReceiptConfig(company._id, options)`.

### `accounting.js` (legacy / non-microservice company)

- **Mount**: `getAccountingServicesBasedOnTags(ENABLE_ACCOUNTING_PAGE_IN_ADMIN_APP)` to classify `companyAccountingSubscriptions`; loads questionnaire via `api.getAccountingOnboardingQuestionnaireAnswers`, `api.getCompanyResourceAllocation`; CMS-driven options from `onboarding_meta.accounting_onboarding_workflow` and related props; if `sleek_receipts_settings` enabled, `fetchReceiptUsers` → `api.getCompanyReceiptUsers`.
- **Questionnaire actions**: `api.sendAccountingOnboardingQuestionnaire`, `api.sendOnboardingEmail`, `api.postAccountingOnboardingQuestionnaire`, `api.putAccountingQuestionaireTaxInfo`.
- **Receipt users**: `api.updateReceiptUser`, `api.createReceiptUser`; `api.validateEmailInAddress` when email-in enabled.
- **Staff / allocation**: `api.updateCompanyResourceAllocation` then `updateExistingDeadlineAssigneesViaStaffAssigned(company, platformConfig)`; `getGroupsAndUsers` refresh.
- **Subscriptions / upgrade**: `<Subscriptions … />` card; `api.runUpgradeOrDowngrade` in upgrade flow.

### `accounting.microservice.js` (microservice-enabled company)

- **Additional load**: `sleekBillingsAPI.getSleekBillingsConfig()`; questionnaire path may merge `bankStatementEngineAPI.getBsmCompanyInfo(company._id)` when loading answers.
- **Email-in**: `api.generateEmailInAddress` in addition to `validateEmailInAddress`.
- **Receipt users**: `api.resendWhastappActivationToReceiptUser` in microservice-specific handlers.
- **UI**: `AccountingUpgrade`, `AccountingDocumentSubmission` (vs legacy `Subscriptions` and related modals); no `runUpgradeOrDowngrade` grep match in the microservice file (upgrade path differs).

### Shared imports and behaviour

- Forms from `views/admin/accounting/accounting-forms/` (finance contact, company setup, currencies, payroll, onboarding info, bank, invoice, receipt user); `AccountingService.parseQuestionnaire`; `StaffAssigned`, `PreviousAccountantInformation`, `IndividualTaxInformationForm`, `AccountingTools`; `ACCOUNTING_TAB_VIEWS` for sub-views.
