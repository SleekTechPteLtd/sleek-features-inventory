# Browse and filter admin companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Browse and filter admin companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations and support staff (Sleek Admin / admin users with companies directory access) |
| **Business Outcome** | Staff can search, narrow by lifecycle and compliance dimensions, and paginate the company directory to find the right accounts for operations or support. |
| **Entry Point / Surface** | **sleek-website** admin: **Companies** (`/admin/companies/`) — `AdminLayout` sidebar `companies`; breadcrumbs “Companies”. |
| **Short Description** | Presents a paginated company table with debounced search (user email, allocated users when enabled, or customer name), column filters for name and business registration number, multi-select toolbar filters for status and sub-status, optional client and company types (CMS flags), record type (client / internal / test), and for Singapore tenant only ACRA non-compliance and ACRA company status. Sort by name, updated date, or created date. Filter state syncs to the URL (`st`, `sst`, `ct`, `cot`, `rt`, `ac`, `as`). Data loads via `GET /admin/companies`. Rows link to company overview or edit (feature flags) and allow opening the customer dashboard with a single-use token. |
| **Variants / Markets** | Multi-tenant via `platformConfig.tenant` and CMS (`COMPANY_STATUSES`, `MAPS_CONSTANTS`, `companies.filters`). **SG**: ACRA filter rows when `tenant === "sg"`. Typical Sleek markets **SG, HK, UK, AU**; exact labels per tenant CMS — use **Unknown** for unconfirmed tenants. |
| **Dependencies / Related Flows** | **`api.getCompanies`** with `admin: true` → main API `GET /admin/companies` (RBAC `companies` read; non–Sleek Admin scoped via `CompanyUser`). **SG**: backend may use corporate registry / ACRA-related filtering (see sleek-back admin company controller). **`getPlatformConfig`**, **`getUser`** (session; unverified users sent to `/verify/`). **`getAuthenticationTokenForDashboard`** for “View dashboard”. **`CreateDraftCompanyButton`** (draft company creation). Related inventory: fetch list, multi-criteria filters, company overview/edit, dashboard SUT. |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/index.js`, `src/utils/api.js` (`getCompanies`, `getUser`, `getAuthenticationTokenForDashboard`, `getPlatformConfig` via `config-loader`). **sleek-back** (not in this repo): admin companies controller and company service for list/count/sanitize. |
| **DB - Collections** | **MongoDB** (backend admin list path; not in sleek-website): `Company` (find + count; populate as implemented); `CompanyUser` / `User` for membership-scoped or email search branches; `File` where populated — **Unknown** exact pipeline without current sleek-back file read; prior inventory cited `controllers/admin/company-controller.js`. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `limit` is only enforced server-side (frontend `perPage: 20`, `skip` in query; `limit` not set in view). Whether column sets differ by tenant beyond SG ACRA toolbar. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/index.js` (`AdminCompaniesView`)

- **Mount**: `domready` renders into `#root`; `sidebarActiveMenuItemKey="companies"`.
- **State / URL**: Constructor reads `st`, `sst`, `ct`, `cot`, `rt`, `ac`, `as` from `querystring`; initial page size 20; `getCompaniesDebounced` = `debounce(getCompanies, 800)`.
- **Config**: `componentDidMount`: `getPlatformConfig()` then `getUser()` and `getCompanies()`.
- **Toolbar**: Status / sub-status from `COMPANY_STATUSES`, `COMPANY_SUB_STATUSES`, `company_sub_statuses.enabled`; company types from `COMPANY_TYPE`; client type from `CLIENT_TYPE`; record types `RECORD_TYPE_OPTIONS`. **`tenant == "sg"`**: `ACRA_NON_COMPLIANT_FILTERS`, `ACRA_COMPANY_STATUSES` from `MAPS_CONSTANTS`.
- **Flags**: `getCompanyClientType` / `getCompanyType` — `cmsAppFeatures.companies.filters` (`client_type_enabled`, `company_type_enabled`). `getResourceAllocation` — optional “Allocated Users” search mode.
- **`getCompanies`**: Builds `options.query`: `status`, `sub_status`, `clientType`, `company_type`, `record_type`, `acra_non_compliant`, `acra_statuses`, `sortBy`, `sortOrder`, `skip: (page - 1) * perPage`, `name`, `uen`, `email`, `emailType`; `options.admin = true`; `api.getCompanies(options)`; sets `companies`, `maxPage` from `count`.
- **Sort**: `handleClickTableHeader` — `name`, `updatedAt`, `createdAt` with toggling `sortOrder`.
- **Search**: `handleChangeNameFilter` / `handleChangeUenFilter` / email search + `handleClickSearch` / Enter; `onUserTypeChange` for User Email vs Allocated Users vs Customer Name.
- **Pagination**: Prev/next, direct page input, `maxPage`.
- **Table**: Status tags, name link `getCompanyOverviewUrl`, UEN, `is_clean`, transfer, client MS/SK vs updated date, record type tag, created date; dashboard + edit actions.
- **Dashboard**: `handleViewDashboardClick` → `getAuthenticationTokenForDashboard` + `getCustomerWebsiteUrl` + `getCompanyDashboardUrl`.
- **URL sync**: `select*` handlers call `window.history.replaceState` with filter query segments.

### `src/utils/api.js`

- **`getCompanies`**: `GET` `` `${getBaseUrl()}/companies` ``; defaults `query.is_shareholder` to `false` if unset (line 377–380).
- **`getResource`**: When `options.admin === true`, rewrites base URL path to include `/admin` → **`GET /admin/companies`** with serialised query (lines 131–144).

### `src/views/admin/companies/checkbox-multiselect/checkbox-multiselect.js`

- Multi-select and nested sub-options for status + sub-status when `subOptionEnabled`.

### Backend (cross-repo, cited for DB/RBAC)

- **sleek-back** `GET /admin/companies`: auth middleware, `companies` read permission, query validation including ACRA-related params where applicable; response shape `{ companies, count }`. Exact collection names and queries live in that service.
