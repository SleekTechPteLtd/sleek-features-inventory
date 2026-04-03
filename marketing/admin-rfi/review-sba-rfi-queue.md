# Review SBA RFI queue

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review SBA RFI queue |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations and support staff (Sleek Admin users with Business Account permissions) |
| **Business Outcome** | Staff can see all company Requests for Information in one place, triage by status and dates, and jump to the company or the full RFI questionnaire without hunting across systems. |
| **Entry Point / Surface** | **sleek-website** admin: **Business Account** → **SBA Request for Info** (`/admin/rfi/`). Primary toolbar title: “SBA Request for Information” (`RFIToolbar`). |
| **Short Description** | Paginated, sortable table of RFIs loaded from the SBA API Gateway. Operators search by company name (debounced), change page size (5 / 10 / 25), and sort by date requested, company name, RFI status, or date submitted. Each row shows status with styling, links the company name to the company overview (Business Account tab), and offers **VIEW RFI** to `/admin/rfi/detail/?id=…` for questionnaire detail. |
| **Variants / Markets** | **Unknown** for tenant breadth. Production gateway base URL in code defaults to `https://sg-backend.sleek.com/sbaapigateway` (SG-oriented); local dev uses `localhost:4315`. |
| **Dependencies / Related Flows** | **`api.getRFIs`** → SBA API Gateway **`GET /api/v1/rfi`** with `page`, `limit`, `order`, `orderBy`, `search`. **`getUser`** (`src/views/admin/rfi/common.js`) via main **`api.getUser`** — requires verified email and **`permissions.business_account`** in `READ` / `EDIT` / `FULL` (`BUSINESS_ACCOUNT_PERMISSION`); otherwise redirect to `/verify/` or `/admin`. Sidebar visibility gated by CMS Business Account + `canViewBusinessAccount` (`new-admin-side-menu.js`). Related: RFI detail page (`admin/rfi/detail`), company overview Business Account page (`PAGES.BUSINESS_ACCOUNT`). |
| **Service / Repository** | **sleek-website**: `src/views/admin/rfi/index.js`, `components/rfi-table.js`, `components/rfi-toolbar.js`, `common.js`. **SBA API Gateway** (separate service; base from `getBaseUrl()` in `api-gateway.js`, env `SBA_API_GATEWAY_URL` overrides). |
| **DB - Collections** | **Unknown** from this repo; list data is returned by the gateway. Persistence and collection names live in the SBA backend behind `/api/v1/rfi`. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which MongoDB (or other) stores back `GET /api/v1/rfi` and exact RBAC on the gateway. Whether non-SG tenants use the same screen with a different gateway URL. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/rfi/index.js` (`RFIList`)

- **Mount**: `domready` renders into `#root`; **`AdminLayout`** with `sidebarActiveMenuItemKey="rfi"`, `hideDrawer={true}`, **`RFIToolbar`** in primary toolbar.
- **Data**: `getRFIs` calls **`api.getRFIs({query})`** with `query = {page, limit, order, orderBy, search}`; reads `response.data` and `response.meta.total` into table state.
- **Sort**: `onChangeOrder` cycles per column: `asc` → `desc` → cleared (`order` / `orderBy` undefined). Headers: `createdAt`, `companyName`, `status`, `updatedAt`, `action`.
- **Search**: Debounced 200ms `onChangeSearch` updates `search`; `useEffect` refetches when `pagination.limit`, `pagination.page`, `sortOrder`, or `search` change.
- **Initial user**: `useEffect` → `getUser().then(setUser)`.

### `src/views/admin/rfi/components/rfi-table.js` (`RFITable`)

- **Rows**: `_id`, `companyId`, `companyName`, `status`, `createdAt`, `updatedAt`, `response` — company link: `` `/admin/company-overview/?cid=${companyId}&currentPage=${PAGES.BUSINESS_ACCOUNT}` ``; **VIEW RFI**: `` `/admin/rfi/detail/?id=${_id}` ``.
- **Submitted column**: Shows “-” if `response` is empty, else formatted `updatedAt`.
- **Pagination**: Material-UI `Pagination` with `offset` from `(page - 1) * limit`; rows-per-page `NativeSelect` resets to `page: 1` on limit change.

### `src/views/admin/rfi/components/rfi-toolbar.js` (`RFIToolbar`)

- Static title: **“SBA Request for Information”**.

### `src/views/admin/rfi/common.js`

- **`getUser`**: `api.getUser()`; unverified → `/verify/`; missing business account permission → `/admin/`.
- **`RFIStatus`**: `requested`, `submitted`, `approved`, `rejected`, `expired` (constants for domain language; table displays API `status` as returned).

### `src/utils/api-gateway.js`

- **`getBaseUrl()`**: `SBA_API_GATEWAY_URL` env, else prod `https://sg-backend.sleek.com/sbaapigateway`, else `http://localhost:4315`.
- **`getRFIs`**: `GET` `` `${getBaseUrl()}/api/v1/rfi` `` via **`getResource`** (query string from `options.query`).
- Related exports: **`getRFI`**, **`submitRFI`** (`PATCH` with `response` body) — used by detail flow, not the list view.

### `src/components/new-admin-side-menu.js`

- **Business Account** subsection (when `isBusinessAccountCMSEnabled && canViewBusinessAccount`): menu item **“SBA Request for Info”**, `href="/admin/rfi/"`, key `rfi`.
