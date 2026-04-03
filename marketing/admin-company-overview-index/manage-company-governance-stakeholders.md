# Manage company governance and stakeholders

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company governance and stakeholders |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek Admin) |
| **Business Outcome** | Client companies’ officers, owners, registers, and related KYC and invitation state stay accurate and actionable from the Company Overview workspace so compliance and downstream workflows can rely on them. |
| **Entry Point / Surface** | **sleek-website** admin: **Company Overview** — `/admin/company-overview/?cid={companyId}` with side navigation **People & Entities** (`currentPage=People+%26+Entities`). Deep links from workflows and support screens use the same base URL with `currentPage` and optional `editCorpShare`, `shareholder`, `cu` + `userdetails` query params. |
| **Short Description** | On the **People & Entities** tab, operations staff view and edit directors (including SG nominee split), shareholders (individual/corporate, with optional company-shares microservice data), company secretaries (natural, corporate, default Sleek secretary), significant controllers, registrable controllers, designated representatives, admins, standard users, beneficial owners (UBO, when enabled), AU trust/public-officer style roles, and UK sales point of contact. The parent view lazy-loads tab-specific APIs (secretaries, registers, KYC workflows, officer history) and reuses the same **`companies/edit`** presentation components as Company Edit, with tenant-specific branches (e.g. GB `OfficersSection` vs legacy tables, AU hiding some tables). KYC, invite resend, force accept, Camunda KYC workflows, and 2FA wrap edit flows where wired. |
| **Variants / Markets** | **SG, HK, UK, AU** (and default tenant) — `getValuePerTenant` / `getAppFeatureProp` / `platformConfig.tenant` gate sections (e.g. nominee directors SG-only, UK sales POC, AU trust/public officer blocks, GB officer UX). Exact enablement per sub-register varies by CMS flags (`significant_controllers_register`, `registrable_controllers`, `designated_representatives`, `beneficial_owner`, `company_shares_microservice`). |
| **Dependencies / Related Flows** | **Shared UI** with **Company Edit** (`src/views/admin/companies/edit/*` — directors, shareholders, secretaries, registrable controllers, etc.). **APIs** via `src/utils/api.js` and related modules: company users, secretaries, significant/registrable controllers, designated representatives, company history (`getCompanyHistory` / officer appointments), `getCompanySharesByCompanyId`, KYC workflow fetches (`apiWfe.getKycCompanyWorkflows`). **Cross-links** from incorporation/KYC workflow tasks and other admin surfaces open Company Overview → People & Entities. Backend persistence in **sleek-back** (not in repo). |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/index.js` (`AdminCompanyOverview`), `src/views/admin/company-overview/people-entities.js`, `src/views/admin/company-overview/constants.js` (`PAGES.PEOPLE_AND_ENTITIES`); shared components under `src/views/admin/companies/edit/`, `src/components/officers-components/`, `src/components/company-sleek-kyc-section`, etc. |
| **DB - Collections** | Unknown — MongoDB collections are not referenced in sleek-website; data accessed through HTTP APIs only. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Shell and routing — `src/views/admin/company-overview/index.js`

- **`AdminCompanyOverview`** mounts from `#root` on the company-overview bundle (`webpack` entry `admin/company-overview/index`).
- **`setSideNavigationOnLoad`**: reads `currentPage` query param; forces **People & Entities** when `cu` + `userdetails` are present (`goToUserDetailsForm` then opens the correct edit flow for director/shareholder/owner).
- **`loadPeopleAndEntitiesData`**: runs when `isCurrentPage(PAGES.PEOPLE_AND_ENTITIES)` and `peopleAndEntitiesDataLoaded` is false — loads secretaries (`getCompanySecretaries`, `getCompanyCorporateSecretaries` incl. resigned), `getBeneficialOwners`, gated **SCR** / **registrable** / **designated** lists, `enableAddingOfShareholder` URL flag, `kycCompanyWorkflows` when KYC refresh or HK workflow CMS flags on, `companyUserRoles`, then **`getCompanyOfficerAppointmentDetails`** → `getCompanyHistory` + `extractUserPerRoleAndHistoryStatus` for resigned/appointed directors and shareholders.
- **`PeopleEntities`** render block (when `isCurrentPage(PAGES.PEOPLE_AND_ENTITIES)`) passes through dozens of handlers shared with company edit: KYC (`handleStartKyc`, `handleSubmitSleekKyc`, refresh/resend), invite (`handleResendInvitation`, `handleForceInviteAcceptance`), officer GB flows (`handleClickEditOfficer`, `OfficerAddForm`), `reloadPeopleAndEntitiesData`, designated representatives as JSX prop, `companySignificantControllers` from parent state.

### Composition and tenant behaviour — `src/views/admin/company-overview/people-entities.js`

- **Imports** legacy sections from `../companies/edit/`: `Directors`, `NomineeDirectors`, `Admins`, `Shareholders`, `CompanySecretaries`, `CompanyRegistrableControllers`, `StandardUsers`, `CompanySleekSecretary`, `SalesPointOfContact`; plus **`OfficersSection`** / **`OfficerAddForm`** for GB (and other unified officer UX).
- **`componentDidMount`**: optional deep link `editCorpShare` + `shareholder` → `handleClickEditShareholder`; `editUserFunction` + `editUserId` → dynamic edit opener; loads **`getCompanySharesByCompanyId`** when `company_shares_microservice` CMS flag enabled.
- **Director split for SG**: `regularDirectors` vs `nomineeDirectors` / resigned lists using `user.is_nominee_director`.
- **Conditional stacks**: `partner_draft` company status hides admins section; `company.is_shareholder` returns a reduced layout (directors, nominee block, individual shareholders, admins only).
- **Registers**: `companySignificantControllers` vs `CompanyRegistrableControllers` depending on `registrable_controllers` feature; `designatedRepresentatives` prop when form not fullscreen; `CompanySleekSecretary` for default secretary form.
- **Beneficial owners**: `OfficersSection` with `COMPANY_USER_ROLES.UBO` when `beneficial_owner` CMS enabled.
- **AU-only role rows**: `individualTrustShareholders`, `corporateTrustShareholders`, `publicOfficers` when `isDisplayNewRolesPerTenant` (AU).
- **Fullscreen form modes** return early with single section or `OfficerAddForm` / edit forms embedding **`CompanySleekKycSection`**, **`CompanyShareDetailsSection`**, 2FA as in company edit.

### Constants — `src/views/admin/company-overview/constants.js`

- `PAGES.PEOPLE_AND_ENTITIES === "People & Entities"` — tab label and `currentPage` value.

### External references (same repo)

- Workflow and admin UIs build URLs such as ``/admin/company-overview/?cid=${companyId}&currentPage=...`` pointing at this surface (e.g. `kyc-overview-all-users.js`, `kyc-complete-task-button.js`, `officer-table-list.js`).
