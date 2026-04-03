# Connect Google Gmail for receipt gateway

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Connect Google Gmail for receipt gateway |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators authorize a shared Gmail mailbox via Google OAuth so the receipt gateway can keep IMAP access to Gmail for receipt-related mail without re-entering credentials on every deploy or token expiry. |
| **Entry Point / Surface** | **Start OAuth:** `GET /google/generate-consent-url` — HTTP redirect to Google’s consent screen (scope `https://mail.google.com/`, offline access, prompt consent). **Callback:** `GET /google/authenticate?code=…` — exchanges the authorization code and persists tokens. No Nest guards or API decorators on these routes in code; treat as operator or infrastructure-facing URLs behind network controls. |
| **Short Description** | `GoogleService` wraps `googleapis` OAuth2 with env-based client id/secret/redirect and mailbox email; stores access and refresh tokens on `GoogleAuthCredentials` keyed by `client_id`. On startup, `EmailGateway` loads credentials from MongoDB, refreshes expired access tokens, builds an XOAUTH2 string for `imap.gmail.com`, and runs the IMAP client to process inbound messages into the receipt email pipeline (with Redis-backed message locking). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Downstream:** `EmailGateway` (`email.gateway.ts`) — IMAP to Gmail, `IncomingEmailReader`, `EmailForwarderService.sendEmailToReceipt`, Redis `acquireLock` for Message-ID idempotency. **External:** Google OAuth token endpoint (`accounts.google.com/o/oauth2/token`), Gmail IMAP. **Config:** `EMAIL_GATEWAY_CLIENT_ID`, `EMAIL_GATEWAY_CLIENT_SECRET`, `EMAIL_GATEWAY_REDIRECT_URI`, `EMAIL_GATEWAY_USER_EMAIL`, `EMAIL_GATE_WAY_SEARCH_FILTERS`. |
| **Service / Repository** | sleek-receipt-gateway |
| **DB - Collections** | `googleauthcredentials` (Mongoose model `GoogleAuthCredentials` on connection `SLEEK_RECEIPT_GATEWAY`; fields `client_id`, `access_token`, `refresh_token`, `scope`, `expiry_date`, `token_type`, timestamps) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GoogleController.authenticate` calls `saveAuthentication` without `await`, so the HTTP response may return before persistence finishes; `generateAuth2Token` uses `xoauth2`’s async `getToken` but returns `xoAuthToken` synchronously (possible race before IMAP uses the token). Whether these URLs are exposed beyond internal ops is not defined in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/modules/google/google.controller.ts`

- **`GoogleController`** — base path `google`.
- **GET** `authenticate`: reads `code` from the request URL query (`url.parse`); on success calls `GoogleService.saveAuthentication`, responds JSON `{ message }` (`Successful Authentication` / errors). No auth guard.
- **GET** `generate-consent-url`: returns redirect to `GoogleService.generateConsentURL()`.

### `src/modules/google/google.service.ts`

- **`GoogleService`**: constructs `google.auth.OAuth2` from `EMAIL_GATEWAY_*` config; injects `googleAuthCredentialsModel` for `SLEEK_RECEIPT_GATEWAY`.
- **`generateConsentURL`**: scope `https://mail.google.com/`, `access_type: 'offline'`, `prompt: 'consent'`, `generateAuthUrl`.
- **`saveAuthentication`**: `getToken(authenticationCode)`, `setCredentials`, `findOneAndUpdate` with filter `{ client_id: EMAIL_GATEWAY_CLIENT_ID }`, `$set: tokens`, upsert.
- **`getGoogleAuthCredentials`**: `findOne({ client_id })`.
- **`refreshAccessToken`**: POST to Google token endpoint with refresh token; updates `access_token` on the same `client_id` document.
- **`generateAuth2Token`**: `xoauth2.createXOAuth2Generator` with user email and tokens for IMAP SASL.

### `src/modules/google/models/google-auth-credentials.schema.ts`

- **`GoogleAuthCredentials`**: Mongoose `@Schema({ timestamps: true })` with required string/number fields for OAuth token bundle and `client_id`.

### `src/modules/google/google.module.ts`

- Registers `GoogleAuthCredentials` schema on `DBConnectionName.SLEEK_RECEIPT_GATEWAY`; provides `GoogleController`, `GoogleService`.

### `src/modules/email/gateway/email.gateway.ts`

- **`EmailGateway`**: on `onModuleInit`, `verifyAuth` loads credentials via `getGoogleAuthCredentials(EMAIL_GATEWAY_CLIENT_ID)`, compares expiry to refresh or reuse access token, calls `generateAuth2Token`, creates `simple-node-imap-async` client to `imap.gmail.com:993`, `start()`; on disconnect, `verifyAuth` again; on `message`, lock + `IncomingEmailReader.readEmailMessage` + `EmailForwarderService.sendEmailToReceipt`.
