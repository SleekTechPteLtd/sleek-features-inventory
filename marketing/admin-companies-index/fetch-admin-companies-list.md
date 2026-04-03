# Fetch admin companies list

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Fetch admin companies list |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Staff can load a page of companies from the admin API with server-side filtering, sorting, and offset pagination so the directory stays usable at scale. |
| **Entry Point / Surface** | Sleek Admin > Companies (`/admin/companies/`); list loads on mount and on filter/sort/page/search changes |
| **Short Description** | `AdminCompaniesView` calls `api.getCompanies` with `admin: true`, which resolves to `GET {API base}/admin/companies` with query parameters for status, sub-status, client/company/record types, ACRA filters (SG), `sortBy`, `sortOrder`, `skip` derived from page and `perPage`, plus name, UEN, and email search fields. The response supplies `data.companies` and `data.count` to render the table and compute `maxPage`. |
| **Variants / Markets** | SG (ACRA query params when UI exposes those filters); listing behaviour otherwise shared — tenant CMS/config affects filter options, not the fetch contract itself |
| **Dependencies / Related Flows** | `api.getCompanies` / `getResource` (`admin` prefix); Sleek main API companies list endpoint (backend not in sleek-website); `getUser` on same page for session; related: multi-criteria filters, URL query sync (`st`, `sst`, etc.) |
| **Service / Repository** | sleek-website; Sleek API (companies service) |
| **DB - Collections** | Unknown (persistence in backend API) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/index.js` (`AdminCompaniesView`)

- **Load on mount**: `componentDidMount` loads platform config, then `getUser()` and `getCompanies()` (lines 604–608).
- **Request assembly**: `getCompanies` copies filter/sort/pagination state from `this.state`, normalises “Any” / empty selections to `null` where appropriate, then sets `options.query` to `status`, `sub_status`, `clientType`, `company_type`, `record_type`, `acra_non_compliant`, `acra_statuses`, `sortBy`, `sortOrder`, `skip: (page - 1) * perPage`, `name`, `uen`, `email`, `emailType` (user search mode: User Email / Allocated Users / Customer Name). Sets `options.admin = true` and calls `api.getCompanies(options)` (lines 659–715).
- **Response handling**: On success, reads `response.data.companies` and `response.data.count`, sets `maxPage` via `Math.ceil(count / perPage)` (lines 710–714).
- **Pagination**: `perPage` 20; `page` state with prev/next and direct input; `handleChangePage`, `handleClickPrevPage`, `handleClickNextPage` update `page` and call `getCompanies` (lines 723–737).
- **Sorting**: `handleClickTableHeader` toggles `sortBy` / `sortOrder` (1 or −1) for columns `name`, `updatedAt`, `createdAt` (lines 949–956, 542–586).
- **Debounced refetch**: `getCompaniesDebounced` (800 ms) used for name/UEN filters and email search flow to limit API churn (lines 60, 959–986).
- **Default `is_shareholder`**: Not set in this view; `api.getCompanies` defaults `query.is_shareholder` to `false` when omitted (see `api.js`).

### `src/utils/api.js`

- **`getCompanies`**: Builds `GET ${getBaseUrl()}/companies` and passes through `getResource`, which when `options.admin === true` rewrites the path to `${getBaseUrl()}/admin/companies` before appending the serialised query string (lines 131–144, 377–382).
- **`getResource`**: Adds default headers; `handleResponse` parses JSON and enforces auth via `checkResponseIfAuthorized` (lines 95–128, 131–144).
