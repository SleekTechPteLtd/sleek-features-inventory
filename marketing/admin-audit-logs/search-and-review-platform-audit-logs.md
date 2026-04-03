# Search and review platform audit logs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Search and review platform audit logs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / operations staff (Sleek Admin users with access to the audit logs screen) |
| **Business Outcome** | Staff can investigate who did what, for which company, and when—supporting operational troubleshooting, compliance questions, and internal audit workflows. |
| **Entry Point / Surface** | **sleek-website** admin: **Audit Logs** (`/admin/audit-logs/`) — `AdminLayout` with `sidebarActiveMenuItemKey="audit-logs"`; primary toolbar title “Audit Logs” and **Search** action. |
| **Short Description** | Loads paginated audit entries via the platform API after the user applies filters. Filters include **date range** (start/end), **company** (searchable select from `getCompanies`), **tags** (comma-separated, mapped to `tags[0]`, `tags[1]`, …), free-text **text**, and **actor email** (`actionByEmail`). Results show company name, log text, **Action By** (email), tags (click to copy), and **Created Date**. Pagination uses the current page and total count from the API. **Search** applies filters; the legacy `action` column exists in constants but is not shown in the table UI. |
| **Variants / Markets** | **Unknown** — no tenant-specific branching in these views; platform behaviour may vary by deployment. |
| **Dependencies / Related Flows** | **`api.getAuditLogsV2`** → `GET {base}/v2/sleek-auditor-v2/audit-logs` with query (`page`, `startDate`/`endDate`, `companyName`, `tags[n]`, `text`, `actionByEmail`, etc.). **`api.getCompanies`** for company filter options. **`api.getUser`** (session; unverified users redirected to `/verify/`). Legacy **`getAuditLogs`** in the same module targets `GET /v2/utilities/audit-logs` but this screen uses **V2** only. Downstream: **sleek-auditor-v2** (and backing storage) — not in this repo. |
| **Service / Repository** | **sleek-website**: `src/views/admin/audit-logs/index.js`, `src/views/admin/audit-logs/components/audit-table.js`, `src/utils/api.js` (`getAuditLogsV2`, `getCompanies`, `getUser`). **sleek-auditor-v2** / API gateway (not in this repo): persists and serves audit log entries. |
| **DB - Collections** | **Unknown** from this frontend — audit log storage is behind **sleek-auditor-v2**; not referenced in sleek-website. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the list should load without an explicit **Search** click on first visit (`componentDidMount` does not call `loadAuditLogs`). **`handleRowsPerPageChanged`** in `index.js` invokes `loadTransactions`, which is not defined on the class (rows-per-page UI is commented out in `audit-table.js`, so this may be dead or broken if re-enabled). Whether `GET /v2/utilities/audit-logs` (`getAuditLogs`) is still used elsewhere for overlapping data. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/audit-logs/index.js` (`TransactionList`)

- **Mount**: `domready` → `ReactDOM.render` into `#root`; `componentDidMount` calls `getUser()` and `getCompanies()` only (no initial audit fetch).
- **Data load**: `loadAuditLogs(limit, page, filterQuery)` → `api.getAuditLogsV2({ query: { page, ...filterQuery } })`; reads `data.data` and `data.totalCount`.
- **Filters → query** (`handleApplyFilters`): `startDate`/`endDate` from `dateRange`; `companyName` from selected company label; `tags[i]` from comma-split tags; `text`; `actionByEmail`.
- **Pagination**: `handlePaginationClicked` → `loadAuditLogs` with current `filterQuery`.
- **Layout**: `AdminLayout` `hideDrawer={true}`, `sidebarActiveMenuItemKey="audit-logs"`, **Search** button → `handleApplyFilters`.

### `src/views/admin/audit-logs/components/audit-table.js` (`CustomPaginationActionsTable`)

- **Columns**: Company, Text, Action By, Tags, Created Date (Blueprint `DateRangeInput` under Created Date for range filter; company `react-select` with `getCompanies` on input change; text inputs for tags, text, action by).
- **Row display**: `company.name`, `text`, `actionBy.email`, `tags` as chips (clipboard copy), `createdAt` formatted as `DD MMM YYYY`.
- **Pagination**: `material-ui-flat-pagination` with `limit`, `offset` from `(page - 1) * limit`, `total`, `handlePaginationClicked`.

### `src/utils/api.js`

- **`getAuditLogsV2`**: `GET ${getBaseUrl()}/v2/sleek-auditor-v2/audit-logs` via `getResource`.
- **`getAuditLogs`** (legacy): `GET ${getBaseUrl()}/v2/utilities/audit-logs` — not used by this admin audit logs page.

### `src/utils/constants.js`

- **`AUDIT_LOGS_TABLE_HEADERS`**: `TEXT`, `COMPANY_NAME`, `CREATED_DATE`, `ACTION_BY`, `ACTION`, `TAGS`.

### `src/components/new-admin-side-menu.js`

- Nav item `key="audit-logs"`, `href="/admin/audit-logs/"` (admin menu entry).
