# Connect Xero OAuth (consent and callback)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Connect Xero OAuth (consent and callback) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User (user completes Xero consent; service stores tokens for automation) |
| **Business Outcome** | The platform holds valid Xero OAuth tokens so SleekBooks can call Xero Accounting APIs on behalf of connected organisations after a standard consent and redirect flow. |
| **Entry Point / Surface** | Xero SleekBooks HTTP API: `GET /xero/consent` builds the Xero consent URL and redirects the browser; after approval, Xero redirects to the app-registered callback, which must be handled by `GET /xero/callback` on this service (exchanges the URL for tokens). Exact Sleek App navigation path to start consent is not defined in these files. |
| **Short Description** | `XeroService` builds an `xero-node` `XeroClient` from `XERO_CLIENT_ID`, `XERO_CLIENT_SECRET`, `XERO_REDIRECT_URL`, and `XERO_SCOPES`. Consent returns a redirect URL; the callback passes `request.url` into `apiCallback`, then persists the token set to MongoDB. `initializeXeroConfig` loads that credential, refreshes expired access tokens, updates stored tokens, and resolves Xero tenants for subsequent API calls. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **External** — Xero OAuth 2.0 and Accounting API via `xero-node`. **Upstream** — env-configured redirect must match Xero app settings. **Related** — company UEN → Xero tenant resolution uses BigQuery (`xero_tenants`) elsewhere in `XeroService`; OAuth storage itself is a single credential document used for API access. **Downstream** — all authenticated Xero calls in this service flow through `initializeXeroConfig` (invoices, COA, migration, publishing, etc.). |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `xeroauthtokens` (Mongoose model `XeroAuthToken`; default pluralized collection name — not overridden in schema) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `storeTokenInDb` uses `findOne()` with no tenant key, implying a single global token document for the deployment—is that intentional for multi-company production, or should credentials be partitioned per org? Should `GET /xero/consent` and `GET /xero/callback` be protected or rate-limited beyond relying on Xero’s OAuth redirect? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/xero/xero.controller.ts`

- **`GET /xero/callback`** — `getXeroCallBackData`: `@ApiOperation` “Get CallBack data from XERO & Store in DB”; calls `xeroService.storeXeroData(request)`; returns JSON confirming token saved. **No `UseGuards`** on this route or on consent.
- **`GET /xero/consent`** — `generateConsentURL`: `@ApiOperation` “Get Consent URL from Xero”; `generateConsentURL` → redirect to consent URI.

### `src/xero/xero.service.ts`

- **`getXeroClient`**: constructs `XeroClient` with `clientId`, `clientSecret`, `redirectUris` from `XERO_REDIRECT_URL`, `scopes` from `XERO_SCOPES` (space-split).
- **`storeXeroData`**: reads `xeroData.url`, runs `getXeroClient()`, `xero.apiCallback(callbackUrl)`, then `storeTokenInDb(tokenSet)`.
- **`storeTokenInDb`**: `xeroAuthTokenModel.findOne()`; if document exists, `updateOne` with `$set` of token fields; else `create`. Single-row upsert pattern.
- **`generateConsentURL`**: `getXeroClient()`, `xero.buildConsentUrl()`.
- **`initializeXeroConfig`**: loads `xeroAuthTokenModel.findOne()`, builds `XeroClient`, `initialize`, `setTokenSet`, `readTokenSet`; on expiry, `refreshWithRefreshToken` and persist updated token set; `updateTenants(false)` for tenant resolution.

### `src/xero-auth-provider/schemas/xeroauthtoken.schema.ts`

- **`XeroAuthToken`** schema: `id_token`, `access_token`, `expires_at`, `token_type`, `refresh_token`, `scope`, `session_state`; `timestamps: true`.

### Other controller routes (context only)

- `GET /xero/company/:companyUEN` and `POST /xero/bulk-create-company-bank-accounts-from-bsm` use **`M2MAuthGuard`** — distinct from the unguarded OAuth consent/callback surface.
