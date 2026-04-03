# Operate admin onboarding dashboard

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Operate admin onboarding dashboard |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operations staff (authenticated Sleek admin users) |
| **Business Outcome** | UK operators get a single place to see Camunda UK incorporation workload by category, optionally jump to unpaid and paid incomplete order queues when product config allows, refresh Companies House status for applicants in CH, and open category-filtered company lists—including AML review—so onboarding and compliance work stays visible and actionable. |
| **Entry Point / Surface** | **sleek-website** admin: **Dashboard** — React bundle `admin/dashboard` → `src/views/admin/dashboard-v2/index.js` (webpack `paths.js`). `AdminLayout` with `sidebarActiveMenuItemKey="dashboard"`, `hideDrawer={true}`. Public path follows the `admin/dashboard` entry (typically `/admin/dashboard/` depending on site routing). |
| **Short Description** | For **GB** tenant, loads UK incorporation workflow **categories** from the API (`getUkCompanyWorkflowsCategories`), shows per-category counts and **VIEW** to drill down with `?category=…`. Optional rows for **Unpaid incomplete orders** and **Paid incomplete orders** appear only when CMS app features enable `companies.overview.props.incomplete_orders` and `paid_incomplete_orders`. Counts use admin `getCompanies` with `draft` and `paid_and_awaiting_company_detail` (GB adds `appOnboardingVersion: Beta`). For category **applicants_in_ch**, **CH UPDATE** calls `receiveCompanyHouseStatus` and surfaces an updates chip. The drill-down list posts to `getDashboardCompanies`, enriches rows with Camunda **process tasks** for KYC dates, links to company overview or legacy edit, opens **Workflow** in sleek-workflow, and **AML** opens a drawer of per-user AML statuses. |
| **Variants / Markets** | **UK (gb)** tenant: workflow categories and GB-only company query flags. **CMS** toggles gate incomplete-order shortcuts. Other tenants: workflow categories cleared; incomplete-order rows still driven by CMS. |
| **Dependencies / Related Flows** | **API (sleek-back)**: `GET /v2/sleek-workflow/uk-incorporation/categories`; `POST /admin/companies/dashboard` (via `getDashboardCompanies`); `GET /admin/companies` with filters; `GET /company-house/{id}/get-company-status` (CH refresh). **Camunda / sleek-workflow**: `GET /v2/sleek-workflow/processes/tasks` for incorporation task lists; workflow task UI at `/admin/sleek-workflow/workflow-task/`. **Platform config**: `getPlatformConfig` for tenant and `cmsAppFeatures`. Downstream: **Incomplete orders** (`/admin/incomplete-orders`), **Paid incomplete orders** (`/admin/paid-incomplete-orders`), **Company overview** or **Companies edit**. |
| **Service / Repository** | **sleek-website** (admin dashboard v2, `api.js`, `api-camunda.js`). **sleek-back** (or API host implementing the routes above; not read in this pass). |
| **DB - Collections** | Unknown (persistence is server-side; not visible from these view files). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `receiveCompanyHouseStatus(false, …)` passes boolean `false` as the path segment for `company-house/:id/get-company-status`—confirm whether this is intentional (e.g. batch or sentinel) or should be a company id. Sorting in `company-list.js` `handleClickTableHeader` assigns `sortBy` twice and compares `sortBy === sortBy` (always true), so sort toggle behaviour may not match intent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/dashboard-v2/index.js` (`Dashboard`)

- **Bootstrap**: `domready` → `ReactDOM.render` on `#root` → `AdminLayout` (`primaryToolbarContent`, `bodyContent`), `sidebarActiveMenuItemKey="dashboard"`.
- **Tenant / categories**: `getPlatformConfig()` → if `tenant === "gb"`, `getUkCompanyWorkflowsCategories()` → `setWorkflowCategories`; else empty categories.
- **CMS gates**: `getAppFeatureProp(platformConfig.cmsAppFeatures, "companies")` → `overview.props.incomplete_orders.enabled`, `paid_incomplete_orders.enabled` control row visibility.
- **Counts**: `getCompanies({ query: { status: "draft" \| "paid_and_awaiting_company_detail", removeEmptyNames: true, appOnboardingVersion: "Beta" when gb }, admin: true })` → draft / paid-awaiting counts.
- **User**: `getUser()`; unverified email redirects to `/verify/`.
- **Navigation**: Unpaid → `/admin/incomplete-orders`; Paid incomplete → `/admin/paid-incomplete-orders`; category drill-down → `?category=` + `setHideDashboard(true)` → renders `CompanyList`.
- **CH refresh**: `receiveCompanyHouseStatus(false, { admin: false, body: null })` → `setUpdatesCount` from `data.length`; chips on `applicants_in_ch` row.

### `src/views/admin/dashboard-v2/components/company-list.js` (`CompanyListFilteredByCategory`)

- **Category**: `getQueryStringValue("category")` indexes `workflowCategories[category]` for `companyIds`, labels, description.
- **Data**: `getDashboardCompanies` → `POST …/companies/dashboard` with JSON body: `sortBy`, `sortOrder`, `skip`, `ID` (company ids from category), `category`, filters (`name`, `transaction_id`, `applicant_status`, `company_aml_status`).
- **Camunda**: `getSleekWorkflowProcessTasks` with `processIds` from `incorporation_workflow.business_key` → KYC completion from task `kyc_verification`.
- **Actions**: **Workflow** → `window.open` sleek-workflow URL with `processId` and `processInstanceId`; company name → `getCompanyOverviewUrl` (CMS `new_ui` vs `/admin/companies/edit/`); **AML** → `AMLStatusDrawer`.
- **Table columns**: Category-specific headers in `TABLE_HEADER_CONFIG` (AML status, payment date, CH fields, applicant status, etc.).

### `src/views/admin/dashboard-v2/components/AMLStatusDrawer.js`

- **UI**: Material-UI `Drawer`; groups `company.company_users` by `aml_status`; labels Approved / Rejected / Pending / Resubmission; shows name, roles via `getCompanyUserRoles`, phone, email.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getUkCompanyWorkflowsCategories`**: `GET ${getBaseUrl()}/v2/sleek-workflow/uk-incorporation/categories`.
- **`getSleekWorkflowProcessTasks`**: `GET ${getBaseUrl()}/v2/sleek-workflow/processes/tasks?…` (used for process task lists).

### `src/utils/api.js`

- **`getDashboardCompanies`**: `POST ${getBaseUrl()}/companies/dashboard` with `admin: true` → `/admin/companies/dashboard`.
- **`getCompanies`**: `GET` companies with optional admin prefix.
- **`receiveCompanyHouseStatus`**: `GET ${getBaseUrl()}/company-house/${id}/get-company-status`.
- **`getUser`**: `GET …/admin/users/me`.

### Webpack

- **`webpack/paths.js`**: entry key `"admin/dashboard"` → `./src/views/admin/dashboard-v2/index.js`.
