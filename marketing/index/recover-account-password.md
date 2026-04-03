# Recover account password

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Recover account password |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin and marketing-site users who have lost or forgotten credentials |
| **Business Outcome** | Users can request a password-reset email and complete a new password on a tokenized link so they regain access without operator intervention. |
| **Entry Point / Surface** | **sleek-website** root entry **`index`** (`webpack` chunk **`index`** → `src/views/index.js` / `index.html`). **Forgot password**: query **`?ft=forgot-password`** or **“Forgot password?”** from the email/password login card when Auth0 is off. **Reset password**: **`?ft=reset-password&token=…`** (token parsed in constructor). When **Auth0 Lock** is enabled, forgot-password is offered inside the Lock widget (CMS-configurable copy and `allowForgotPassword`). |
| **Short Description** | **Non-Auth0**: “Forgot password” collects email and **`POST`s** **`/users/forgot-password`**; success returns the user to the login form with a generic confirmation. **Reset** collects new and confirm password, attaches **`reset_password_token`** from the URL, validates match client-side, then **`POST`s** **`/users/reset-password`**; on success shows confirmation and redirects via **`handleRedirect()`** (respects safe `redirect` query); on failure surfaces support email. **Auth0**: platform config drives **`allowForgotPassword`** and Lock **`languageDictionary`** strings for forgot-password UX tied to Auth0’s hosted reset flow. |
| **Variants / Markets** | **SG** (production API default `https://api.sleek.sg`); other regions **Unknown** unless environment overrides `API_BASE_URL`. |
| **Dependencies / Related Flows** | **Backend API**: **`POST /users/forgot-password`**, **`POST /users/reset-password`** (email send and token validation happen server-side). **Auth0**: **`auth0-lock`**, CMS **`auth0`** / nested **`forgotPassword`** feature props (`enabled`, success message, instructions). **Related**: email/password **`logIn`** (`POST /users/login`), **`getUser`** / session redirect on existing token, SSO and Auth0 alternate login paths that bypass custom forms. |
| **Service / Repository** | **sleek-website**: `src/views/index.js` (`StartView`: `formType` `forgot-password` / `reset-password`, handlers, Auth0 Lock options), `src/utils/api.js` (`forgotPassword`, `resetPassword`). **Backend** (not in this repo): user store, reset tokens, transactional email. |
| **DB - Collections** | **MongoDB** (backend only; not visible in sleek-website): **Unknown** — reset tokens and password updates are persisted server-side. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact email template and link shape for the reset URL (frontend assumes `ft=reset-password` + `token`). Whether **`forgotPassword`** API errors are surfaced (handler always shows success path after `then`). Overlap vs Auth0-only tenants where custom forms never appear. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/index.js` (`StartView`)

- **Query routing**: `querystring.parse` → `formType` = `query.ft`; for `ft=reset-password`, `resetPasswordToken = query.token` (lines 57–70).
- **`renderForgotPassword`**: Shown when `formType === "forgot-password"`; form **`handleSubmitForgotPassword`** (lines 198–223).
- **`renderResetPassword`**: Shown when `formType === "reset-password"`; fields `new_password`, `confirm_password`; **`handleSubmitResetPassword`** (lines 226–258, 580–615).
- **`handleClickForgotPassword`**: Sets `formType` to **`forgot-password`** from login (lines 721–723).
- **`handleSubmitForgotPassword`**: **`api.forgotPassword`** with serialized email; then sets `formType` to **`login`**, opens alert with instructions copy (lines 562–577).
- **`handleSubmitResetPassword`**: Client check `new_password` vs `confirm_password`; adds **`reset_password_token`** from state; **`api.resetPassword`**; success **`handleRedirect`** via **`alertOnConfirm`**; failure shows support **`customer_support`** email from CMS localization (lines 580–615).
- **Auth0 Lock**: `componentDidMount` reads **`forgotPassword`** from CMS under **`auth0`** props; sets **`allowForgotPassword: isForgotPasswordEnabled`**, custom **`languageDictionary.success.forgotPassword`** and **`forgotPasswordInstructions`** (lines 374–446).

### `src/utils/api.js`

- **`forgotPassword`**: **`POST ${getBaseUrl()}/users/forgot-password`** (lines 233–235).
- **`resetPassword`**: **`POST ${getBaseUrl()}/users/reset-password`** (lines 238–240).

### Build / routing

- **`webpack/paths.js`**: **`"index": "./src/views/index.js"`** — root marketing login / password recovery shell.
