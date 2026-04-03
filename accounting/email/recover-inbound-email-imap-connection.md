# Recover inbound email IMAP connection

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Recover inbound email IMAP connection |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System |
| **Business Outcome** | Inbound receipt email can flow again after Gmail IMAP drops or OAuth tokens fail, without a full service redeploy. |
| **Entry Point / Surface** | **Operational / automation:** `POST /email/reinitialize-email-gateway` — re-runs the gateway’s module init to re-verify Google credentials and restart IMAP. **Automatic:** on `server:disconnected`, the gateway calls `verifyAuth()` to refresh tokens and reconnect. |
| **Short Description** | `EmailGateway` maintains an XOAUTH2 IMAP session to `imap.gmail.com` for the configured mailbox, parses inbound messages, and forwards them into the receipt pipeline. Operators or automation can call the reinitialize endpoint to repeat startup auth and client wiring after credential or connection problems; the gateway also attempts self-healing on disconnect. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Google** — OAuth tokens for `EMAIL_GATEWAY_CLIENT_ID` in `GoogleAuthCredentials`; token refresh via Google token endpoint. **Downstream** — `EmailForwarderService.sendEmailToReceipt`, `IncomingEmailReader.readEmailMessage`. **Infra** — Redis-backed `CacheUtility.acquireLock` on Message-ID for idempotent processing. **Related** — Google consent/OAuth routes in the same service for initial or renewed authorization. |
| **Service / Repository** | sleek-receipt-gateway |
| **DB - Collections** | `googleauthcredentials` (read in `verifyAuth`; `access_token` updated on refresh in `GoogleService.refreshAccessToken`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `POST /email/reinitialize-email-gateway` has no controller-level auth or `@ApiOperation` in code — confirm whether access is restricted by network policy, API gateway, or should be added; default Mongoose collection name for `GoogleAuthCredentials` assumed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/modules/email/email.controller.ts`

- **POST** `/email/reinitialize-email-gateway`: calls `this.emailGateway.onModuleInit()` (no return type / Swagger summary on this action; OpenAPI lists 201).

### `src/modules/email/gateway/email.gateway.ts`

- **`OnModuleInit`**: `onModuleInit` → `verifyAuth()` when `googleClientConfig` is present.
- **`verifyAuth`**: loads credentials via `googleService.getGoogleAuthCredentials(this.googleClientConfig.EMAIL_GATEWAY_CLIENT_ID)`; refreshes access token when expired; builds XOAUTH2 via `generateAuth2Token`; **`createImapClient()`** (host `imap.gmail.com`, port 993, TLS, `searchFilter` from `EMAIL_GATE_WAY_SEARCH_FILTERS`); **`start()`** or **`stop()`** on failure (logs ask for manual Google auth regeneration).
- **`server:disconnected`**: logs and **`await this.verifyAuth()`** to reconnect.
- **`message`**: random delay, **`cacheUtility.acquireLock(messageId)`**, `IncomingEmailReader.readEmailMessage`, **`emailForwarderService.sendEmailToReceipt`**.

### `src/modules/google/google.service.ts`

- **`getGoogleAuthCredentials`**: `googleAuthCredentialsModel.findOne({ client_id })`.
- **`refreshAccessToken`**: POST to `https://accounts.google.com/o/oauth2/token`; **`findOneAndUpdate`** on credentials with new `access_token`.

### `src/modules/google/models/google-auth-credentials.schema.ts`

- Mongoose model **`GoogleAuthCredentials`** — fields include `client_id`, `access_token`, `expiry_date`, `refresh_token`, `scope`, `token_type`, timestamps.

### `src/docs/openapi.yaml`

- Documents **`POST /email/reinitialize-email-gateway`** as `EmailController_reinitializeEmailGateway`.
