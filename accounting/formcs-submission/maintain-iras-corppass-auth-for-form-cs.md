# Maintain IRAS CorpPass authentication for Form CS

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Maintain IRAS CorpPass authentication for Form CS |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (IRAS OAuth callback); integrated services via M2M for consent URL and token retrieval |
| **Business Outcome** | Each Sleek group can complete IRAS CorpPass consent once and retain usable access tokens so Form CS and other IRAS calls can run without re-authenticating on every submission. |
| **Entry Point / Surface** | **sleek-iras-service** HTTP API: `GET /formcs-submission/consent` (M2M) returns or redirects to IRAS CorpPass consent URL; browser completes CorpPass at IRAS; IRAS redirects to the configured callback, which hits `GET /formcs-submission` with `state` and `code` to exchange for tokens; callers use `GET /formcs-submission/token` (M2M) to read a valid access token for a `group`. Exact Sleek App or operator UI path that starts consent is not defined in these files. |
| **Short Description** | The service calls IRAS `Authentication/CorpPassAuth` with scope, callback URL, tax agent flag, and an opaque `state` derived from a per-group MongoDB document. After CorpPass, IRAS invokes the callback; `getTokenFromIras` posts to `Authentication/CorpPassToken` with `code` and `state`, then stores scope, encrypted token, and expiry (25 minutes) on the `IrasAuthToken` record. `getIrasToken` decrypts the stored token and rejects expired credentials; Form CS submission reuses that token as the `access_token` header on IRAS `/ct/submitformcs`. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **External** — IRAS APIs (`app.irasBaseUrl`): `Authentication/CorpPassAuth`, `Authentication/CorpPassToken`, and downstream `POST .../ct/submitformcs` (uses the same token). **Config** — `irasClientId`, `irasClientSecret`, `irasScope`, `irasCallbackUrl`, `irasBaseUrl`. **Internal** — `SleekAesService` encrypts tokens at rest. **Related** — Form CS POST `POST /formcs-submission/:group` depends on valid stored CorpPass tokens for that group. |
| **Service / Repository** | sleek-iras-service |
| **DB - Collections** | `irasauthtokens` (Mongoose model `IrasAuthToken`; default pluralized collection name — not overridden in schema) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /formcs-submission` (OAuth callback) has no auth guard — is callback URL validation at IRAS sufficient? Is there a refresh flow when tokens expire after ~25 minutes, or must operators re-consent? `generateState` falls back to a hardcoded ObjectId string on error — is that legacy/test-only? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/formcs-submission/formcs-submission.controller.ts`

- **`GET /formcs-submission/consent`** — `@ApiOperation` “generates IRAS consent url”; **`M2MAuthGuard`**; query `tax_agent`, `group`; optional `redirect` (default `true`) — either HTTP redirect to IRAS consent URL or JSON `{ consentUrl }`; failure → 400.
- **`GET /formcs-submission`** — `@ApiOperation` “generates IRAS Token”; **no guard**; query `state`, `code`, `debug`; calls `getTokenFromIras`; success → 200 `{ message: 'Token updated Successfully!' }`; failure → 400.
- **`GET /formcs-submission/token`** — `@ApiOperation` “Get IRAS Token”; **`M2MAuthGuard`**; query `group`; returns `{ token }` or 400 “Token Expired!”.
- **`POST /formcs-submission/:group`** — `@ApiOperation` “submit formcs to IRAS”; uses service `formCsSubmission` (depends on `getIrasToken` for bearer-style access).

### `src/formcs-submission/formcs-submission.service.ts`

- **`getConsentUrl`**: GET `${irasBaseUrl}/Authentication/CorpPassAuth` with IBM client id/secret headers; `state` from `generateState(group)`; on `returnCode == 10`, returns `data.url`.
- **`generateState`**: `updateOne` upsert by `group`, then `findOne`; returns `_id` as string (or hardcoded fallback on error).
- **`getGroupFromState`**: `findOne` by `_id` == `state`, returns `group`.
- **`getTokenFromIras`**: resolves `group` from state; non-production `debug=true` short-circuit stores test tokens; otherwise POST `${irasBaseUrl}/Authentication/CorpPassToken` with scope, callback_url, code, state; on success calls `setIrasToken` with encrypted token via `aes.encrypt`.
- **`getIrasToken`**: `findOne({ group })`; throws if missing or `expires_at` not after now; returns `aes.decrypt(token)`.
- **`setIrasToken`**: `updateOne` or `create` with encrypted `token`, `expires_at` = now + 25 minutes.
- **`formCsSubmission`**: POST `${irasBaseUrl}/ct/submitformcs` with header `access_token` from `getIrasToken(group)`.

### `src/formcs-submission/iras-auth.schema.ts`

- **`IrasAuthToken`**: `code`, `state` (indexed), `group` (indexed), `scope`, `token`, `expires_at`; `timestamps: true`. (Exported document type is misnamed `AuditLogDocument` — naming inconsistency only.)

### `src/formcs-submission/formcs-submission.module.ts`

- Registers `MongooseModule.forFeature([{ name: IrasAuthToken.name, schema: IrasAuthTokenSchema }])`, `HttpModule`, `SleekAesModule`.
