# Authorize Google for Gmail receipt gateway

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Authorize Google for Gmail receipt gateway |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | The receipt gateway can store and refresh Gmail OAuth credentials so it can read receipt mail on behalf of the configured mailbox without manual token entry on each run. |
| **Entry Point / Surface** | **Start consent:** `GET /google/generate-consent-url` — server responds with **redirect** to Google’s OAuth consent URL (scope `https://mail.google.com/`, offline access, prompt consent). **Callback:** `GET /google/authenticate?code=…` — reads `code` from the query string, exchanges it for tokens, persists them, returns JSON `{ message }`. Intended for operator-driven or infrastructure-triggered flows rather than an in-app screen in this service. |
| **Short Description** | NestJS `GoogleController` exposes two routes: one builds the OAuth2 consent URL via `googleapis` `OAuth2.generateAuthUrl`, the other accepts Google’s redirect with an authorization code and calls `GoogleService.saveAuthentication` to exchange the code and upsert token fields into MongoDB. `GoogleService` also supports refreshing access tokens and XOAUTH2-style token generation for mail access, keyed by configured `EMAIL_GATEWAY_CLIENT_ID`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Google** — OAuth2 token exchange and refresh against `accounts.google.com` and Google APIs (`googleapis`, axios). **Related product** — Receipt ingestion stacks (e.g. sleek-receipts Gmail/IMAP flows) may parallel this pattern; this repo is the **sleek-receipt-gateway** Nest app. **Downstream** — Any mail-reading or forwarding that relies on stored `GoogleAuthCredentials`. |
| **Service / Repository** | sleek-receipt-gateway |
| **DB - Collections** | `googleauthcredentials` (Mongoose model `GoogleAuthCredentials` on connection `SLEEK_RECEIPT_GATEWAY`; fields include `client_id`, `access_token`, `refresh_token`, `scope`, `expiry_date`, `token_type`, timestamps) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Controller routes have **no auth guards** in code — confirm network/policy restrictions for production. **Variants / markets** depend on deployment env (`EMAIL_GATEWAY_REDIRECT_URI`, etc.) and are not encoded in these files. Whether `generateAuth2Token`’s async `xoauth2` callback is safe for callers expecting a synchronous return value is not fully clear from usage sites alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/modules/google/google.controller.ts`

- **`GoogleController`** base path **`/google`**.
- **GET** `authenticate`: parses `code` from `req.url` via `url.parse`; on success calls `googleService.saveAuthentication(parsedUrl.code)`; responds `{ message }` (`Successful Authentication` or error/`Missing authentication code`).
- **GET** `generate-consent-url`: returns **`res.redirect(consentURL)`** where `consentURL = googleService.generateConsentURL()` (not JSON).

### `src/modules/google/google.service.ts`

- **`GoogleService`**: loads `EMAIL_GATEWAY_CLIENT_ID`, `EMAIL_GATEWAY_CLIENT_SECRET`, `EMAIL_GATEWAY_REDIRECT_URI`, `EMAIL_GATEWAY_USER_EMAIL` from config; constructs `google.auth.OAuth2` client.
- **`generateConsentURL`**: scopes `['https://mail.google.com/']`; `generateAuthUrl` with `access_type: 'offline'`, `prompt: 'consent'`.
- **`saveAuthentication`**: `getToken(authenticationCode)`, `setCredentials(tokens)`, **`findOneAndUpdate`** on `googleAuthCredentialsModel` with filter `{ client_id: EMAIL_GATEWAY_CLIENT_ID }`, `$set: tokens`, **upsert**.
- **`refreshAccessToken`**: POST to Google token endpoint with `refresh_token`, updates `access_token` on the same `client_id` document.
- **`getGoogleAuthCredentials`**: `findOne({ client_id })`.
- **`generateAuth2Token`**: `xoauth2.createXOAuth2Generator` with user email and tokens (async callback sets token).

### `src/modules/google/models/google-auth-credentials.schema.ts`

- Mongoose schema **`GoogleAuthCredentials`**: `client_id`, `access_token`, `expiry_date`, `refresh_token`, `scope`, `token_type` (all required in schema).

### `src/modules/google/google.module.ts`

- Registers **`GoogleAuthCredentials`** with **`DBConnectionName.SLEEK_RECEIPT_GATEWAY`**.
