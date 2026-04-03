# Export company event history

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Export company event history |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff with admin access (Sleek Admin / users granted `companies` read on admin API) |
| **Business Outcome** | Staff can download a consolidated CSV of company lifecycle status transitions for audit, compliance, or investigation. |
| **Entry Point / Surface** | **sleek-website** admin **Home** (`admin` bundle → `/admin/`) — `AdminLayout` with `sidebarActiveMenuItemKey="home"`; primary toolbar **Export Event History** (Blueprint `Button`, icon `export`). |
| **Short Description** | From the admin home dashboard, operators trigger a file download. The client calls the main API `GET /admin/companies/export-event-history` with session headers; the backend returns `history.csv` (plain text CSV) built from each company’s `event_history` array. |
| **Variants / Markets** | No market filter in the export handler; data is whatever exists in the deployed `Company` documents. Typical Sleek markets **SG, HK, UK, AU** — **Unknown** for tenant-specific scoping without runtime config review. |
| **Dependencies / Related Flows** | **sleek-website**: `viewUtil.downloadFile` → `api.downloadFile` (`getResource` with default auth headers). **sleek-back**: `Company.find` for companies that have at least one `event_history` entry; CSV columns: company name, event date, new status (`event`), previous status. Related: admin home stats (`GET /admin/companies/get-stats`), company lifecycle elsewhere in admin. |
| **Service / Repository** | **sleek-website**: `src/views/admin/home.js`, `src/utils/view.js` (`downloadFile`), `src/utils/api.js` (`getBaseUrl`, `downloadFile` / `getResource`). **sleek-back**: `controllers/admin/company-controller.js` (route registration). |
| **DB - Collections** | **MongoDB**: `Company` — reads `name` and `event_history` for documents where `event_history` is non-empty. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether any middleware or DB routing limits export to a single tenant in production (not visible in the handler body). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/home.js` (`AdminHomeView`)

- **Toolbar**: `renderPrimaryToolbarContent` — `Button` **Export Event History** → `handleClickExportEventHistory`.
- **Handler**: `handleClickExportEventHistory` — `viewUtil.downloadFile(\`${api.getBaseUrl()}/admin/companies/export-event-history\`)`.
- **Body**: `AdminDashboard` with statistics from `api.getStats({ admin: true })` (separate from export).
- **Mount**: `componentDidMount` — optional CMS redirect (`enable_admin_home_redirect`); else `getUser`, `getRequestsCount`, `getStats`.

### `src/utils/view.js`

- **`downloadFile(fileUrl)`**: `api.downloadFile` → blob; reads `Content-Disposition` / `content-disposition` for filename; triggers browser download.

### `src/utils/api.js`

- **`getBaseUrl()`**: production default `https://api.sleek.sg`, else `http://localhost:3000` (or `API_BASE_URL`).
- **`downloadFile(urlString)`**: `getResource` with `getDefaultHeaders()` (auth cookie / token as configured).

### `sleek-back/controllers/admin/company-controller.js`

- **Route**: `GET /admin/companies/export-event-history`
- **Guards**: `userService.authMiddleware`, `accessControlService.can("companies", "read")`.
- **Logic**: `Company.find({ "event_history.0": { $exists: true } }).select({ name: 1, event_history: 1 })`; builds CSV header `name,date,new status,old status`; rows iterate each company’s `event_history` in order, emitting new status and chained “old status” from the prior row’s event name.
- **Response**: `Content-Type: text/plain`, `Content-Disposition: attachment; filename=history.csv`, `Access-Control-Expose-Headers: Content-Disposition`.

### `sleek-back/tests/controllers/company-controller/export-event-history.js`

- **200**: user in Sleek Admin group with `companies` read.
- **401**: user without access.
