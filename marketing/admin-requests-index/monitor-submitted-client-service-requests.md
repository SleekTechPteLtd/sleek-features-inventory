# Monitor submitted client service requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Monitor submitted client service requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / Operations |
| **Business Outcome** | Staff can see which client document and servicing requests are in the queue, in what workflow state, and for which company—so they can prioritise work, drill into a company, or open a request for back-office processing. |
| **Entry Point / Surface** | Sleek Admin > Requests (`AdminRequestsView`, `sidebarActiveMenuItemKey="requests"`; route served from `src/views/admin/requests/index.js`) |
| **Short Description** | Paginated list of request instances from `GET /admin/request-instances`, joined in the UI to template names (including soft-deleted templates for labelling). Operators filter by one or more workflow statuses (`REQUEST_STATUSES`) and optionally by company via a searchable company picker; URL query `?st=` reflects status selection. Toolbar links to **New Request** and per-row **Edit** open create/edit flows when `user.permissions.requests` is `full`. |
| **Variants / Markets** | Unknown (status labels include ACRA-specific wording; not hard-coded to a single market in this view) |
| **Dependencies / Related Flows** | Request templates list (`GET /request-templates?showSoftDeletedTemplates=true`) for display names; admin request instance index (`GET /admin/request-instances`); company search (`GET /companies` with `admin: true` via `fetchCompaniesList`); downstream **New Request** (`/admin/requests/new/`), **Edit request** (`/admin/requests/edit/?cid=&rid=`), company profile (`/admin/companies/edit/?cid=`). Persistence and workflow rules live in the main API—out of repo. |
| **Service / Repository** | `sleek-website`: `src/views/admin/requests/index.js`, `src/views/admin/components/request-company-lookup.js`, `src/views/admin/common.js`, `src/utils/api.js` (`getRequestInstances`, `getRequestTemplates`, `getCompanies`), `src/utils/constants.js` (`REQUEST_STATUSES`). Main API (`getBaseUrl()`). |
| **DB - Collections** | Unknown (request instances and templates served by APIs not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the API honours a page size of 20 without an explicit `limit` query param; exact backend semantics when `status` is multi-select vs `Any`; whether `selectStatusValue` on `RequestCompanyLookup` is obsolete (still passed from parent but unused in the component). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/requests/index.js`

- **Shell:** `AdminLayout` with `sidebarActiveMenuItemKey="requests"`, `hideDrawer={true}` (lines 51–65).
- **Initial load:** `getUser` → `getRequestTemplates` (with `showSoftDeletedTemplates: true`) → `getRequestInstancesList` in `componentDidMount` (lines 44–47).
- **List API:** `getRequestInstancesList` builds `options.query`: `status` from `values` (null when first value is `"Any"`), `company` from `companyId`, `skip` = `(page - 1) * perPage` with `perPage` 20 (lines 265–277). Calls `api.getRequestInstances(options)`; stores `response.data` in `requestInstances`.
- **Status filter:** `CheckboxMultiSelect` with `REQUEST_STATUSES` plus `"Any"`; `selectStatusHandleChange` toggles values, resets to `["Any"]` when empty, updates URL `?st=` via `replaceState`, refetches list (lines 76–104, 107–148).
- **Pagination:** Shared handlers from `common.js`—prev/next and page input call `getRequestInstancesList`; next disabled when `requestInstances.length < 20` (lines 119–127).
- **Company filter:** `RequestCompanyLookup` with `fetchCompaniesList`, `getRequestInstancesList` as `getRequestInstances` (lines 151–154).
- **Table:** Columns for index, template name + `document_name`, custom-document icon if `client_provided_document`, company link to `/admin/companies/edit/?cid=`, status `Tag` from `REQUEST_STATUSES`, formatted `createdAt`, **Edit** to `/admin/requests/edit/?cid=&rid=` (lines 168–230). **New Request** and **Edit** gated on `user.permissions.requests === "full"` (lines 114–116, 208–210).
- **Empty state:** `NonIdealState` when `requestInstances` is empty (lines 168–171).
- **Query on load:** `querystring.parse` for `st` into initial `values` (lines 31–40).

### `src/views/admin/components/request-company-lookup.js`

- Blueprint `Select` over `companiesList`, client-side filter on `item.name`; `onQueryChange` → `fetchCompaniesList(query)` (lines 28–44).
- Selecting a company calls `handleSelectCompany` then `getRequestInstances(company._id)`; “No Selection” clears company and refetches via `handleSelectNoCompany` (lines 39–43).

### `src/views/admin/common.js`

- **`fetchCompaniesList`:** `api.getCompanies({ query: { name }, admin: true })`, uses `response.data.companies`, filters empty names (lines 24–37).
- **`handleSelectCompany` / `handleSelectNoCompany`:** Set selection state then run callback (lines 6–21).
- **Pagination:** `handleChangePage`, `handleClickPrevPage`, `handleClickNextPage` (lines 40–53).
- **`getUser`:** `api.getUser()`, redirect to `/verify/` if email not verified (lines 56–65).

### `src/utils/api.js`

- **`getRequestInstances`:** `GET ${getBaseUrl()}/admin/request-instances` with optional query via `getResource` (lines 1185–1187).

### `src/utils/constants.js`

- **`REQUEST_STATUSES`:** Values `processing_by_sleek`, `waiting_for_signatures`, `voided`, `referred_to_acra`, `success`, `fail` with Blueprint `intent` for tags (lines 1324–1330).
