# Filter consents (URL query sync)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Admin auto-sign consent filters |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets CorpSec or other admins narrow the document-signing consent list by employee, role, or auto-sign mode and keep that view in the URL for sharing or revisiting without re-selecting filters. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — `/admin/auto-sign-configuration/` (`AutoSignConfiguration`, sidebar key `auto-sign-configuration`) |
| **Short Description** | Table header multi-selects (react-select with checkbox options) filter consents by `userId`, `roleId`, and `automatedSignature` (true/false for Auto-Signature vs Manual Signature). On change, the parent refetches via `getAllConsents` with query params including filters, `limit`, and `offset`. Current filter values are written back with `window.history.replaceState` so the query string stays in sync. Initial load reads `window.location.search` via `querystring.parse` and splits comma-separated values for the three filter keys. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `api.getAllConsents` → `GET ${baseUrl}/admin/document-signing-consent` with `options.query`; CMS/platform config for `auto_sign_documents` / `add_employee_active_role_identifiers` (enables page and role list); `api.getGroups` for role filter options; `api.getUser()` for permissions (`auto_sign_management`) and email verification gate |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/views/admin/auto-sign-configuration/table.js`; `src/utils/api.js` (`getAllConsents`) |
| **DB - Collections** | Unknown (consents persisted via API backing `/admin/document-signing-consent`, not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `getDefaultFilter` assigns every query-string key into `defaultFilterValues` (not only `userId` / `roleId` / `automatedSignature`); confirm whether extra keys are harmless for the API and UI. `setPathName` builds `key=value` from `value.split(",")` (array stringifies with commas) — confirm parity with backend expectations for multi-values. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **URL → state:** `getDefaultFilter()` uses `querystring.parse(window.location.search.slice(1))`, maps all keys into `defaultFilterValues` as `{ label, value }`, splits `userId`, `roleId`, and `automatedSignature` on commas for the request object, and returns `queryParams` for `fetchConsents` (lines 138–154, 94–112).
- **Fetch:** `api.getAllConsents({ query: { ...filter, limit, offset } })` (lines 94–104).
- **Filter change:** `handleFilterChange` updates `defaultFilterValues`, calls `setPathName`, then `fetchConsents()` (lines 397–404).
- **URL sync:** `setPathName` builds `pathname?key=val&…` via `window.history.replaceState` (lines 406–414).

### `src/views/admin/auto-sign-configuration/table.js`

- **Filter definitions:** `generateHeadRows` / `getOptions` — columns `userId` (employees from `dataSource`), `roleId` (from `activeRoles`), `automatedSignature` (boolean string options `"true"` / `"false"`) (lines 118–161).
- **UI:** Material-UI `TableHead` with `react-select` per filter; `onMultiSelectChange` → `handleFilterChange(filterStateKey, getCommaSeparetedValues(...))` (lines 247–251, 270–285, 300–318).

### `src/utils/api.js`

- `getAllConsents`: `endpoint = \`${getBaseUrl()}/admin/document-signing-consent\``; `getResource(endpoint, options)` (lines 2077–2079).
