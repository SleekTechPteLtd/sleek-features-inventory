# Connect Xero accounting integration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Connect Xero accounting integration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | The service holds valid Xero OAuth tokens so bookkeeping and automation flows can call Xero APIs (invoices, accounts, publishing) without manual secret handling per request. |
| **Entry Point / Surface** | Sleek Receipts HTTP API: `GET /xero/consent` returns a Xero OAuth consent URL; user completes consent in Xero; Xero redirects to the configured callback, which must hit `GET /xero/authenticate` with the OAuth query string. Routes are mounted at `/xero` in `index.js`. `src/routes/xero-auth.js` has `// TODO: middleware` — no auth middleware is applied in code. |
| **Short Description** | Builds a Xero `XeroClient` from env (`XERO_CREDENTIALS`, `XERO_REDIRECT_URI`, `XERO_SCOPES`, `XERO_STATE`), returns the consent URL for the first step, then exchanges the callback URL for tokens via `apiCallback`, persisting the token set to MongoDB. A single credential document is upserted (`findOne` then update or create). `initializeXero` in `xero-utilities.js` loads that credential for downstream API use and refreshes expired access tokens. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Downstream** — `initializeXero()` in `src/xero/xero-utilities.js` supplies an authenticated client for scripts such as `src/scripts/get-xero-client-invoices.js`. **Related** — company-level Xero org linkage is handled separately (e.g. company settings / third-party ids); this flow only stores app-level OAuth tokens. **External** — Xero OAuth 2.0 (`xero-node` `XeroClient`). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `xeroauthcredentials` (Mongoose model `XeroAuthCredential`; default pluralized collection name — not overridden in schema) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is a single global `XeroAuthCredential` document (no company or tenant key) intentional for this deployment, or should tokens be partitioned per org? What middleware or network controls are planned for `/xero/consent` and `/xero/authenticate`? Should `generateAuthToken` return a payload to the browser (service returns `undefined` after persist)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `index.js`

- **`app.use("/xero", XeroAuthRouter)`** — base path `/xero` for all Xero auth routes.

### `src/routes/xero-auth.js`

- **GET** `/consent` → `generateConsentUrl`
- **GET** `/authenticate` → `generateAuthToken`
- Comment: **`// TODO: middleware`**

### `src/controllers/xero-auth.controller.js`

- **`generateConsentUrl`**: calls `xeroAuthService.generateConsentUrl()`, responds with `XERO_AUTH_CODES.GENERATE_CONSENT_URL`
- **`generateAuthToken`**: passes **`req.url`** as `callbackUrl` to `xeroAuthService.generateAuthToken(callbackUrl)`; responds with `XERO_AUTH_CODES.GENERATE_AUTH_TOKEN`

### `src/services/xero-auth.service.js`

- **`generateConsentUrl`**: `initializeXeroConfigs()` → `xero.buildConsentUrl()` → `{ url: consentUrl }`
- **`generateAuthToken(callbackUrl)`**: `initializeXeroConfigs()` → `xero.apiCallback(callbackUrl)` → **`XeroAuthCredential.findOne()`**; if exists, `updateOne` with `$set: { ...tokenSet }`; else **`XeroAuthCredential.create({ ...tokenSet })`**

### `src/xero/xero-utilities.js`

- **`initializeXeroConfigs`**: reads **`XERO_CREDENTIALS`** JSON from env (first key = `client_id`, value = `client_secret`), **`XERO_REDIRECT_URI`**, **`XERO_SCOPES`** (space-split), **`XERO_STATE`**; constructs `xero-node` **`XeroClient`**
- **`initializeXero`**: loads **`XeroAuthCredential.findOne()`**, `xero.setTokenSet`, **`tokenSet.expired()`** then **`refreshWithRefreshToken`** and persists updated token set to the same collection

### `src/schemas/xero-auth-credential.js`

- Fields aligned with OAuth token set: `id_token`, `access_token`, `expires_at`, `token_type`, `refresh_token`, `scope`, `session_state`; **timestamps** enabled

### `src/constants/success-message.js`

- **`XERO_AUTH_CODES`**: `GENERATE_CONSENT_URL`, `GENERATE_AUTH_TOKEN` with success messages for HTTP 200 responses
