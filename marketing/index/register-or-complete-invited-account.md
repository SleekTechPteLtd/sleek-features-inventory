# Register or complete invited account

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Register or complete invited account |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | New or invited users (Sleek client type) completing account creation on the marketing site |
| **Business Outcome** | Prospects and invitees can create a Sleek account or finish registration tied to a server-issued registration token, accept legal terms, and land in the app (or email verification) without breaking the admin redirect flow. |
| **Entry Point / Surface** | **sleek-website** root **`/`** with query **`?ft=register`**; optional **`token`** when completing an invite (`?ft=register&token=…`). Optional **`email`** pre-fills the email field. Webpack entry **`index`** (`src/views/index.js` → `index.html`). Footer link “Create an account” sets register mode from login. |
| **Short Description** | **`StartView`** shows a “New Account” form (name, email, password, confirm password) with required acceptance of Terms & Conditions and Privacy Policy (URLs from CMS **`external_links`**). If **`token`** is present, **`checkRegistrationToken`** preloads the user; invalid or reused tokens show an error with support email. **Without token**: **`POST /users`** (`register`) then **`POST /users/login`**, then an alert directing the user to **`/verify/`** for email verification. **With token**: **`POST /users/update-and-verify`** (`updateAndVerifyUser`) then login, then success and **`handleRedirect()`** (default **`/admin/`** or safe `redirect` query). |
| **Variants / Markets** | Unknown — platform name and links come from **`getPlatformConfig`** / CMS; no market-specific branching in this view. |
| **Dependencies / Related Flows** | **Backend API** (`getBaseUrl()`, typically `https://api.sleek.sg` in production): **`POST /users`**, **`POST /users/login`**, **`POST /users/check-registration-token`**, **`POST /users/update-and-verify`**. **`GET /admin/users/me`** (`getUser`) when a session token exists to skip loading if already verified (`registered_at`). **Downstream**: **`/verify/`** for self-serve signup email verification ([complete marketing account email verification](../verify/complete-marketing-account-email-verification.md)). **CMS**: `cmsGeneralFeatureList` → `external_links` (terms, privacy), `localization` → support email. |
| **Service / Repository** | **sleek-website**: `src/views/index.js`, `src/views/index.css`, `src/utils/api.js` (`register`, `logIn`, `checkRegistrationToken`, `updateAndVerifyUser`, `getUser`), `src/utils/config-loader.js` / `getPlatformConfig`, `src/utils/constants.js` (`CLIENT_TYPE_DB_TEXT.SLEEK_CLIENT`), `src/utils/auth-utils.js` (`getRedirectUrlFriendly`). **Backend** (not in this repo): user records, registration tokens, verification. |
| **DB - Collections** | **MongoDB** (backend only; not visible in sleek-website): **Unknown** — user and registration-token persistence. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Invite completion path calls **`logIn`** with `{ email, password, clientType }` while other paths use **`client_type`** — confirm backend accepts the invite-login payload. Whether empty `registrationToken` with `ft=register` is intentionally “open signup” vs misconfiguration. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/index.js` (`StartView`)

- **Query parsing** (`constructor`): `querystring.parse` → `formType` (`ft`), `email`, `resetPasswordToken` when `ft=reset-password`, **`registrationToken`** when `ft=register` and `token` present.
- **`register` UI** (`renderRegisterForm`): If `registrationToken === false` (failed **`checkRegistrationToken`**), shows invalid-token copy and **`customer_support`** mailto. Otherwise form with **`accept_terms`** checkbox linking to **`termsLink`** / **`policyLink`** from state.
- **`componentDidMount`**: Loads **`getPlatformConfig`**; sets terms/policy from **`getAppFeatureProp(..., "external_links")`**; if `formType === "register"` and **`registrationToken`** is non-empty, **`api.checkRegistrationToken(token)`** → sets **`registrationUser`** and **`email`**; on catch sets **`registrationToken: false`**.
- **`handleSubmitRegister`**: Password match validation; strips **`accept_terms`** and **`confirm_password`**. **No token / false**: **`api.register`** with **`client_type: SLEEK_CLIENT`** → on success **`api.logIn`** → alert to verify email, **`alertOnConfirm` → `window.location = "/verify/"`**. **With token**: removes email from body, adds **`registration_token`**, **`api.updateAndVerifyUser`** → **`api.logIn`** → success alert, **`alertOnConfirm` → `handleRedirect()`** (uses **`getRedirectUrlFriendly("redirect")`** or **`DEFAULT_LANDING_PAGE`** `/admin/`).
- **Existing session**: If **`store.get("user_auth_token")`**, **`api.getUser()`** — if **`registered_at`** set, **`handleRedirect()`**; else clears loading spinner.

### `src/utils/api.js`

- **`register`**: **`POST ${getBaseUrl()}/users`**.
- **`logIn`**: **`POST ${getBaseUrl()}/users/login`**, stores **`auth_token`** in **`store`**.
- **`checkRegistrationToken`**: **`POST ${getBaseUrl()}/users/check-registration-token`** with body **`{ registration_token: token }`**.
- **`updateAndVerifyUser`**: **`POST ${getBaseUrl()}/users/update-and-verify`**.

### Build / routing

- **`webpack/paths.js`**: `"index": "./src/views/index.js"`.
- **`webpack/webpack.common.js`**: `index.html` chunk **`index`**.
