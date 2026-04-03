# Monitor and filter business account transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Monitor and filter business account transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations and support staff (Sleek Admin users with `permissions.business_account` of `read`, `edit`, or `full`) |
| **Business Outcome** | Staff can find and prioritize business account payment activity using the same dimensions they use to triage operations and compliance work. |
| **Entry Point / Surface** | **sleek-website** admin: **Business Account Transactions** — `/admin/transactions/` — `AdminLayout` with `sidebarActiveMenuItemKey="transactions"` (see `new-admin-side-menu`). |
| **Short Description** | Loads a paginated list of all admin business account transactions via the bank API, with column filters for transaction ID, company (async company picker), sender/receiver name, account number, type/source, currency, amount, vendor, transaction status, and combined ops (admin) plus compliance status. Date range filter maps to `start_date` / `end_date`. Row click opens detail; URL can deep-link with `transaction_id` and `isShowDetailPopup=true` (`TransactionUrlManager`). Unverified users are redirected to `/verify/`; users without business account permission are redirected to `/admin`. |
| **Variants / Markets** | **Unknown** — no tenant-specific filter row in this view; Sleek typically operates **SG, HK, UK, AU**; confirm with bank/SBA service if markets differ. |
| **Dependencies / Related Flows** | **`bankApi.getTransactions`** → **`GET ${base}/sba/v2/admin/transactions/all`** with query (`limit`, `page`, `statuses`, `admin_statuses`, `compliance_statuses`, `vendor`, `start_date`, `end_date`, `transaction_id`, `origin_target_name`, `transaction_type`, `currency`, `amount`, `account_number`, `company_id`). **`api.getUser`** (session + permission gate). **`api.getCompany`** when refreshing a row’s company name after updates. Same page hosts **create transaction**, **manual reconciliation**, and **transaction detail** dialogs (separate capabilities). |
| **Service / Repository** | **sleek-website**: `src/views/admin/transactions/index.js`, `src/views/admin/transactions/components/new-table.js`, `src/views/admin/transactions/utils/transaction-url-manager.js`, `src/utils/business-account-utils.js`, `src/utils/api-bank.js`. **Bank / SBA backend** (not in this repo): implements `/sba/v2/admin/transactions/all` and persistence. |
| **DB - Collections** | **Unknown** — MongoDB or other stores for transactions live in the bank/SBA service; **sleek-website** is a client only. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact server-side validation and indexing for filter combinations; whether all query params are optional independently; RBAC details on the bank API beyond admin session. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/transactions/index.js` (`TransactionList`)

- **Mount**: `domready` renders into `#root`; `sidebarActiveMenuItemKey="transactions"`; primary toolbar title “Business Account Transactions”.
- **Permission**: `getUser()` → requires `registered_at` (else `/verify/`); `permissions.business_account` must be `read`, `edit`, or `full` (else `/admin`).
- **Data load**: `loadTransactions(limit, page, filterQuery)` → `bankApi.getTransactions({ query: { limit, page, ...filterQuery } })`; sets `transactionList`, `total` from `results` / `total`.
- **Filters** (`handleFilterChanged`): builds `filterQuery` for `statuses`, `admin_statuses`, `compliance_statuses`, `vendor`, `start_date`/`end_date`, `transaction_id`, `origin_target_name`, `transaction_type`, `currency`, `amount` (parsed float), `account_number`, `company_id` (from company select `value`). Resets to page 1, limit 10 on filter change. Special case: `ops_statuses` from child carries `admin_statuses` + `compliance_statuses` objects.
- **Pagination**: `handlePaginationClicked`, `handleRowsPerPageChanged` call `loadTransactions` with current `filterQuery`.
- **URL deep link**: If `TransactionUrlManager.hasTransactionUrlParams()`, seeds `filterValues` with `transaction_id` and optionally loads list + opens detail when `isShowDetailPopup=true`.
- **Child**: Renders `NewTable` with `handleFilterChanged`, pagination handlers, `defaultValues={filterValues}`.

### `src/views/admin/transactions/components/new-table.js` (`CustomPaginationActionsTable`)

- **Table**: Columns — transaction ID, transaction date, company, sender/receiver, account number, type/source, currency, amount, vendor, transaction status chip, ops status chip (`OpsStatusChip` / `TransactionStatusChip`).
- **Filters**: Debounced text inputs (1s) for ID, user name, transaction type, currency, amount, account number; `CompanySelect` for company; `DateRangeInput` popover for date range; multi-select with checkboxes for transaction status, ops+compliance status (split into `admin_*` / `compliance_*` values for parent), and vendor (`TRANSACTIONS_CONSTANTS.TRANSACTION_VENDOR`: DBS, NIUM, CURRENCYCLOUD).
- **Pagination**: `TablePagination` with `rowsPerPageOptions={[5, 10, 25]}`; props `page`, `limit`, `total`, `handlePaginationClicked`, `handleRowsPerPageChanged`.
- **Row UX**: Click row → `onClickOpenTransactionDetails` with transaction `_id`.

### `src/utils/business-account-utils.js` / `src/utils/api-bank.js`

- **`getTransactions`**: `GET` `` `${getBaseUrl()}/sba/v2/admin/transactions/all` `` with serialized query via `getResource`.

### `src/utils/constants.js`

- **`BUSINESS_ACCOUNT_PERMISSION`**, **`TRANSACTIONS_TABLE_HEADERS`**, **`TRANSACTIONS_CONSTANTS`** (status, admin status, compliance status, vendor enums).

### `src/views/admin/transactions/utils/transaction-url-manager.js`

- Syncs `transaction_id` and `isShowDetailPopup` with `history.replaceState` for shareable detail links.
