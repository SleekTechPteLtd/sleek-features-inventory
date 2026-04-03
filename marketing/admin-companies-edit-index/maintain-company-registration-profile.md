# Maintain company registration profile

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Maintain company registration profile |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operations and support staff (Sleek Admin users with access to company edit) |
| **Business Outcome** | Incorporated company legal identity, registered addresses, industry classification (natures of business), identifiers, and related metadata stay accurate in Sleek so client-facing and compliance-facing records align with registry and internal policy. |
| **Entry Point / Surface** | **sleek-website** admin: **Company edit** (`/admin/companies/edit/?cid=<companyId>`), `AdminLayout` with sidebar context; CMS may auto-redirect to **Company overview** (`/admin/company-overview/?cid=…`) when `companies.overview.new_ui` is enabled. Deep links from workflows, subscriptions, invoices, and dashboard use the same `cid` query pattern. |
| **Short Description** | Loads a single company with `admin: true`, hydrates a large form (legal name, former names, UEN / business registration number, company type, natures of business primary/secondary, financial year, incorporation and appointment dates, full address block including district and premise-related fields, exempt / clean flags, and status). Staff save via **`editCompany`** (core profile) and separate actions for **lifecycle status** (`changeCompanyStatus` with optional client notification and onboarding bypass side effects) and **data-quality flag** `is_clean` (`changeCompanyIsClean`). The same page composes many sub-features—officers, share capital, subscriptions, wallet, KYC, receipts users, corpsec deadlines—via local imports and shared `updateCompanyUsers` refresh. |
| **Variants / Markets** | Multi-tenant via `getPlatformConfig` / CMS (`company_types`, `company_meta.hasSSIC`, `corpsec`, `significant_controllers_register`, `registrable_controllers`, `designated_representatives`, `credit_balance`, `companies.edit.resource_allocation`, localization defaults). **SG** often uses SSIC-backed nature lists when enabled; address types from `getAddressTypes`. Typical Sleek markets **SG, HK, UK, AU**; exact toggles per tenant CMS — use **Unknown** for unconfirmed tenants. |
| **Dependencies / Related Flows** | **`api.getCompany`**, **`api.editCompany`**, **`api.changeCompanyStatus`**, **`api.changeCompanyIsClean`** (sleek-back admin company routes). **`api.getCompanyBusinessNature`** + `industries` when SSIC off. **Company overview** (`redirectToNewUI`) may replace this UI for navigation. **Wallet** (`api-wallet`), **WFE KYC** (`apiWfe.getKycCompanyWorkflows`), **Camunda** (`startProcess`), **Sleek Auditor** comments (`getCompanyComments` / `postCompanyComment`). Downstream: customer app status/onboarding (`postPostpaymentOnboardingBypassStatus`, `postLaunchDashboard`). Related inventory: admin companies index, company overview, subscription and billing flows. |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/edit/index.js` (orchestrator), child modules under `src/views/admin/companies/edit/*.js`, `src/utils/api.js` (`getCompany`, `editCompany`, `changeCompanyStatus`, `changeCompanyIsClean`, and many company-user / secretary / controller / share endpoints), `src/utils/api-wallet.js`, `src/utils/api-wfe.js`, `src/utils/api-sleek-auditor.js`. **sleek-back** (not in this repo): admin `Company` and `CompanyUser` HTTP handlers and persistence. |
| **DB - Collections** | **MongoDB** (backend; not defined in sleek-website): **`Company`** for legal profile, address, natures of business, status, flags; **`CompanyUser`** (and related subdocuments) for directors, shareholders, admins; **`File`** for uploads referenced by forms; other collections for subscriptions, wallet, workflows — **Unknown** exact write set without current sleek-back read. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all tenants still use this page for primary edits or only when new UI / `oldView` is forced; exact RBAC permission names on `GET/PUT /admin/companies/:id` in sleek-back. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/edit/index.js` (`AdminCompaniesEditView`)

- **Bootstrap**: `domready` → `ReactDOM.render` into `#root`; class `AdminCompaniesEditView`.
- **Company load**: `componentDidMount` → `api.getCompany(query.cid, { admin: true })` — client prepends **`/admin`** for `getResource` when `admin: true` → **`GET /admin/companies/:id`**.
- **Form seeding**: Maps `company` fields into `formValues` including `name`, `company_type`, `uen`, `business_registered_number`, `nature_of_business`, `secondary_nature_of_business_1`, `financial_year`, `incorporation_date`, `appointment_date`, nested `address.*` (`address_1`–`3`, `district`, `postal_code`, `city`, `country`, `own_address_type`, `business_activities_premise_answer`), `is_clean`, `is_exempt`, `has_only_one_member_since`, `business_name`, `partner`, status remarks, etc.
- **Industry / classification**: `companyNaturesOfBusiness` from CMS `hasSSIC` + `industries` or `buildNaturesOfBusinesses` calling **`api.getCompanyBusinessNature`** merged with static industry list.
- **Core save**: `handleSubmitCompanyForm` → **`api.editCompany`** (`putResource` → **`PUT /admin/companies/:id`**) with JSON body for legal name, type, former name, proposed names, business name, UEN, BRN, primary/secondary nature of business, financial year, dates, resignation file refs, `has_only_one_member_since`, `is_exempt`, full `address` object, and `status`; then **`api.changeCompanyIsClean`** → **`POST /admin/companies/:id/change-is-clean`** with `is_clean`. On success calls `getCompany()` to refresh.
- **Status change**: `handleSubmitCompanyStatus` → **`api.changeCompanyStatus`** → **`POST /admin/companies/:id/change-status`** with `status`, `status_remarks`, `send_notification`; optional **`postPostpaymentOnboardingBypassStatus`** and **`postLaunchDashboard`** when revamped onboarding bypass CMS flags apply.
- **Refresh**: `reloadCompanyState`, `getCompany`, `updateCompanyUsers` (re-fetches `getCompanyUsers`, secretaries, controllers, payment requests, `getCompanyOfficerAppointmentDetails` via **`api.getCompanyHistory`**).
- **New UI redirect**: `redirectToNewUI` — if CMS `companies.overview.new_ui` enabled + auto_redirect, navigates to `/admin/company-overview/` unless `oldView` in non-production query.
- **Composition**: Imports `Deadlines`, `Admins`, `Directors`, `Shareholders`, `StandardUsers`, `CompanySubscriptions`, `CompanySecretaries`, `CompanySignificantControllers`, `CompanyRegistrableControllers`, `DesignatedRepresentatives`, `CompanySleekSecretary`, `CompanyShares`, accounting onboarding/receipt/dashboard user panels, KYC and 2FA components — each extends the same company record context.

### `src/utils/api.js`

- **`getCompany`**: `GET ${base}/companies/:id` (→ `/admin/companies/:id` when `options.admin === true`).
- **`editCompany`**: `PUT ${base}/companies/:id` (→ **`PUT /admin/companies/:id`** with admin flag).
- **`changeCompanyStatus`**: `POST ${base}/companies/:id/change-status`.
- **`changeCompanyIsClean`**: `POST ${base}/companies/:id/change-is-clean`.

### Webpack / page

- `webpack/paths.js`: entry `admin/companies/edit/index` → `./src/views/admin/companies/edit/index.js`.
