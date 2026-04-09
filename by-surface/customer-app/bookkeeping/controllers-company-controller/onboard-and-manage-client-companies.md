# Onboard and manage client companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Onboard and manage client companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (authenticated Sleek client); Sleek Admin for cross-company list |
| **Business Outcome** | Clients can stand up draft companies, complete onboarding data, see progress toward go-live, and clean up unpaid drafts while controlling who can act on each company. |
| **Entry Point / Surface** | Sleek customer app — company portfolio (list/search), company detail, onboarding progress; API routes under `/companies` (v1 and `/v2/companies` create) |
| **Short Description** | Authenticated users create companies in `draft` (v1 snake_case or v2 camelCase payloads), become owner via `CompanyUser`, get file root and subscription stubs. They list and search their portfolio (`GET /companies`), load a company with optional loaders (`GET /companies/:companyId`), update fields while permissions allow (`PUT`), track incorporation-style onboarding via `check-progress` (workflow tasks + invite summaries), submit validation when roles are ready, and delete unpaid drafts. Per-user module privileges for accounting-style surfaces are exposed via `company-privileges`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `company-subscription-service` (subscription creation), `file-service` (company root folder), `invoice-service` (selected services validation), Camunda/`cs_workflow_instance` and `WorkflowTask` for task progress, `partner-service` (partner-origin bypass on `canManageCompanyMiddleware`), `access-control-service` (Sleek Admin, Accounting Management where used), downstream submit/apply-for-payment flows, auditor on delete |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies`, `companyusers`, `companyuserprivileges`; reads/writes also touch related docs populated from company detail (e.g. `files`, `invoices` on expected payment info) — full cascade on delete includes `companyhistories`, `companyworkflows`, `requestinstances`, etc. via `companyService.deleteCompany` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /companies/:companyId/user/:userId/company-privileges` requires `authMiddleware` only; confirm whether additional checks are enforced elsewhere (gateway) or if caller–company–user alignment should be explicit in code. Exact client-app navigation labels for “portfolio” vs admin routes not verified here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/company-controller.js`

- **Create (v1):** `POST /companies` — `authMiddleware`; validates `name`, `is_transfer`, `selected_services`, optional `record_type`; creates `Company` with `status: "draft"`, default share item; `CompanyUser` with `is_owner: true` and invite/invoice flags; `fileService.createCompanyRootFolder`; `companySubscriptionService.createCompanySubscriptions`; **201**.
- **Create (v2):** `POST /v2/companies` — same pattern with camelCase fields (`companyName`, `isTransfer`, `selectedServices`, UEN/proposed names, `natureOfBusiness`, `financialYear`, `businessName`, `recordType`).
- **Update draft/paid-incomplete fields:** `PUT /companies/:companyId` — `canManageCompanyMiddleware("ownerIncompleteCompany")`; field allowlist expands for Sleek Admin, draft, or `paid_and_incomplete`; subscription expiry guard for name changes; UEN uniqueness; persists company.
- **Detail:** `GET /companies/:companyId` — `canManageCompanyMiddleware("companyUser")`; populates workflows, payment info, optional `load` query (`files`, `subscriptions`, `fye`); cache headers.
- **Onboarding progress:** `GET /companies/:companyId/check-progress` — merges `cs_workflow_instance` presentation tasks (filtered section names) with `companyUserService.getCompanyUsersSummaryByCompany` (invite counts, shareholder/director coverage).
- **List / search portfolio:** `GET /companies` — builds query on `name`, `status`, `uen`, `is_shareholder`; restricts to user’s `CompanyUser` companies unless Sleek Admin; pagination via `skip`/`limit` (default limit from `PAGINATION_LIMIT`); returns `{ companies, count }`.
- **Remove unpaid draft:** `DELETE /companies/:companyId` — `canManageCompanyMiddleware("ownerIncompleteCompany")`; rejects if `hasCompanyPaid`; `companyService.deleteCompany`; auditor log.
- **Submit / payment-related (context):** `POST .../submit-to-validation`, `submit-company-members`, `apply-for-post-payment`, `apply-for-external-payment` — further onboarding pipeline (not fully expanded here).
- **Company–user privileges (flags/modules):** `GET /companies/:companyId/user/:userId/company-privileges` — loads `CompanyUserPrivilege.find({ company, user })`, returns array or `[]`.

### `services/company-service.js`

- **`canManageCompanyMiddleware` / `getManagePermission`:** Partner origin skips checks; Sleek Admin passes; draft/partner_draft relaxes owner to `companyUser`; locked company or `admin` permission mode rejects; validates owner vs any company user vs owner/director vs director+main POC via `CompanyUser` queries.
- **`deleteCompany`:** Cascading cleanup (files, company users via `companyUserService.deleteCompanyUser`, requests, history, workflows, profiles, risk, ComplyAdvantage, RCD/RAR, workflow instances/tasks) then deletes company document.
- **`hasCompanyPaid`:** Used to block delete when any paid invoice exists.
- **`retrieveCompanyData` / `buildFindQuery`:** Admin-style company data retrieval (separate from this controller’s list; evidence for broader company querying patterns).

### `services/company-user-service.js`

- **`getCompanyUsersSummaryByCompany`:** Aggregates invite acceptance and shareholder/director counts for progress UI.
- **`canManageCompanyUserMiddleware` / `setCompanyRightValue`:** Role resolution for editing company users (owner vs connected user vs director) depending on company status and KYC — supports related “who can manage people” flows.
- Exports used elsewhere for AOQ emails, KYC, share transactions, etc.

### `schemas/company-user-privilege.js`

- Mongoose model **`CompanyUserPrivilege`**: `group_name`, `user`, `company` (indexed), `modules` array, timestamps; JSDoc references `general_accounting_dashboard` style module config (filters, `site_name`, `label`).
