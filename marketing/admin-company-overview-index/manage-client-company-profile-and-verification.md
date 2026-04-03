# Manage client company profile and verification

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage client company profile and verification |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations and internal admin users (Sleek Admin) with company view/edit permissions (`permissions.companies` full or edit for edits) |
| **Business Outcome** | Client company legal identity, addresses, activity and onboarding questionnaire data stay accurate and reviewable in admin, supporting compliance (CDD), risk (RAF), and operational handover. |
| **Entry Point / Surface** | **sleek-website** admin: **Company overview** at `/admin/company-overview/?cid=<companyId>` when CMS `companies.overview.new_ui` is enabled (otherwise users are redirected to `/admin/companies/edit/`). Sidebar tabs include **Overview** (`CompanyInfo`) and **Company Info** (`CompanyVerification`) for the flows described here. |
| **Short Description** | **Overview** tab: staff view and edit core company fields (about the company, activity, registered and business operation addresses, optional onboarding preferences, business account flags, staff/resource assignment, linked workflows). Saves go through **`handleCompanyInfoUpdate`** → **`api.editCompany`** (admin), optional **`api.changeCompanyStatus`**, onboarding profile updates via child ref, Camunda risk-rating sync when configured, and FYE hooks. **Company Info** tab: displays and edits CMS-driven CDD / company verification questionnaire from **`companyProfile`** (`onboarding_information`), SSIC follow-ups, optional profile history via **`api.getCompanyProfileHistory`**, and persists with **`api.updateCompanyProfile`**. Risk ratings and RAF-related fields tie to CMS `kyc_raf` and workflow data when enabled. |
| **Variants / Markets** | Tenant-specific via `getPlatformConfig` / CMS (e.g. address types, SSIC, risk rating visibility, sole trader rules). Typical Sleek markets **SG, HK, UK, AU**; exact toggles per tenant — use **Unknown** for unconfirmed tenants. |
| **Dependencies / Related Flows** | **`api.getCompany`**, **`api.editCompany`**, **`api.changeCompanyStatus`** (sleek-back admin company APIs). **`api.getCompanyProfile`**, **`api.getCompanyProfileHistory`**, **`api.updateCompanyProfile`**, **`api.createCompanyProfile`** (`/companies/:id/company-profile[...]`). **`apiSleekFye.getCompanyFye`**, **`apiWfe.updateProcessSavedData`** (risk assessment workflow). **`api.updateCompanyResourceAllocation`**, **`api.updateCompanyResourceGroupAllocation`**, **`api.editCompany`** (`assigned_to`). Post-payment onboarding bypass (`postPostpaymentOnboardingBypassStatus`, `postLaunchDashboard`, `onboardingProcessPostPayment`). **`getCompanyVerificationData`** / **`getCompanyBusinessNature`** (industry lists). Related: **People & Entities** on the same page for per-user KYC actions; **Company edit** legacy page when new UI off. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/index.js` (`AdminCompanyOverview`), `src/views/admin/company-overview/company-info.js` (`CompanyInfo`), `src/views/admin/company-overview/company-verification.js` (`CompanyVerification`), `src/utils/api.js`, `src/utils/company-utils.js` (`getCompanyVerificationData`, `getCompanyIncorporationType`), Camunda services under `src/views/admin/sleek-workflow/`. **sleek-back** (not in repo): admin company and company-profile HTTP handlers and persistence. |
| **DB - Collections** | **MongoDB** (backend; not defined in sleek-website): **`Company`** and related subdocuments for profile, status, addresses, risk fields, assignments; **`CompanyProfile`** (or equivalent) for `onboarding_information` / CDD answers — **Unknown** exact collection names without current sleek-back schema. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC route names for company-profile endpoints when called from admin session; whether all tenants expose both Overview and Company Info tabs or only when `company_info_tab` / questionnaire completion flags apply. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-overview/index.js` (`AdminCompanyOverview`)

