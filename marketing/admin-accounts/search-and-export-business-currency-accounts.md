# Search and export business currency accounts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Search and export business currency accounts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin users with `permissions.business_account` of `read`, `edit`, or `full` |
| **Business Outcome** | Staff can find and review customer currency (virtual) accounts across companies and vendors, open a company’s business-account context from a row, and obtain a CSV from the bank service for oversight and reporting. |
| **Entry Point / Surface** | **sleek-website** admin: **Business Account Search** — page title in toolbar; `AdminLayout` with `sidebarActiveMenuItemKey="accounts"` (`src/views/admin/accounts/index.js`). Route is wired by the admin build to the accounts entry (same pattern as other admin views under `/admin/...`). |
| **Short Description** | After email verification and business-account permission checks, loads paginated currency accounts from the SBA bank API. Operators filter by virtual account number (debounced text) and company (async company search + select), sort by vendor, status, or date created, and change page size and page. Each row shows virtual account number, currency, vendor, company (link to company overview on the Business Account tab), styled status, and created date. A **DOWNLOAD AS CSV** action requests a file from the bank API download endpoint (button disabled when the current table has no rows or while downloading). Unverified users are sent to `/verify/`; users without the permission triplet are sent to `/admin`. |
| **Variants / Markets** | Unknown — no market dimension in this view; Sleek typically operates SG, HK, UK, AU; confirm with bank/SBA if behaviour differs by tenant. |
| **Dependencies / Related Flows** | **`getCurrencyAccounts`** → **`GET ${API_BANK_URL}/sba/v2/admin/currency-accounts`** with query `page`, `limit`, `virtualAccountNumber`, `companyId`, `orderBy`, `order` (via `business-account-utils` → `api-bank`). **`getCompanies`** → **`api.getCompanies`** (main API) for company name typeahead. **CSV** → **`view.downloadFile`** → **`api.downloadFile`** → **`GET ${getBaseUrl()}/sba/v2/admin/currency-accounts/download`** on the bank base URL (no query string in client). **Session** → **`api.getUser`** (`/admin/users/me`). **Company context** → `/admin/company-overview/?cid={company_id}&currentPage={PAGES.BUSINESS_ACCOUNT}` (`PAGES.BUSINESS_ACCOUNT` = `"Business Account"`). |
| **Service / Repository** | **sleek-website**: `src/views/admin/accounts/index.js`, `src/views/admin/accounts/components/table.js`, `src/views/admin/accounts/components/toolbar.js`, `src/utils/business-account-utils.js` (`getCurrencyAccounts`), `src/utils/api-bank.js` (`getCurrencyAccounts`, `getBaseUrl`), `src/utils/api.js` (`getUser`, `getCompanies`, `downloadFile` used by `view.downloadFile`), `src/utils/auth-utils.js` (`checkResponseIfAuthorized` on API responses). **SBA / bank backend** (not in this repo): list, pagination, and CSV export. |
| **DB - Collections** | Unknown — persistence for currency accounts lives in the bank/SBA (and related) services; sleek-website is a client only. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the CSV export applies the same filters as the on-screen list: the client calls `/sba/v2/admin/currency-accounts/download` with **no** query parameters, while the table uses `virtualAccountNumber`, `companyId`, `orderBy`, `order`, `page`, and `limit` for **`/sba/v2/admin/currency-accounts`** — confirm server behaviour (full dump vs session-scoped vs undocumented contract). Minor UI inconsistency: loading/empty row `colSpan` is 5 while the table has 6 columns. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/accounts/index.js` (`AccountList`)

- **Mount**: `domready` → `#root`; `AdminLayout` `hideDrawer`, `sidebarActiveMenuItemKey="accounts"`.
- **Permission**: `api.getUser()` → require `registered_at` or redirect `/verify/`; `permissions.business_account` ∈ `{ read, edit, full }` (`BUSINESS_ACCOUNT_PERMISSION`) else redirect `/admin`. Errors use `checkResponseIfAuthorized` from `auth-utils`.
- **State**: `table` holds `data`, `paging` (`total`, `limit`, `page`, `virtualAccountNumber`, `companyId`, `order`, `orderBy` default `desc` / `createdAt`), `loading`.
- **Query builder**: `buildCurrencyAccountsQuery` merges filter overrides with `table.paging`.
- **Data load**: `getAccounts` → `bankApi.getCurrencyAccounts({ query })` (imported as `business-account-utils`), maps `response.results` and `response.total`.
- **Companies for filter**: `getCompanies(name)` → `api.getCompanies({ query: { limit: 10, name } })`, maps to `{ label, value }` options.

### `src/views/admin/accounts/components/table.js`

- **Columns**: `virtual_account_number`, `currency_code`, `vendor_name`, `company_name`, `status`, `createdAt` (Moment `DD MMM YYYY`).
- **Sort** (server): `TableSortLabel` on `vendor_name`, `status`, `createdAt` — toggles `order`, resets to `page: 1`, first click on a new column uses `desc` when switching from another column.
- **Virtual account filter**: `react-select` with debounced 700ms `onInputChange` → `getAccounts({ page: 1, virtualAccountNumber })`; clear sets empty string.
- **Company filter**: options from `companyOptions`; `onChange` → `getAccounts({ page: 1, companyId })`; input debounced → `getCompanies`.
- **Status display**: `classNames` on `active` | `deleted` | `closed` for pill styling.
- **Company link**: `href={`/admin/company-overview/?cid=${company_id}&currentPage=${PAGES.BUSINESS_ACCOUNT}`}` with `PAGES.BUSINESS_ACCOUNT` from `../../company-overview/constants`.
- **Pagination**: `NativeSelect` rows per page 5/10/25; `material-ui-flat-pagination` with `offset` from `page`/`limit`.

### `src/views/admin/accounts/components/toolbar.js`

- **Title**: “Business Account Search”.
- **CSV**: `onBtnDownloadClicked` → `viewUtil.downloadFile(\`${apiBank.getBaseUrl()}/sba/v2/admin/currency-accounts/download\`)`; success toast via `BottomToaster`; disabled if `isEmpty(table.data)` or `loading`.

### `src/utils/business-account-utils.js`

- **`getCurrencyAccounts`**: `apiBank.getCurrencyAccounts(options)` → `get(response, "data.data")`.

### `src/utils/api-bank.js`

- **`getCurrencyAccounts`**: `GET ${getBaseUrl()}/sba/v2/admin/currency-accounts` with optional `query` string from caller.
- **`getBaseUrl`**: `API_BANK_URL` env, else production `https://sba-api.sleek.sg` or dev `http://localhost:4300`.

### `src/utils/api.js`

- **`getUser`**: `/admin/users/me` (used for permission gate).
- **`getCompanies`**: used for admin company search (exact path not expanded here; evidence: `getCompanies({ query: { limit: 10, name } })` in index).
- **`downloadFile`**: `getResource(urlString, options)` with default headers minus `Accept`/`Content-Type` — used indirectly by `view.downloadFile` for the CSV GET.

### `src/utils/auth-utils.js`

- **`checkResponseIfAuthorized`**: on 401, clears store and redirects to `/?redirect=...`.
