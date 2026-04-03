# Finish admin OAuth sign-in

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Finish admin OAuth sign-in |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Internal staff complete the identity-provider redirect so the marketing site stores their admin access token and downstream authenticated admin experiences can load API calls with a bearer token. |
| **Entry Point / Surface** | Sleek marketing site — OAuth redirect lands on `/auth/callback/` (webpack entry `auth/callback` → `AdminAuthCallbackView`); users arrive here after `adminLogin()` / SSO authorize |
| **Short Description** | On load, the view obtains a configured `AuthClient`, runs `handleAdminRedirectCallback` to validate `code` and `state`, exchange the authorization code for tokens via `POST /sso/token` (PKCE), then persists `tokenSet.access_token` under `user_auth_token` in the local `store`. On success, `auto_redirect` sends the user to the stored post-login URL (default `/admin/`). Errors render a minimal error panel with link home. |
| **Variants / Markets** | Unknown (country comes from `PLATFORM_COUNTRY_CODE` / default `SGP`; not fully enumerated here) |
| **Dependencies / Related Flows** | Upstream: `AuthClient.adminLogin()` → `/sso/authorize` with PKCE (`generateAdminAuthorizationUrl`). Same client: `logout()` → `/sso/logout`. Config: `getAppCustomEnv()` → `SLEEK_AUTH_BASE_URL`, `PLATFORM_COUNTRY_CODE`. Downstream: any admin view that reads `user_auth_token` or shared API headers for staff APIs |
| **Service / Repository** | `sleek-website` — `src/views/admin/auth/callback/index.js`, `src/utils/get-auth-client.js`, `src/utils/auth/auth-client.js`, `src/utils/auth/auth-proxy.js`, `src/utils/auth/managers/*` (transaction, redirection, store) |
| **DB - Collections** | None in this repo (tokens and PKCE transaction state are client-side via `StoreManager` / local storage patterns; Sleek Auth service backs `/sso/token`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auth/callback/index.js`

- **`AdminAuthCallbackView`:** `useEffect` calls `handleCallback()` once.
- **`handleCallback`:** `getAuthClient()` then `client.handleAdminRedirectCallback((error, tokenSet) => { ... })`.
- **Success path:** `store.set("user_auth_token", tokenSet.access_token)`.
- **Error path:** Sets `authError`, logs `name`, `code`, `reference_id`, `details`; updates `document.title`; UI shows error details and link to `/`.

### `src/utils/get-auth-client.js`

- **`getAuthClient`:** Loads env via `getAppCustomEnv()`, returns `new AuthClient({ auth_base_url: env.SLEEK_AUTH_BASE_URL, auto_redirect: true, country_code: env.PLATFORM_COUNTRY_CODE || "SGP", redirect_path: "/auth/callback/", default_login_redirect_url: "/admin/", store: { key_prefix: BUILD_NUMBER } })`.
- **`redirect_path`:** Aligns with webpack mapping `auth/callback` → `src/views/admin/auth/callback/index.js` (`webpack/paths.js`).

### `src/utils/auth/auth-client.js`

- **`redirectUri`:** `${window.location.origin}${config.redirect_path}` — must match authorize and token requests.
- **`generateAdminAuthorizationUrl`:** `${auth_base_url}/sso/authorize?` with `code_challenge`, `state`, `country_code`, `redirect_uri`.
- **`handleAdminRedirectCallback`:** Reads `code` and `state` from `window.location.search`; validates against `TransactionManager` PKCE transaction (`state`, `code_verifier`); calls `this.proxy.createToken({ code, code_verifier, country_code, redirect_uri })`; invokes callback with `(null, session)` or standardized error; on success and `auto_redirect`, `redirectionManager.initPostLoginRedirect()`.

### `src/utils/auth/auth-proxy.js`

- **`createToken`:** `POST /sso/token` with `code`, `code_verifier`, `country_code`, `redirect_uri`; returns token payload (includes `access_token` used by the callback view).
