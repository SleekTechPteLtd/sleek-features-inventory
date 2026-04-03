# Manage UK LTD onboarding from LC Website

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage UK LTD onboarding from LC Website |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | After Companies House formation, UK limited companies initiated on the LC Website are provisioned in Sleek with aligned users, company records, cap table and governance data, incorporation documents, and optional accounting onboarding follow-up, while incomplete payloads are recorded for backfill. |
| **Entry Point / Surface** | Internal integration: LC Website (or trusted backend) calls `sleek-back` under `/v2/ltd-onboarding/*`, guarded by `internalServicesMiddleware` (Basic `Authorization` with configured internal secret; optional bypass in dev). Not exposed to customer web or mobile clients. |
| **Short Description** | **Create** (`POST /create-company`): invite or reuse users, create/update company draft via internal company APIs, optional comments to audit log, create officers/share allocations, pull Companies House PDF by `docKey` and split/upload to incorporation folder, and upsert `ltdmigrations` when `validateData` reports missing required fields. **Update** (`PUT /create-company`): refresh user and company draft, clear and rebuild officers, mark company live (transfer path), FYE updates, accounting questionnaire fields, optional accounting questionnaire email when `sendAccountingInvite` and active accounting subscription, documents and migration gap record. **Check** (`GET /check-company/:uen`): returns whether a company with that UEN already exists. |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | **`/v2/company/insert/`**, **`/v2/company/update/`** (HTTP from service using user auth token). **`/users-invite`**, **`userService.loginKeep`**. **`/companies/:companyId/company-users-without-email`**, **`/v2/company-user-roles/:companyId/corporate-director`**, PSC and company-secretary resource allocation routes. **`sleekCompanyRoles` company-shares microservice** (GET/POST). **`companyHouseService.getCompanyDocument`**, **`fileService`** (incorporation PDF split: certificate, memorandum). **`accountingQuestionnaireService`**, **`companyUserService.sendAccountingOnboardingQuestionnaire`** (update path, subscription-gated). **`auditorService.saveAuditLog`** (comments). Subscription/tags via **`subscriptionService`**. Revenue paths (**Xero invoice**, **`invoiceService`**, deadlines) exist on the service class but are commented out in the ltd-onboarding handlers. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (`Company`), `users` (`User`), `companyusers` (`CompanyUser`), `groups` (`Group`), `companyresourceusers` (`CompanyResourceUser`), `resourceallocationroles` (`ResourceAllocationRole`), `ltdmigrations` (`LtdMigration`); `invoices` (`Invoice`) referenced in service methods used for invoice flows not currently invoked by the ltd-onboarding handlers. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | OpenAPI `ltd-onboarding.yml` documents `security: sleek_auth`; actual routes use `internalServicesMiddleware` — align docs or confirm legacy spec. **`validateData`** iterates all keys in `requiredFields` including `comments`; when `comments` is omitted from the body, behaviour may still list comment-related paths as missing (verify intended). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/ltd-onboarding.js`

- **`POST /create-company`** → `insertLtdOnboardingHandler.execute`; **`PUT /create-company`** → `updateLtdOnboardingHandler.execute`; **`GET /check-company/:uen`** → `checkLtdOnboardingHandler.execute`.
- All routes: **`internalServicesMiddleware()`** (see `middlewares/internal-services.js`).

### `controllers-v2/handlers/ltd-onboarding/insert.js`

- Body validation: `user_data`, `company_data`, `company_shares` required; optional `checkoutItems`, `comments`; arrays for `xero_invoice_data`, `comments`.
- Flow: `LtdOnboardingService` → `formAndAssignCompanyUser` → `formCompanyDraft` → optional `formComments` → `createCompanyAndUserStatus` → `updateDocuments`; then `validateData(req.body)` and conditional `updateMigration` when missing fields present.
- Success: `200` `{ code: 200, message: 'Company transfer completed' }`; errors: `400`.

### `controllers-v2/handlers/ltd-onboarding/update.js`

- Same core body shape (without optional `comments` in validation schema).
- Flow: `formAndAssignCompanyUser` → `updateCompanyDraft` → `updateCompanyAndUserStatus` → `updateDocuments`; if `companyData.sendAccountingInvite`, `updateAccountingQuestionnaire`; then `validateData` / `updateMigration` when gaps exist.
- Success: `200` `{ message: "Company update completed.", code: 200 }`.

### `controllers-v2/handlers/ltd-onboarding/check.js`

- Validates `req.params.uen`; `checkCompany(uen)` returns boolean; response `message` is that boolean per handler.

### `controllers-v2/handlers/ltd-onboarding/utils/validate.js`

- **`requiredFields`**: `user_data`, `company_shares` (per-shareholder fields including nested `address.*`, share economics), `company_data` (UEN, incorporation, risk, addresses, business operation address, `docKey`, etc.), `comments` (`first_name`, `comment`).
- **`validateData`**: flattened missing path list returned as array; used to populate **`ltdmigrations.missing_fields`** when non-empty.

### `services/ltd-onboarding-service.js` (class `LtdOnboardingService`)

- **User**: `checkExistingUser`, `createNewUser` via `/users-invite`, password generation, `formAndAssignCompanyUser` with `loginKeep` for new users.
- **Company**: `createDraftCompany` / `updateDraftCompany` calling **`/v2/company/insert/`** and **`/v2/company/update/`**; `formCompanyDraft` sets migration marker `is_migrated_from` `UK_MIGRATION_YYYYMMDD`; `updateCompanyIdentifiers` (CH auth code, risk rating); transfer vs incorporation branching in `createCompanyAndUserStatus` (`markCompanyLive` vs `updateCompanyStatus`).
- **Officers / shares**: `updateOfficerDetails`, `clearOfficerDetails`, `addSignificantControllers`, `addSleekSecretaries`, `addCorporateSecretary` (feature-flagged), `addCorporateDirector`; KYC flags via `updateKycStatus` (`send_sumsub_invite`). `updateShares` posts to company-shares microservice when no existing shares.
- **Migration**: `updateMigration` → `LtdMigration.findOneAndUpdate` upsert by `company_id` with `uen`, `admin_email`, `doc_key`, `renewal_date`, `onboarding_migrated`, `missing_fields`.
- **Documents**: `updateDocuments` → Companies House document by `docKey`, PDF split/upload under secretary folder **"A - Incorporation Documents"`** with template names from `UK_INCORPORATION_WORKFLOW.DOCUMENT_TEMPLATE_NAME`.
- **Accounting**: `updateAccountingQuestionnaire` (PUT path), `updateAccountingDetails` when `isAccountingActive`.
- **`checkCompany`**: `Company.findOne({ uen })` truthiness.

### `schemas/ltd-onboarding/ltd-onboarding-migration.js`

- Model **`ltdmigrations`**: `company_id`, `uen`, `admin_email`, `doc_key`, `renewal_date`, `onboarding_migrated`, `missing_fields` (array), timestamps.

### `public/api-docs/ltd-onboarding.yml`

- Describes **`GET .../check-company/{uen}`**, **`POST`/`PUT` .../create-company** with example payloads; security stanza **`sleek_auth`** (differs from implementation middleware).
