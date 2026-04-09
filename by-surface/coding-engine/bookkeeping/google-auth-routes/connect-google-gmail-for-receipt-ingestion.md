# Connect Google Gmail for receipt ingestion

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Connect Google Gmail for receipt ingestion |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | A shared Gmail mailbox is authorized for `https://mail.google.com/` so Sleek Receipts can maintain an IMAP connection and turn inbound receipt emails into document events and downstream forwarding without manual token handling on every restart. |
| **Entry Point / Surface** | **OAuth redirect (Google → app):** `GET /google/auth-v2?code=…` — exchanges the authorization code, stores tokens, and starts the V2 IMAP client (redirect URI is region-specific, e.g. `…/sleekreceipts/google/auth-v2` in production ConfigMaps). **Operational re-init:** `GET /google/reinitialize-email-clients` with header `consent-auth` equal to server `RECEIPTS_CONSENT_AUTH` — stops the client, rebuilds `GoogleImapClient` from env, runs `initialize()`, returns JSON `{ emailClient2Url }` when a new OAuth URL is needed. |
| **Short Description** | `GoogleImapClient` drives offline OAuth with prompt consent, persists access/refresh tokens on the `GoogleAuthCredentials` document keyed by `client_id`, builds XOAUTH2 for `imap.gmail.com`, and `EmailClientV2` processes messages into receipt workflows (document events, forwarding, bank paths). The singleton from `getGoogleImapClientV2.js` is wired at app startup when `EMAIL_FORWARDING_V2_ENABLED` and existing refresh credentials allow reconnect without a new code. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | **Inbound email pipeline** — `EmailClientV2` uses `IncomingEmailReader`, `EmailForwarder`, `documentEventService`, `UserDetails`, Redis `acquireLock` for idempotency, tenant `features.email_client_async` / `document_submission_settings`. **Google** — OAuth2 token and refresh via `googleapis` / `google-auth-utils` (axios to Google token endpoint). **Process lifecycle** — `index.js` stops IMAP on exit signals. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `googleauthcredentials` (Mongoose model `GoogleAuthCredentials`; fields include `client_id`, `access_token`, `refresh_token`, `scope`, `expiry_date`, `token_type`, timestamps) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether product exposes the OAuth and reinitialize URLs or only infrastructure operators use them; `connectToImap` obtains the XOAUTH2 token via a callback while proceeding immediately to `EmailClientV2` — any race between `getToken` completion and `start()` is not clarified here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/routes/google-auth.js`

- **GET** `/auth-v2` (mounted at `/google` → `/google/auth-v2`): parses `code` from query; `stopImapClient()` on the module’s `emailClientV2` reference; `connectToImap(code, {})`; responds `{ message }`.
- **GET** `/reinitialize-email-clients`: protected by **`consentCheck`**; reads `RECEIPTS_EMAIL_CLIENT_ID_V2`, `RECEIPTS_EMAIL_CLIENT_SECRET_V2`, `RECEIPTS_REDIRECT_URI_V2`, `RECEIPTS_USER_EMAIL_V2`; stops client; if all set, `new GoogleImapClient({...})`, `initialize()`, returns `emailClient2Url` from client `url`.

### `src/middleware/google-auth-middleware.js`

- **`consentCheck`**: requires `RECEIPTS_CONSENT_AUTH`; compares to `req.headers["consent-auth"]`; 500 if server key missing, 403 if header missing, 400 if mismatch.

### `google-auth/main.js` (`GoogleImapClient`)

- **`initialize(existingCredentials)`**: builds `google.auth.OAuth2` with client id/secret/redirect; scope `https://mail.google.com/`; if no `existingCredentials`, `generateAuthUrl` with `access_type: "offline"`, `prompt: "consent"`, stores `this.url`.
- **`connectToImap(authenticationCode, existingCredentials)`**: `getToken(authenticationCode)` when code present; **`AUTH2CREDENTIALS.findOneAndUpdate({ client_id: CLIENT_ID }, { $set: tokens }, upsert)`**; creates `xoauth2` generator; instantiates **`EmailClientV2`**, **`start()`**.
- **`stopImapClient()`**: stops nested `emailClient`.

### `getGoogleImapClientV2.js`

- Single exported **`GoogleImapClient`** instance from env `RECEIPTS_*_V2` variables (same module re-required in `google-auth.js` for mutation on reinitialize).

### `src/email-client-v2.js` (`EmailClientV2`)

- IMAP to **`imap.gmail.com:993`** with XOAUTH2, `searchFilter` from `EMAIL_SEARCH_FILTERS`.
- On **`server:disconnected`**: loads refresh token from **`AUTH2CREDENTIALS`**, **`refreshAccessToken`**, updates access token in DB, recreates client or stops if refresh invalid (log points operators to `/google/reinitialize-email-clients`).
- On **`message`**: lock by Message-ID, **`IncomingEmailReader.readEmailMessage`**, bank vs receipt paths, **`documentEventService.createDocumentEvent`** when enabled, **`EmailForwarder.sendToReceiptBankOrHubdocV2`** / bank inbox / error handling.

### `src/schemas/google-auth-credentials.js`

- Mongoose schema for Google OAuth token fields and model name `GoogleAuthCredentials`.

### `index.js`

- **`app.use("/google", GoogleAuthRouter)`**; on listen, if **`EMAIL_FORWARDING_V2_ENABLED`**, loads credentials by `client_id`, **`initialize(existingCredentials)`**, **`connectToImap("", existingCredentials)`** when non-empty; **`require("./getGoogleImapClientV2")`** shared with route module.

### Regional deployment (redirect URIs)

- Kubernetes `configMap.yaml` files under `kubernetes/production-*` and `staging-*` set **`RECEIPTS_REDIRECT_URI_V2`** to region backend paths ending in **`/google/auth-v2`**, supporting **SG, HK, UK, AU** variants.