- **Bootstrap**: `domready` → `ReactDOM.render` into `#root`; loads platform config, **`api.getUser`**, **`api.getCompany(query.cid, { admin: true })`**, **`apiSleekFye.getCompanyFye`**, **`api.getCompanyProfile`**. If **`companies.overview.new_ui`** is not enabled, redirects to **`/admin/companies/edit/?cid=`**.
- **Permissions**: `isUserAllowedToEditCompany` from `user.permissions.companies` === `full` or `edit`.
- **Overview tab**: Renders **`CompanyInfo`** when `currentPage` is **`PAGES.OVERVIEW`** and data loaded.
- **Company Info tab**: Renders **`CompanyVerification`** when **`PAGES.COMPANY_INFO`** (CDD / verification questionnaire surface).
- **Save pipeline**: **`handleCompanyInfoUpdate`** validates **`companyInfoForm`**, page header, live-status rules, FYE; builds payload (name, type, identifiers via **`setCompanyIdentifiers`**, natures of business, addresses, business operation address, status, risk ratings when enabled, etc.); **`api.editCompany`** with **`admin: true`**; on status change **`api.changeCompanyStatus`**; optional onboarding bypass side effects; then **`companyInfoRef.current.handleCompanyProfileUpdate()`** when onboarding preferences enabled; risk rating workflow update via **`apiWfe.updateProcessSavedData`** when workflow-linked rating changes; refresh via **`getCompany`** / **`getCompanyFyeInfo`** in success path.
- **Cancel edit**: **`handleCancelCompanyInfoUpdate`** refreshes company state and validations.

### `src/views/admin/company-overview/company-info.js` (`CompanyInfo`)

- **Sections**: **`aboutTheCompanyForm`**, **`companyActivityForm`**, **`companyAddressForm`**, optional **Onboarding Preferences** (when CMS enabled) via **`initializeCompanyProfileData`** / **`getCompanyProfile`**, optional **Business Account** block, **Staff assigned** / **`StaffAssigned`**, **Workflows** when `user.permissions.manage_workflows` !== `none`**.
- **Risk / compliance UI**: Risk rating fields driven by CMS **`kyc_raf`**, **`risk_assessment`**, **`company_overview_tab_labels`**; **`perform_kyc`** permission gates some edits.
- **Persistence**: Core company updates delegated to parent **`handleCompanyInfoUpdate`**. Onboarding preferences subset: **`handleCompanyProfileUpdate`** → **`api.updateCompanyProfile`** or **`api.createCompanyProfile`** when no profile id. Staff assignment modal: **`api.updateCompanyResourceGroupAllocation`**, **`api.editCompany`** (`assigned_to`), **`api.updateCompanyResourceAllocation`**, deadline assignee sync via **`updateExistingDeadlineAssigneesViaStaffAssigned`**.

### `src/views/admin/company-overview/company-verification.js` (`CompanyVerification`)

- **Load**: **`getCompanyProfileHistory`** → history dropdown; **`loadConfig`** uses **`getCompanyVerificationData`** (platform config + `companyProfile` + transfer flag) for template sections/answers.
- **Display**: Dynamic questionnaire sections, SSIC-linked questions, legacy **`oldCddAnswers`** block for template v1, crypto-related read-only fields from onboarding data.
- **Save**: **`handleCompanyProfileUpdate`** / **`parseAndCleanAnswers`** → **`api.updateCompanyProfile`** with **`onboarding_information`** payload; snackbar on success; exits edit via **`handleCancelCompanyInfoUpdate`**.

### `src/utils/api.js`

- **`getCompanyProfile`**: `GET .../companies/:companyId/company-profile`
- **`getCompanyProfileHistory`**: `GET .../companies/:companyId/company-profile-history`
- **`updateCompanyProfile`**: `PUT .../companies/:companyId/company-profile/:companyProfileId`
- **`createCompanyProfile`**: `POST .../companies/:companyId/company-profile`
- **`getCompany`** / **`editCompany`** with **`admin: true`** → admin-prefixed company routes as elsewhere in the app.
