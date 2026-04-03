# Complete marketing account email verification

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Complete marketing account email verification |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospects and customers (signed-in marketing site users completing or checking email verification) |
| **Business Outcome** | Users can finish registration by consuming the email verification token, see clear verified vs unverified state, request another verification email when needed, and keep the SleekSign e-sign session aligned with the marketing app session (including a clean logout path). |
| **Entry Point / Surface** | **sleek-website** standalone page **`/verify/`** with optional query **`?token=…`** — webpack entry **`verify`** (`src/views/verify.js` → `verify/index.html`). Linked from signup and many gated flows when `registered_at` is unset (e.g. `window.location = "/verify/"`). |
| **Short Description** | On load, reads `token` from the query string and, when present, POSTs it to **`/users/verify-email`** as `registration_token`, then reloads the user profile. Shows **verified** when `user.registered_at` is set, otherwise **not verified** with the user’s email and a progressive disclosure path to **resend** verification (`POST /users/resend-verification-email`). Fetches **`/admin/users/me`** and companies for session context. **Log out** clears the marketing `store` and notifies SleekSign via a hidden iframe postMessage. **SleekSign** login sync runs in constructor and `componentDidMount` using `loginToSleekSignPlatform` against `SLEEK_SIGN_URL[window.location.host]` and `app_iframe` (see `pages/_default.layout.marko`). |
| **Variants / Markets** | **SG**, **HK** (SleekSign `security.html` URLs and host keys map `app.sleek.sg` / `app.sleek.hk` and equivalents); other markets **Unknown** unless backend restricts verification. |
| **Dependencies / Related Flows** | **Backend API** (sleek-back or equivalent): **`POST /users/verify-email`**, **`POST /users/resend-verification-email`**, **`GET /admin/users/me`** (`getUser`), **`GET companies`** (`getCompanies`). **SleekSign** cross-domain session sync via **`loginToSleekSignPlatform`** / **`logoutToSleekSignPlatform`** (`postMessage` to iframe `contentWindow` with `isSleekPayload`, `Login` / `Logout`). **Upstream**: transactional email with registration link containing `token`. **Downstream**: many admin and onboarding views redirect unverified users to **`/verify/`**. |
| **Service / Repository** | **sleek-website**: `src/views/verify.js`, `src/views/verify.css`, `src/utils/api.js` (`verifyUser`, `resendVerification`, `getUser`, `getCompanies`), `src/utils/login-to-sleeksign.js`, `src/utils/logout-to-sleeksign.js`, `src/utils/constants.js` (`SLEEK_SIGN_URL`), `pages/_default.layout.marko` (`#app_iframe`). **Backend** (not in this repo): user persistence, verification tokens, email send. |
| **DB - Collections** | **MongoDB** (backend only; not visible in sleek-website): **Unknown** — user / registration records updated when `registered_at` is set and email resend is triggered. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `verifyUser()` should run when `token` is absent (currently always calls `verifyUser()` after `fetchUser`; early return leaves `verifyUser` as rejected promise path). Whether failed verification should surface a user-visible error (errors are swallowed in `catch`). Exact backend contract for `registered_at` vs `verify-email` success. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/verify.js` (`VerifyView`)

- **Query**: `querystring.parse` → `this.verifyToken = query.token`.
- **Constructor**: Reads `store` `user_auth_token`, `company_id`, `platformConfig.country_code` as `tenantId`; **`loginToSleekSignPlatform(SLEEK_SIGN_URL[window.location.host], authToken, companyId, 'app_iframe', tenantId)`** (no callback).
- **`componentDidMount`**: `fetchUser()` → on success `verifyUser()`; `await fetchCompanies()`; second **`loginToSleekSignPlatform`** call (same args).
- **`fetchUser`**: **`api.getUser()`** — on failure sets `user: false`, redirects to **`/`**.
- **`verifyUser`**: If `!token` → `Promise.reject()`; else **`api.verifyUser({ body: JSON.stringify({ registration_token: this.verifyToken }) })`** → then **`fetchUser()`**; catch only clears loading.
- **UI**: `user.registered_at != null` → verified title; else unverified + optional resend (button after “Did you receive…” link). **`handleClickResendVerification`**: **`api.resendVerification()`** → success alert with email.
- **`handleClickLogOut`**: **`store.clearAll()`**, then **`logoutToSleekSignPlatform(SLEEK_SIGN_URL[window.location.host], 'app_iframe', () => window.location = "/")`**.

### `src/views/verify.css`

- Layout for **`main.verify`**: centered card, responsive padding; **`[data-verified="false"]`** spacing for copy and button.

### `src/utils/api.js`

- **`verifyUser`**: **`POST ${getBaseUrl()}/users/verify-email`**.
- **`resendVerification`**: **`POST ${getBaseUrl()}/users/resend-verification-email`**.
- **`getUser`**: **`GET ${getBaseUrl()}/admin/users/me`** (also initializes Intercom beacon when profile is `user`).

### `src/utils/login-to-sleeksign.js`

- **`loginToSleekSignPlatform`**: Sets iframe `src` to `domain`; on `load`, `postMessage` JSON with `key: 'storage'`, `method: "set"`, `data: { token, companyId, action: "Login", isSleekPayload: true, tenantId }` (token prefixed `Bearer ` when length > 36).

### `src/utils/logout-to-sleeksign.js`

- **`logoutToSleekSignPlatform`**: Same iframe pattern with `action: "Logout"`, then runs `callback`.

### Build / routing

- **`webpack/webpack.common.js`**: `verify/index.html` chunk **`verify`**.
- **`webpack/paths.js`**: `"verify": "./src/views/verify.js"`.
