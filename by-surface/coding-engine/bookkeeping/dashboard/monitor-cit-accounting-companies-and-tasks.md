# Monitor CIT accounting companies and computation work

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Monitor CIT accounting companies and computation work |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (CIT operators); authenticated via app auth (`useAuth` — user email used when starting flows and deletions) |
| **Business Outcome** | Operators see all Corporate Income Tax computation work in one place with deadlines and ownership so they can triage, open a case, or start a new year’s computation for a client. |
| **Entry Point / Surface** | Sleek CIT UI → **Dashboard** (`/dashboard`; homepage per `app-constants` `HOMEPAGE`) |
| **Short Description** | Lists accounting companies with active CIT flows: search and page the list, multi-column sort (status, task step, client, form/YA, assignee, plan type, deadline), row navigation into the computation workspace, optional row actions (open company in Sleek Admin, delete workflow). Separate controls filter company by name, pick year of assessment, and **Start Tax Computation** when no flow exists. |
| **Variants / Markets** | **SG** (CIT, YA, Form C-S / form types in `FORM_TYPE_TITLE`, IRAS-oriented copy); other markets not evidenced in these files |
| **Dependencies / Related Flows** | Backend REST: **`GET /accounting-companies`** (list/search/sort/paginate), **`GET /company-details/filter-by-name/:name`**, **`GET /accounting-companies/:companyId/:ya`**, **`POST /accounting-flow/start/:companyId/:ya`**, **`POST /accounting-flow/delete/:companyId/:ya`**; **Sleek Admin** company overview (`getConfigUrl` → `admin/company-overview/?cid=…`); **Computation** detail route `/computation/:companyId/:ya`; ledger hint from company (`xero` vs `sb`) when starting a flow |
| **Service / Repository** | sleek-cit-ui (this capability); backend API unspecified in-repo |
| **DB - Collections** | Unknown (persistence in backend services; not visible from these UI files) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend models and collections for `accounting-companies` and `accounting-flow`; whether non-SG markets share this dashboard |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/components/dashboard/index.js`

- **`getDashBoardListing`**: `GET` ``/accounting-companies?search=…&page=…&limit=…&sortBy=…&sortOrder=…`` — populates table rows and `total` for paging.
- **Search**: text field + Enter / search icon triggers listing with current `searchString`.
- **Sort**: `sortBy` / `sortOrder` state; `useEffect` refetches when they change (driven by `DashboardTable` via `handleSortSelection`).
- **Paging**: `page`, `pageLimit` (10–100), `CustomPager` `onPageChange` → `getDashBoardListing(pageNo, searchString)`.
- **Company + YA pickers**: debounced `GET` `/company-details/filter-by-name/${encodeURIComponent(name)}`; YA options derived from `moment` vs `incorporation_date` / `current_fye` / `financial_year` (`checkYAOptions`).
- **Start Tax Computation**: `GET` `/accounting-companies/${selectedCompany._id}/${selectedYA}` — if empty, `POST` `/accounting-flow/start/${id}/${ya}` with `userId` (email), `ledger` `xero` or `sb` from `accounting_tools.accountingLedger`; else modal with link to existing computation; errors surface BQ/Xero messaging.
- **Modal**: warns if financial year missing in Admin (`handleSelectedYa`); optional `accounting_plan_error_message` from start response.

### `src/components/dashboard/dashboard-table.js`

- **Columns**: Status (`getTaskStatus` + `CustomStepIcon`, `TASK_STATUS_*` from `utils/constants`), Task (`getTaskType` / `TASK_TYPE`, legacy step mapping), Client (`name`), Form (YA) (`getFormType` / `FORM_TYPE_TITLE` + `year_of_assessment`), Assignee (`assignee_name`), Plan type (`plan_type`), Deadline (`computeDeadline` from `end_date`, `year_of_assessment`, `last_step` — Nov 30 rule when `last_step >= 6`, else FYE + 3 months rule).
- **Sort**: `SortColumn` + `onClickSortOrders` builds comma-separated `sortBy` / `sortOrder` for parent (`status`, `task`, `client`, `task_type`, `assignee`, `plan_type`, `deadline`).
- **Row click** (most cells): `navigate` to `/computation/${company_id}/${ya}?uen=…` (`handleNav`).
- **Overflow menu**: **Company Information** → new tab to Admin `company-overview/?cid=${company_id}`; **Delete Workflow** → confirm modal → `POST` `/accounting-flow/delete/${company_id}/${year_of_assessment}` with `startDate`, `endDate`, `userId`; then `getLatestDashboardData()`.

### `src/components/dashboard/custom-pager.js`

- **UI**: “Showing X to Y of Z entries”, prev/next, clickable page numbers; `pageNumbers = ceil(total / limit)`.

### `src/pages.js`

- Route **`url: "/dashboard"`** → `Dashboard` component.

### `src/commons/constants/app-constants.js`

- **`HOMEPAGE: "/dashboard"`** — default landing for the app.
