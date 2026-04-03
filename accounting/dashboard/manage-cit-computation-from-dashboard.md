# Manage CIT computation from dashboard

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage CIT computation from dashboard |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Tax operations staff can list in-flight CIT workflows, start a new computation for a chosen company and year of assessment, open an existing run, remove a workflow, or jump to the company in Sleek Admin—without leaving the CIT dashboard surface. |
| **Entry Point / Surface** | Sleek CIT App > **Dashboard** (`/dashboard`; homepage per `app-constants` `HOMEPAGE`). |
| **Short Description** | The dashboard loads paginated, sortable accounting company / flow rows, supports search and filters to pick a company and YA, validates financial-year setup before starting work, posts to start or detect duplicate flows (with ledger choice Xero vs SleekBooks), and links rows to the computation route. Row actions open Sleek Admin company overview or delete a workflow after confirmation. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **Downstream**: CIT computation wizard at `/computation/:companyId/:yearOfAssessment` (and optional `uen` query). **External**: Sleek Admin `company-overview` (URL from `getConfigUrl()` + `/admin/company-overview/?cid=…`). **APIs (backend)**: `GET /accounting-companies`, `GET /company-details/filter-by-name/:name`, `GET /accounting-companies/:id/:ya`, `POST /accounting-flow/start/:id/:ya`, `POST /accounting-flow/delete/:companyId/:ya`. **Auth**: `useAuth` (`currentLoggedInuser.email` on start/delete). |
| **Service / Repository** | sleek-cit-ui |
| **DB - Collections** | Unknown (collections live in backend services called by this UI; not evidenced in this repo). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend service repo name and MongoDB collections for `accounting-companies` / `accounting-flow` (not in sleek-cit-ui). When company has no `incorporation_date`, YA options are not populated and UI only comments “show warning”—no user-facing message in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/pages.js`

- **Route**: `url: "/dashboard"` → `Dashboard` component (home for the CIT app).

### `src/components/dashboard/index.js`

- **`getDashBoardListing`**: `GET /accounting-companies?search=&page=&limit=&sortBy=&sortOrder=` — populates table and `total`.
- **Company search**: `GET /company-details/filter-by-name/:name` (debounced) for react-select options.
- **`checkYAOptions` / `handelSelectedCompany`**: Builds YA options for current year ±1/±2; disables YAs that violate incorporation vs financial-year-end rules (`moment` on `incorporation_date`, `financial_year`, `current_fye`).
- **`handleSelectedYa`**: If `financial_year` is missing/null, modal: *"Please add a Financial Year for 'next FYE to file' in Sleek Admin before proceeding."*
- **`startTaxComputation`**: `GET /accounting-companies/${companyId}/${ya}` — if empty, `POST /accounting-flow/start/${companyId}/${ya}` with `{ userId, ledger }` where `ledger` is `"xero"` if `accounting_tools.accountingLedger` contains `"xero"` (case-insensitive), else `"sb"`. On success navigates to `/computation/...`. If flow exists, modal with link to same path. On `accounting_plan_error_message`, shows warning modal; **`handleClose`** navigates to computation when `accountingPlanError` is set. Catch block shows BQ/Xero UEN messaging.
- **UI**: Search, page size, company select, YA select, **Start Tax Computation** button (disabled until YA selected or while start in flight).

### `src/components/dashboard/dashboard-table.js`

- **Row click** (`handleNav`): `navigate(\`/computation/${company_id}/${ya}?uen=${DUMMY_UEN}\`)` with `ya` from `new Date(fye).getFullYear()`.
- **Sort**: `SortColumn` + `onClickSortOrders` → `handleSortSelection(sortBy, sortOrder)` (parent refetches with sort params).
- **Overflow menu**: **Company Information** — `getConfigUrl()` then `window.open` `${admin}/admin/company-overview/?cid=${company_id}`. **Delete Workflow** — opens confirm modal; **`deleteComputationalFlow`**: `POST /accounting-flow/delete/${company_id}/${year_of_assessment}` with `{ startDate, endDate, userId }`, then `getLatestDashboardData()`, toast success.
- **Display**: Task type/status via `TASK_TYPE`, `TASK_STATUS`, `TASK_TYPE_LEGACY`, `CustomStepIcon`; form label via `FORM_TYPE_TITLE`; deadline via `computeDeadline`.

### `src/components/dashboard/custom-pager.js`

- Pagination UI wired from parent `page`, `limit`, `total`, `onPageChange`.

### `src/commons/constants/app-constants.js`

- **`HOMEPAGE: "/dashboard"`** — confirms dashboard as default landing.
