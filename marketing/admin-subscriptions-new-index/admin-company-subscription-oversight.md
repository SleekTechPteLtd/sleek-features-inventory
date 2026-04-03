# Admin company subscription oversight

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Admin company subscription oversight |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin / operations users (authenticated Sleek admin; same surface as other subscription admin tools) |
| **Business Outcome** | Operators can find companies and subscription rows quickly, see renewal timing, payment context, and ownership, and leave audit-style comments so billing and account management stay coordinated. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/subscriptions/new/`** — `AdminLayout` with `sidebarActiveMenuItemKey="subscriptions"` and `sidebarActiveMenuSubItemKey="paid-subscriptions"` (highlights **Paid** under Subscriptions; the standalone “Subscriptions” top-level item in `new-admin-side-menu.js` is commented out). Detail drill-down: **`/admin/subscriptions/new/details/?subscriptionId=<id>`** (opens in new tab from table). Company profile: **`/admin/companies/edit/?cid=<companyId>`**. |
| **Short Description** | Loads paginated **company subscriptions** from the admin API with default sort `updatedAt` desc, renewal window default **to** date six months ahead, and optional **company** search (async company list). **Advance Filter** supports company status, payment status, CSS-in-charge, account manager (accounting group), subscription product, subscription status, and renewal date range; filter state can persist in `localStorage` (`subscriptions-advance-search-filter`). The table shows company (with CMS-driven status tag), **comments** (popover: list + load more, **post** via Sleek Auditor), subscription name, duration, renewal date, service activated date, payment info (manual vs card, manual details popover), owner, invoice link, subscription status; column sorting triggers server-side re-query. Pagination uses `limit` / `skip`. |
| **Variants / Markets** | Unknown (API is shared; no market-specific branching in these views). |
| **Dependencies / Related Flows** | **`api.getAdminAllCompanySubscriptions`** → `GET /admin/company-subscriptions` with query (`sortBy`, `sortOrder`, `skip`, `limit`, `company`, `company_status`, `payment_status`, `css_in_charge`, `accounting_in_charge`, `overdue_at_from`, `overdue_at_to`, `payment_info_by`, `subscription_by`, `subscription_status`, optional `overdue_at`, `is_auto`). **`api.getCompanies`** (`admin: true`) for company picker (`views/admin/subscriptions/common.js`). **`api.getAdminsByGroup`** with `group_name` **Customer Success** / **Accounting** for filter dropdowns. **CMS platform config** (`admin_constants`: `COMPANY_STATUSES`, `SUBSCRIPTION_NAMES`, `SUBSCRIPTION_STATUSES`). **`getCompanyComments` / `postCompanyComment`** (`api-sleek-auditor`) → `GET`/`PUT` `/v2/sleek-auditor/api/log/company/:companyId/comment/`. Related: paid/unpaid/cancellation subscription admin lists, subscription detail page under `new/details`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/subscriptions/new/index.js`, `src/views/admin/subscriptions/new/components/table.js`, `src/views/admin/subscriptions/new/components/filter.js`, `src/views/admin/subscriptions/common.js`, `src/utils/api.js`, `src/utils/api-sleek-auditor.js`. **Backend** (not in repo): admin company-subscriptions service, companies, users/admins-by-group, Sleek Auditor comment storage. |
| **DB - Collections** | **MongoDB** (backend only; not visible in sleek-website): **Unknown** exact collections for `company-subscriptions`, companies, and auditor comments without backend source. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium (top-level nav to this URL is commented out in `new-admin-side-menu.js`; access may be direct URL or legacy bookmarks.) |
| **Disposition** | Unknown |
| **Open Questions** | `AdminSubscriptionsView` uses `sidebarActiveMenuSubItemKey="paid-subscriptions"` while the route is **`/admin/subscriptions/new/`** — confirm whether the **Paid** sub-nav highlight is intentional. `getCompanySubscriptions` uses `this.state.perPage` for `maxPage` but state defines **`limit`** — likely a bug (pagination math). `index.js` `delete options.query.accountingInCharge` may not clear **`accounting_in_charge`** when filter cleared. Whether `is_auto` / `overdue_at` from state are still used (not set in shown `new/index` state). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/subscriptions/new/index.js` (`AdminSubscriptionsView`)

- **Mount**: `getUser()` (from `subscriptions/common`), `getCompanySubscriptions()`.
- **State**: Pagination `offset`, `limit`, `page`, `sortBy` default `updatedAt`, `sortOrder` default `-1`, `filter.renewalTo` default six months ahead; `selectedCompanyId` for company scope.
- **API**: `api.getAdminAllCompanySubscriptions({ query })` → `GET ${getBaseUrl()}/admin/company-subscriptions` per `api.js`.
- **Handlers**: `handlePaginationClick`, `handleRowsPerPageChange`, `handleSorting`, `handleOnCompanyChange`, `handleOnAdvanceSearch` merge filter into query params as listed in master sheet.

### `src/views/admin/subscriptions/new/components/filter.js` (`Filter`)

- Company **Select** with `handleSearchCompany` / `fetchCompaniesList` / `handleOnCompanyChange`.
- **Advance Filter** toggles extra rows: `companyStatus`, `paymentStatus`, `cssInCharge`, `accountingInCharge`, `subscriptionBy`, `subscriptionStatus`, `renewalFrom`, `renewalTo`; **Search** / **Clear**; `localStorage` key `subscriptions-advance-search-filter`.
- Loads `companyStatuses` from CMS; `getCustomerSuccessMembers` / `getAccountingMembers` via `api.getAdminsByGroup`.

### `src/views/admin/subscriptions/new/components/table.js` (`SubscriptionsTable`)

- **Sort**: `handleSorting(property, numberedOrder)` from `TableSortLabel` on sortable columns (company, service, duration, overdue_at, expected_external_payment_info, status).
- **Columns**: Company + status tag, comment icon → MUI popover with `getCompanyComments`, `postCompanyComment`, load more; links to company edit and subscription detail; `ManualPaymentInfo` popover when manual payment path; invoice number + Xero URL from `getInvoiceInfo`; subscription status label from CMS.
- **Platform config** in `componentDidMount`: `SUBSCRIPTION_NAMES`, `COMPANY_STATUSES`, `SUBSCRIPTION_STATUSES`.

### `src/views/admin/subscriptions/common.js`

- `getUser` → `api.getUser` with redirect to `/verify/` if email not verified; `checkResponseIfAuthorized` on error.
- `handleSearchCompany`, `fetchCompaniesList` → `api.getCompanies({ query: { name }, admin: true })`.

### `src/utils/api.js`

- `getAdminAllCompanySubscriptions` → `GET` `` `${getBaseUrl()}/admin/company-subscriptions` ``.
- `getAdminsByGroup` → `GET` `` `${getBaseUrl()}/admin/users/admins` `` with query `group_name`.
- `getCompanies`, `getUser` — standard `getResource` with optional `admin` prefix.
