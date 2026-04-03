# Multi-criteria admin company filters

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Multi-criteria admin company filters |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Admins can slice the company directory by status, sub-status, client and company type, record type, and (for Singapore) ACRA non-compliance and ACRA status so support and operations can find the right entities quickly. |
| **Entry Point / Surface** | Sleek Admin > Companies (`/admin/companies/` with query string state) |
| **Short Description** | Toolbar and table header controls combine multi-select and single-select filters. Filter choices are loaded from CMS platform config (`COMPANY_STATUSES`, `COMPANY_SUB_STATUSES`, `COMPANY_TYPE`, `CLIENT_TYPE`, record-type presets, and for tenant `sg` only `ACRA_NON_COMPLIANT_FILTERS` and `ACRA_COMPANY_STATUSES`). Changing filters updates the URL via `history.replaceState` (`st`, `sst`, `ct`, `cot`, `rt`, `ac`, `as`) and refetches companies through `api.getCompanies` with `admin: true` and the assembled query. |
| **Variants / Markets** | SG (ACRA filters shown when `platformConfig.tenant === "sg"`); client/company-type filter visibility gated by `companies.filters` feature flags; status/sub-status lists are tenant CMS-driven — HK, UK, AU, etc. as configured |
| **Dependencies / Related Flows** | `getPlatformConfig()` / `getAppFeatureProp` for CMS feature lists; `api.getCompanies` → `GET {base}/companies` with query (`status`, `sub_status`, `clientType`, `company_type`, `record_type`, `acra_non_compliant`, `acra_statuses`, pagination, sort, name/uen/email filters); backend companies listing API (not in sleek-website); shared `CheckboxMultiSelect` UI |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (company persistence lives in backend API service, not evidenced in these view files) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/index.js` (`AdminCompaniesView`)

- **Initial URL sync**: Constructor parses `querystring` from `window.location.search` into `st` (status, comma-separated), `sst` (sub-statuses), `ct`, `cot`, `rt`, `ac` (ACRA non-compliant), `as` (ACRA status), with edge cases when `Any` is combined with other params (lines 37–46, 48–58).
- **Config-driven options**: `COMPANY_STATUSES` and sub-statuses from `admin_constants` + `MAPS_CONSTANTS` / `company_sub_statuses.enabled`; `COMPANY_TYPE` from admin constants; `CLIENT_TYPE` from `../../../utils/constants`; `RECORD_TYPE_OPTIONS` local. For `tenant == "sg"`, `ACRA_NON_COMPLIANT_FILTERS` and `ACRA_COMPANY_STATUSES` from `MAPS_CONSTANTS` (lines 117–136).
- **Feature flags**: `getCompanyClientType` / `getCompanyType` read `companies.filters` (`client_type_enabled`, `company_type_enabled`) to show Client Type and Company Type blocks (lines 274–305, 637–656).
- **API payload**: `getCompanies` builds `options.query` with `status`, `sub_status`, `clientType`, `company_type`, `record_type`, `acra_non_compliant`, `acra_statuses`, plus `sortBy`, `sortOrder`, `skip`, `name`, `uen`, `email`, `emailType`; sets `options.admin = true` (lines 659–715). Invokes `api.getCompanies(options)`.
- **URL sync on change**: `selectStatusHandleChange`, `selectSubStatusHandleChange`, `selectClientTypeHandleChange`, `selectCompanyTypeHandleChange`, `selectRecordTypeHandleChange`, `selectAcraNonCompliantHandleChange`, `selectAcraStatusHandleChange` each call `window.history.replaceState` with the appropriate query segments after `setState` (lines 739–946).

### `src/views/admin/companies/checkbox-multiselect/checkbox-multiselect.js` (`CheckboxMultiSelect`)

- Reusable dropdown: toggles open state, renders options with optional nested **sub-options** when `subOptionEnabled` and status options expose `subOptions` (status + sub-status UX).
- **Props**: `options`, `values`, `selectedSubOptions`, `handleOptionChange`, `handleSubOptionChange`, `subOptionEnabled`, `placeholder`, `label`, `checkBoxStyles`.
- **Display**: Single selection shows label; multiple selections show “Multiple Selected” (lines 56–71).

### `src/utils/api.js`

- `getCompanies`: `GET ${getBaseUrl()}/companies` via `getResource`, merges query options (lines 377–382).
