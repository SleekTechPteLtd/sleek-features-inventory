# Manage tax registration and share capital

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage tax registration and share capital |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek Admin user with company overview access and edit rights) |
| **Business Outcome** | Client company tax-registration posture (Australian ABN / GST / PAYGW / FBT) and share-class / cap-table style records stay accurate in Sleek for compliance, filings, and internal operations. |
| **Entry Point / Surface** | **sleek-website** admin **Company overview**: `/admin/company-overview/?cid=<companyId>` (`webpack/paths.js` entry `admin/company-overview/index`). **Tax** tab renders `TaxRegistration` when `PAGES.TAX` is active and data is loaded. **Shares** tab renders `CompanySharesComponent` or `CompanySharesComponentNew` when `PAGES.SHARES` is active; variant chosen by CMS `company_shares_microservice.enabled`. |
| **Short Description** | **Tax:** Loads and edits **company profile** tax fields (registered services, income bands, activity statement frequency, accounting basis, payroll-related flags) via `getCompanyProfile` / `createCompanyProfile` / `updateCompanyProfile`. Labels and visibility come from CMS `company_overview_tax_tab`. **Shares:** Either the **legacy** flow (share items on `company.share_items` plus per-shareholder allocations via `createCompanyShareItems`, `updateCompanyShareItem`, `updateCompanyShares`) or the **microservice** flow (`getCompanySharesByCompanyId`, `insertCompanyShares`, `updateCompanyShare`, `deleteCompanyShare` against the company-roles service), including trust-style shareholders via `COMPANY_USER_ROLES` in the new component. |
| **Variants / Markets** | Tax UI is **Australian** (ABN, GST, PAYGW, FBT). Share flows are multi-tenant; exact markets per company/CMS — **SG, HK, UK, AU** plausible; use **Unknown** where tenant mapping is not confirmed in this repo. |
| **Dependencies / Related Flows** | **Tax:** Subscription gating uses `validateTaxRegistrationSubscription` and CMS `TAX_REGISTRATION_SERVICES` (`admin_constants`). **Shares:** Parent `AdminCompanyOverview` supplies `company`, `companyUsers`, dialogs/alerts; legacy path ties to `getCompany` / `company.share_items` and `updateCompanyShares` batch update. **Related:** Company overview **Company info**, **People**, subscriptions, accounting tabs; backend **sleek-back** / **company-roles** APIs (not in this repo). |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/tax-registration.js`, `src/views/admin/company-overview/components/CompanySharesComponent.js`, `CompanySharesComponentNew.js`, orchestration in `src/views/admin/company-overview/index.js`, `src/utils/api.js` (`getCompanyProfile`, `createCompanyProfile`, `updateCompanyProfile`, `createCompanyShareItems`, `updateCompanyShareItem`, `updateCompanyShares`, `insertCompanyShares`, `getCompanySharesByCompanyId`, `updateCompanyShare`, `deleteCompanyShare`). |
| **DB - Collections** | **Unknown** in this repo. Evidence suggests documents for **company profile** (tax nested under profile) and **share items** / **shareholder share** links; microservice path uses **company-shares** HTTP resources — exact Mongo collection names require backend read. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC on company profile and share endpoints; Mongo collection names; full list of tenants where `company_shares_microservice` is enabled vs legacy; whether tax tab is shown only when `hasTaxRegistrationSubscription` / related state gates (see parent) apply in all environments. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-overview/tax-registration.js` (`TaxRegistration`)

- **Data:** `getCompanyProfile(company._id)` seeds `tax.registered_services` (abn, gst, paygw, fbt), `first_business`, `expected_annual_income`, GST and PAYGW follow-up fields, etc.
- **Save:** Builds `{ company, tax: { registered_services, … } }` and calls **`updateCompanyProfile(companyId, profileId, …)`** or **`createCompanyProfile(companyId, …)`** if no profile id.
- **UI:** Four cards — ABN, GST, PAYGW, FBT — with CMS-driven copy from `platformConfig.cmsAppFeatures` → `company_overview_tax_tab` (`abn_registration_labels`, `gst_registration_labels`, `paygw_registration_labels`, `fbt_registration_labels`). Conditional clears when toggling registrations off (`setDefaultValueForNoAnswer`).
- **Validation:** Integer check on `employee_count` for PAYGW.

### `src/views/admin/company-overview/components/CompanySharesComponent.js`

- **Legacy UI:** Wraps `CompanyShares` list and `CompanyShareForm` from `views/companies/edit/company-shares` and `components/company-share-form`; **Add Share Class**, edit/remove callbacks passed from parent (`index.js`). Respects `isEnhanceShareAllocationEnabled` and `paidUpShareCapitalInputIsVisible`.

### `src/views/admin/company-overview/components/CompanySharesComponentNew.js`

- **Microservice:** `useEffect` → **`getCompanySharesByCompanyId(company._id)`**. Submit builds `shares` array per shareholder (including `company_user_role` for trust roles) and calls **`insertCompanyShares`** or **`updateCompanyShare`**. Remove confirms then **`deleteCompanyShare`**. Uses `CompanySharesTable` / `CompanySharesForm` from `@/components/company-shares/*`.

### `src/views/admin/company-overview/index.js`

- **Tabs:** `isCurrentPage(PAGES.TAX)` → `TaxRegistration`; `isCurrentPage(PAGES.SHARES)` → `getCompanySharesComponentPerTenant()` (switches on `company_shares_microservice.enabled`).
- **Tax subscription:** `validateTaxRegistrationSubscription` compares subscriptions to **`TAX_REGISTRATION_SERVICES`** and allowed statuses from **`MAPS_CONSTANTS`**.

### `src/utils/api.js`

- **Company profile:** `GET|POST ${base}/companies/:companyId/company-profile`, `PUT …/company-profile/:companyProfileId`; **`getCompanyProfileHistory`** available for audit (not used in these three files).
- **Legacy shares:** `POST ${base}/companies/:companyId/share-items`, `PUT …/share-items/:shareItemId`, `PUT ${base}/companies/:companyId/shares`.
- **Microservice shares:** `getCompanyRolesServiceBaseUrl()` → `GET|POST|PATCH|DELETE …/company-shares` (with `?company=` for list).
