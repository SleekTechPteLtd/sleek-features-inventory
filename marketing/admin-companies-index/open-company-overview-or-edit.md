# Admin company overview routing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Admin company overview routing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Ensures admins land on the intended company detail surface (legacy edit vs new overview) as controlled by CMS rollout flags. |
| **Entry Point / Surface** | Sleek Admin > Companies — company name link, Edit button, and related list actions |
| **Short Description** | The admin companies list loads platform config from CMS and renders a searchable, filterable table. Links that open a company use `getCompanyOverviewUrl`, which chooses `/admin/company-overview/?cid=` when `companies.overview.new_ui` is enabled and `auto_redirect` is true; otherwise `/admin/companies/edit/?cid=`. Additional CMS flags toggle filters (client type, company type, resource allocation search, ACRA filters for SG), labels, and SSIC hints. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | CMS `cmsAppFeatures` / `cmsGeneralFeatureList` via `getPlatformConfig`; `api.getCompanies` (admin list), `api.getUser`, `api.getAuthenticationTokenForDashboard` (open customer dashboard in new tab); downstream routes `/admin/company-overview/`, `/admin/companies/edit/`, `/dashboard/` (customer site). |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact market rollout per tenant is config-driven; backend persistence for companies is not visible in this view-only file. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Entry / layout**: `src/views/admin/companies/index.js` — `AdminCompaniesView` mounts on `#root`, uses `AdminLayout` with `sidebarActiveMenuItemKey="companies"`, loads `platformConfig` in `componentDidMount` via `getPlatformConfig()`.
- **Overview vs edit routing**: `getCompanyOverviewUrl(company)` reads `cmsAppFeatures` → `companies` → `overview` → `new_ui`: if `new_ui.enabled` and `new_ui.value.auto_redirect`, href is `/admin/company-overview/?cid=${company._id}`; else `/admin/companies/edit/?cid=${company._id}`. Used by the company name `<a>` and the Edit `AnchorButton` (`href={this.getCompanyOverviewUrl(company)}`).
- **Other CMS-gated UI**: `getResourceAllocation` → `companies.edit.resource_allocation.enabled` controls “Allocated Users” search option; `getCompanyClientType` / `getCompanyType` → `companies.filters.client_type_enabled` / `company_type_enabled`; `company_meta` for SSIC flag column; `admin_constants` / `MAPS_CONSTANTS` for status and SG ACRA filters; `tenant == "sg"` gates ACRA filter rows.
- **API calls**: `api.getCompanies` with `admin: true` and rich query object; `api.getUser` (redirect to `/verify/` if unverified); `handleViewDashboardClick` → `api.getAuthenticationTokenForDashboard` then opens customer site dashboard URL with `sut`.
- **Helpers**: `getAppFeatureProp` from `src/utils/app-feature-utils.js` (lodash `find` on feature prop arrays by `name`).
