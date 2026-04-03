# Load admin session and platform config

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Load admin session and platform config |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Ensures the admin Companies view (and shared admin chrome) only runs with a resolved platform configuration and an authenticated staff user, and blocks unverified accounts from using admin until email verification completes. |
| **Entry Point / Surface** | Sleek Admin > Companies — `/admin/companies/` (`AdminCompaniesView`, sidebar key `companies`); bootstrap logic is shared with other pages using `AdminLayout` and `getPlatformConfig` |
| **Short Description** | On mount, the view loads CMS-driven platform config (tenant, feature flags, labels) via `getPlatformConfig()`, then loads the current user with `api.getUser()`. Users without `registered_at` are redirected to `/verify/`. The layout receives `user` and enforces `profile === "admin"` plus resource permissions from `user.permissions` against `ADMIN_RESOURCES`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `utils/config-loader.js` (`getPlatformConfig` → `api.getPlatformConfig` with `platform: "admin"`); `api.getUser` → `GET /admin/users/me`; cookie/session implied by `getDefaultHeaders()`; downstream: company list `getCompanies`, sidebar `cmsAppFeatures` / `cmsGeneralFeatureList` from config |
| **Service / Repository** | `sleek-website` — `src/views/admin/companies/index.js`, `src/utils/api.js` (`getPlatformConfig`, `getUser`, `getResource`), `src/layouts/new-admin.js`, `src/utils/config-loader.js` |
| **DB - Collections** | Unknown (user and config served by API backing `/admin/users/me` and `/v2/config/:platform`, not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `AdminLayout`’s duplicate `getPlatformConfig()` in `componentDidMount` is always redundant with the page (extra network/cache read). `config-loader.js` ends with `module.export` typo vs `export` for `getAuthenticatedAppFeatureList` — verify bundler behavior. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/index.js`

- **`componentDidMount`:** `getPlatformConfig()` then `setState({ platformConfig })`; calls `getUser()` and `getCompanies()` (lines 604–608).
- **`getUser`:** `api.getUser()` → `response.data` as `user`; if `get(user, "registered_at") == null`, `window.location = "/verify/"`; else `setState({ user })` (lines 611–634).
- **Render:** `<AdminLayout user={this.state.user} ... sidebarActiveMenuItemKey="companies" />` (lines 65–78). Toolbar and body require `this.state.platformConfig` (lines 89–90, 326–327).

### `src/utils/config-loader.js`

- **`getPlatformConfig`:** Uses cached `localStorage.platformConfig` when build number matches; else `api.getPlatformConfig({ platform: "admin" })`, persists to `localStorage`, returns `platformConfig.data` (lines 9–26).

### `src/utils/api.js`

- **`getUser`:** `GET \`${getBaseUrl()}/admin/users/me\`` via `getResource` (lines 248–255).
- **`getPlatformConfig`:** `GET \`${getBaseUrl()}/v2/config/${options.platform}\`` — with `platform: "admin"` from the loader (lines 415–417).
- **`getResource`:** For `options.admin === true`, prefixes path with `/admin` on the base URL (lines 131–145).

### `src/layouts/new-admin.js`

- **`render`:** If `isEmpty(this.props.user)` returns `null` (lines 166–167). If `user.profile !== "admin"`, shows access denied (lines 167–174).
- **`componentDidMount`:** Loads `getPlatformConfig()` into `this.state.platformConfig` (lines 480–482).
- **`checkUserAccess`:** If active sidebar maps to an `ADMIN_RESOURCES` entry and `user.permissions[permissionKey]` is empty or `"none"`, redirects to `/admin/` (lines 525–539); skipped for paths under `/subscriptions/`.
- **Sidebar:** Passes `cmsAppFeatures` and `cmsGeneralFeatureList` from `this.state.platformConfig` to `AdminSideMenu` (lines 249–250).
