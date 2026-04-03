# Sign in to Sleek Admin

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Sign in to Sleek Admin |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin, Operations User, and Sleek client users (staff and clients who use this entry surface) |
| **Business Outcome** | Authenticated users reach the admin area (or a post-login redirect) so they can work in Sleek Admin without re-entering credentials when a valid session already exists. |
| **Entry Point / Surface** | Sleek marketing site — root `/` webpack entry `index` → `StartView` (`src/views/index.js`); optional query `?ft=login`, `redirect=`, registration and password flows |
| **Short Description** | Loads platform config from the API and CMS-driven feature flags, then offers SSO (Sleek Auth `adminLogin`), Auth0 Lock, or email/password login. Successful sign-in stores `user_auth_token` and redirects to `redirect` or `/admin/`. If a token already exists, the app validates the user via `/admin/users/me` and redirects when the account is verified. Cross-tab iframe messages can sync login/logout tokens. API responses that are unauthorized trigger a cleared session and return to `/` with a redirect back to the current path. |
| **Variants / Markets** | Unknown (country comes from `PLATFORM_COUNTRY_CODE` / default `SGP` on `AuthClient`; not fully enumerated in these files) |
| **Dependencies / Related Flows** | Upstream: `GET /v2/config/admin` (platform config), Auth0 (`auth0-lock`), Sleek Auth SSO (`getAuthClient` → `AuthClient.adminLogin`, callback documented under `marketing/auth-callback/`). Downstream: all admin views using `user_auth_token` / default API headers. Related: password reset and registration flows on the same view |
| **Service / Repository** | `sleek-website` — `src/views/index.js`, `src/views/index.css`, `src/utils/api.js`, `src/utils/get-auth-client.js`, `src/utils/auth-utils.js`, `src/utils/config-loader.js`, `src/utils/app-feature-utils.js`, `src/utils/auth-listener.js`, `src/utils/logout-listener.js`, `src/layouts/browser-check-dialog.js`; backend: Sleek API (`users/login`, `admin/users/me`, etc.) and Sleek Auth for SSO |
| **DB - Collections** | None in this repo (session token in `store` / `localStorage`; platform config cached in `localStorage`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Auth0 path writes `user_auth_token` to `localStorage` while password login uses `store` (`api.logIn`); confirm whether both are guaranteed equivalent for downstream API clients. `logout-listener.js` is stubbed (no `storage` listener). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/index.js`

- **Bootstrap:** Renders `StartView`, registers `AuthenticationListener` and `LogoutListener` at module load.
- **Post-login redirect:** `handleRedirect()` reads `redirect` via `getRedirectUrlFriendly("redirect")`, default `DEFAULT_LANDING_PAGE` `/admin/`, allows only `REDIRECT_RULE_REGEX` before assigning `window.location.href`; otherwise uses `encodeURIComponent(redirect)` as href (defensive handling for unsafe strings).
- **`componentDidMount`:** `getPlatformConfig()` then reads CMS features via `getAppFeatureProp` for `auth0`, `sso`, `external_links`, `localization`; dev overrides via `process.env` for Auth0/SSO flags.
- **SSO:** When `isSsoEnabled` and no `formType`, sets `formType: "login-opts"`; `loginViaSso()` calls `getAuthClient()` then `client.adminLogin()`.
- **Auth0:** When enabled, constructs `Auth0Lock`; on `authenticated`, stores `user_auth_token` in `localStorage`, calls `handleRedirect()`, hides widget.
- **Email/password:** `handleSubmitLogin` → `api.logIn` with `client_type: CLIENT_TYPE_DB_TEXT.SLEEK_CLIENT`, then `handleRedirect()` on success.
- **Session resume:** If `store.get("user_auth_token")`, calls `api.getUser()`; if `user.registered_at != null`, calls `handleRedirect()`; otherwise shows UI.
- **Alternate login:** SSO config `allow_alternate_login` shows link to Auth0 or classic login form.

### `src/utils/api.js`

- **`logIn`:** `POST ${getBaseUrl()}/users/login`; on success stores `data.auth_token` as `store.set("user_auth_token", authToken)`.
- **`getUser`:** `GET ${getBaseUrl()}/admin/users/me` (uses default headers including auth).
- **`handleResponse` / auth:** JSON responses call `checkResponseIfAuthorized(data.status)`; non-JSON errors also call `checkResponseIfAuthorized` for failed responses.

### `src/utils/get-auth-client.js`

- **`getAuthClient`:** `AuthClient` with `auth_base_url: env.SLEEK_AUTH_BASE_URL`, `redirect_path: "/auth/callback/"`, `default_login_redirect_url: "/admin/"`, `country_code`, `store` keyed by `BUILD_NUMBER` — aligns SSO with the separate OAuth callback flow.

### `src/utils/auth-utils.js`

- **`checkResponseIfAuthorized`:** On 401, `store.clearAll()` and `window.location.href = "/?redirect=" + pathname + search` so users re-authenticate and can return to the prior route.
- **`getRedirectUrlFriendly`:** Decodes query parameter values for safe redirect extraction (used by `handleRedirect`).

### `src/utils/config-loader.js`

- **`getPlatformConfig`:** Fetches `api.getPlatformConfig({ platform: "admin" })`, caches in `localStorage` with `BUILD_NUMBER` invalidation (except `development`).

### `src/utils/app-feature-utils.js`

- **`getAppFeatureProp`:** Resolves named props from CMS feature lists (`lodash` `find` by `name`).

### `src/utils/auth-listener.js`

- **`AuthenticationListener.execute`:** `window.onmessage` — JSON payloads with `isSleekSignPayload`: `Logout` clears store; `Login` sets `user_auth_token` from iframe message.

### `src/utils/logout-listener.js`

- **`execute`:** No-op (previous `storage`-based logout listener commented out).

### `src/layouts/browser-check-dialog.js`

- **UX guard:** Bowser-based unsupported-browser dialog; optional dismiss with `browserChecked` stored with expiry; customer support email from cached `platformConfig` localization.

### `src/views/index.css`

- Layout for `main.start`, login options (`.login-options`), cards, and responsive breakpoints for the sign-in shell.
