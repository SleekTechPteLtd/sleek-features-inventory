# Session user and verification gate

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Session user and verification gate |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Ensures the Camunda workflow list only runs for an authenticated staff user with a verified email; unauthenticated API responses send the browser back through login. |
| **Entry Point / Surface** | Sleek Admin > Workflow — `/admin/sleek-workflow/` (`WorkFlowList`, sidebar key `camunda-workflow`) |
| **Short Description** | On mount, `getUser()` calls `api.getUser()` and, if `registered_at` is null (treated as unverified), redirects to `/verify/`. On success, `user` is stored in state and passed to `AdminLayout`. On failure, `checkResponseIfAuthorized` clears client storage and redirects to `/?redirect=…` when the error message indicates HTTP 401. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `api.getUser` → `GET /admin/users/me` (via `getResource`); same verification pattern as other admin index pages (e.g. Companies, Auto-Sign); downstream: workflow list `initialize`, `getCompanies`, Camunda APIs after user is present |
| **Service / Repository** | `sleek-website` — `src/views/admin/sleek-workflow/index.js`, `src/utils/auth-utils.js`, `src/utils/api.js` (getUser) |
| **DB - Collections** | Unknown (user record served by admin API; not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `auth-utils.js` ends with `module.export` instead of `module.exports` for the legacy export block — verify whether dead code or bundler resolves it. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/index.js`

- **`componentDidMount`:** After platform tenant setup, calls `getCompanies()`, `getUser()`, filter restore, `getAssignees()` (lines 221–236).
- **`getUser`:** `api.getUser().then` — `emailVerified` is `get(user, "registered_at") != null`; when `emailVerified === false`, sets `window.location = "/verify/"` and returns; else `setState({ user })` (lines 379–387).
- **`catch`:** Passes `get(error, "message")` to `checkResponseIfAuthorized` (lines 388–391).
- **`render`:** `<AdminLayout … user={this.state.user} sidebarActiveMenuItemKey="camunda-workflow" />` (lines 78–95).

### `src/utils/auth-utils.js`

- **`checkResponseIfAuthorized(responseStatus)`:** If `responseStatus` equals `HTTP_UNAUTHORIZED` (from `./constants`, numeric or string), calls `store.clearAll()` and sets `window.location.href` to `/?redirect=${pathname+search}` (lines 12–16).

### Related API (not duplicated line-by-line)

- **`getUser`:** Implemented in `src/utils/api.js` as `GET` to `/admin/users/me` — see sibling inventory entries and `load-admin-session-and-platform-config` evidence for `getResource` admin prefix behavior.
