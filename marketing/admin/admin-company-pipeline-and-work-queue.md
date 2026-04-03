# Admin company pipeline and work queue

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Admin company pipeline and work queue |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (Sleek Admin users with access to the admin home and companies flows) |
| **Business Outcome** | Staff see draft, processing, and live company volumes at a glance, then browse or narrow the home work list to open corporate secretarial (incorporation/transfer) workflows and see where each company sits in the pipeline. |
| **Entry Point / Surface** | **sleek-website** admin: **Home** — webpack entry `admin` (`src/views/admin/home.js`); `AdminLayout` with `sidebarActiveMenuItemKey="home"` and drawer hidden on this screen. Summary stats link to **Companies** (`/admin/companies/`). |
| **Short Description** | Loads aggregate company counts via admin stats API and renders **CompaniesSummaryStats** (Draft / Processing / Live). Below that, **AdminDashboard** lists companies with pagination, optional **CompanyLookup** name search, and a status dropdown (`COMPANY_STATUSES`). Each row shows **CSWorkflowButton**: link to the current corpsec workflow task, start incorporation or transfer when no instance exists (CMS `workflow.enabled`), or “Workflow complete” when all tasks are done. Toolbar includes **Export Event History** (admin companies export). Optional CMS redirect can send users away from home entirely (`enable_admin_home_redirect`). |
| **Variants / Markets** | **Unknown** for stats breakdown by tenant from this repo; company list and workflow behaviour depend on `platformConfig` and company `status` / `cs_workflow_instance` (multi-market via backend). |
| **Dependencies / Related Flows** | **`api.getStats({ admin: true })`** → **`GET /admin/companies/get-stats`** (response fields merged into state: `draftCount`, `liveCount`, `processingBySleekCount`, `referredToAcraCount`, `paidAndIncompleteCount`, `companiesCount`). **`api.getCompanies`** with `admin: true` → **`GET /admin/companies`** (paginated queue: `skip`, `limit`, `sortBy`/`sortOrder`, optional `name`, `status`). **`api.createWorkflowInstance`** → **`POST /admin/workflow-instances/instantiate`** with `companyId`. **`getCurrentTask` / `getWorkflowIsComplete`** (`corpsec/my-tasks/utils`) from workflow presentation sections. **`getPlatformConfig`**, **`getAppFeatureProp`** for workflow feature flag. Related: full **Companies** directory ([browse/filter companies](../admin-companies-index/browse-filter-admin-companies.md)), **`/admin/workflow/`** UI. **`api.getRequestInstances`** loads request count for header area (paired with home mount). |
| **Service / Repository** | **sleek-website**: `src/views/admin/home.js`, `src/views/admin/dashboard/index.js`, `src/views/admin/workflow/cs-workflow-button.js`, `src/views/admin/components/company-lookup.js`, `src/layouts/new-admin.js`, `src/utils/api.js` (`getStats`, `getCompanies`, `createWorkflowInstance`, `getUser`, `getRequestInstances`), `src/views/admin/corpsec/my-tasks/utils.js`. **sleek-back** (not in this repo): stats aggregation, company list, workflow instantiation. |
| **DB - Collections** | **MongoDB** (backend only; not visible in sleek-website): **Unknown** exact collections for `get-stats` and list — likely `Company` and workflow-related documents populated on company (`cs_workflow_instance`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `get-stats` permissions differ from full companies list. Whether home queue is intended to mirror a specific corpsec backlog or generic recent companies. Pagination “next” is disabled when `companies.length < 20` (may not match true last page if count is exact multiple of 20). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/home.js` (`AdminHomeView`)

- **Mount**: `domready` → `#root`; **`sidebarActiveMenuItemKey="home"`**, **`hideDrawer={true}`**.
- **State**: `companiesCount`, `draftCount`, `paidAndIncompleteCount`, `processingBySleekCount`, `referredToAcraCount`, `liveCount` (populated from stats API).
- **`componentDidMount`**: `getPlatformConfig()`; optional redirect via CMS `optional_redirects` / `enable_admin_home_redirect` → `admin_home_page`; else `getUser()`, `getRequestsCount()`, `getStats()`.
- **`getStats`**: `api.getStats({ admin: true })` → `setState(response.data)`.
- **`getUser`**: unverified users → `/verify/`.
- **Body**: `AdminDashboard` receives `statistics` object with draft / processing (sum of `paidAndIncompleteCount` + `processingBySleekCount` + `referredToAcraCount`) / live counts.
- **`renderStats`**: Present in file but **not** used in `renderBodyContent` (dashboard uses `CompaniesSummaryStats` instead).
- **Primary toolbar**: “Export Event History” → `downloadFile` to `${base}/admin/companies/export-event-history`.

### `src/views/admin/dashboard/index.js` (`AdminDashboard`, `CompaniesSummaryStats`)

- **`CompaniesSummaryStats`**: Same three-segment card as home stats; links to `/admin/companies/`.
- **`getCompanies`**: `options.admin = true`; query `skip`, `limit` (perPage 20), `sortBy: "createdAt"`, `sortOrder: "desc"`; optional `name` from `companyFilter`, `status` from `companyStatus`.
- **Filters**: Status `<select>` with “Any” + `COMPANY_STATUSES`; **`CompanyLookup`** `onChange` → `handleCompanyFilterChange` → filters by name.
- **Table**: Company name, **`<CSWorkflowButton />`**, title-cased `company.status`.

### `src/views/admin/workflow/cs-workflow-button.js` (`CSWorkflowButton`)

- **Striked off**: renders nothing.
- **Existing `cs_workflow_instance`**: If workflow complete → link “Workflow complete”. If `status === "live"` → “Go to Incorporation” button linking to `/admin/workflow/?instanceId=…&taskId=…`. Else → task name link with same URL pattern.
- **No workflow**: Returns null for `live`, `partner_draft`, `partner_paid`. If CMS `workflow.enabled`, shows “Start Incorporation” or “Start Transfer” (`is_transfer`) → confirmation dialog → **`api.createWorkflowInstance`** body `{ companyId }` → opens `/admin/workflow/?instanceId=…` in new tab; errors via `handleErrorResponseWorkflow`.

### `src/views/admin/components/company-lookup.js` (`CompanyLookup`)

- **`getCompanies`**: `api.getCompanies` with `query.name`, optional `status` from `arrayOfCompanyStatus`, `limit` default 15, `admin: true`.
- **Select**: Blueprint `Select`, `onQueryChange` triggers search; **`onChange(company.name, company._id, company.partner)`** to parent (dashboard uses name-only filter).

### `src/layouts/new-admin.js` (`AdminLayout`)

- **Gate**: Renders “You don't have access” if `user.profile !== "admin"`.
- **Home exception**: `checkUserAccess` **returns early** if `sidebarActiveMenuItemKey === "home"` — so permission keys for other menu items are **not** enforced on home; other admin routes redirect to `/admin/` when permission missing.
- **Sidebar**: `AdminSideMenu` with `disabledMenuItemKeys` from `ADMIN_RESOURCES` vs `user.permissions`.

### `src/utils/api.js`

- **`getStats`**: `GET ${base}/companies/get-stats` → with `admin: true`, path becomes **`${base}/admin/companies/get-stats`**.
- **`createWorkflowInstance`**: **`POST ${base}/admin/workflow-instances/instantiate`**.

### `src/views/admin/corpsec/my-tasks/utils.js`

- **`getCurrentTask`**: First task with `status === "available"` in flattened `cs_workflow_instance.presentation.sections` tasks.
- **`getWorkflowIsComplete`**: completed task count equals total task count.
