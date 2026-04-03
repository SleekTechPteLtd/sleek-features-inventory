# Authorize IRAS CorpPass and manage access tokens

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Authorize IRAS CorpPass and manage access tokens |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Tax agent (CorpPass consent in browser), Integration / backend (M2M-secured consent URL and token retrieval) |
| **Business Outcome** | Singapore corporate tax flows can call IRAS APIs (for example Form CS submission) using valid CorpPass-derived access tokens stored per Sleek group, without exposing raw secrets in logs or at rest. |
| **Entry Point / Surface** | **API (sleek-iras-service)** — `GET /formcs-submission/consent` (M2M) returns or redirects to the IRAS consent URL; IRAS redirects to the configured callback hitting `GET /formcs-submission` with `state` and `code`; `GET /formcs-submission/token` (M2M) returns the decrypted bearer token for a `group`. Exact Sleek App navigation to start consent is not defined in these files. |
| **Short Description** | The service requests a CorpPass consent URL from IRAS using IBM API client credentials, ties OAuth `state` to a MongoDB document per `group`, exchanges `code` at `CorpPassToken`, and stores scope and token AES-256-GCM–encrypted with a rolling expiry. Callers fetch the token per `group` for downstream IRAS HTTP calls (for example `access_token` header on Form CS submit). |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **External** — IRAS `Authentication/CorpPassAuth` and `Authentication/CorpPassToken`, Form CS `ct/submitformcs` and related IRAS APIs. **Config** — `app.irasBaseUrl`, `app.irasScope`, `app.irasCallbackUrl`, `app.irasClientId`, `app.irasClientSecret`, `app.sleekServiceEncryptionkey`, `app.nodeEnv`. **Related** — Form CS submission reuses `getIrasToken` for authenticated posts. |
| **Service / Repository** | sleek-iras-service |
| **DB - Collections** | `irasauthtokens` (Mongoose model `IrasAuthToken`; default pluralized collection name — not overridden in schema) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /formcs-submission` (token exchange callback) is unguarded so IRAS can redirect the browser—should this be narrowed (referrer, signed state, rate limits)? `generateState` falls back to a hardcoded ObjectId string on error; is that safe for production? `POST /formcs-submission/:group` has no `M2MAuthGuard` in this controller—is that intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/formcs-submission/formcs-submission.controller.ts`

- **`GET /formcs-submission/consent`** — `@ApiOperation` “generates IRAS consent url”; **`M2MAuthGuard`**; query `tax_agent`, `group`, optional `redirect` — if consent succeeds and `redirect=true`, HTTP redirect to IRAS URL; else JSON `{ consentUrl }`; on failure `400` “Getting Consent URL Failed!”.
- **`GET /formcs-submission`** — `@ApiOperation` “generates IRAS Token”; **no guard** (OAuth callback from IRAS); query `state`, `code`, optional `debug`; calls `getTokenFromIras`; success JSON “Token updated Successfully!”, else `400` “Token update Failed!”.
- **`GET /formcs-submission/token`** — `@ApiOperation` “Get IRAS Token”; **`M2MAuthGuard`**; query `group`; returns JSON `{ token }` or `400` “Token Expired!”.
- **`POST /formcs-submission/:group`** — `@ApiOperation` “submit formcs to IRAS”; delegates to `formCsSubmission` (uses stored token internally; auth surface for this route not shown in snippet beyond absence of M2M guard).

### `src/formcs-submission/formcs-submission.service.ts`

- **`getConsentUrl`**: GET `${irasBaseUrl}/Authentication/CorpPassAuth` with scope, `callback_url`, `tax_agent`, `state` from `generateState(group)`; IBM client id/secret headers; `returnCode == 10` → `data.url`.
- **`generateState`**: `updateOne` upsert `{ group }`, then `findOne` by `group` and return `_id` as `state` (fallback ObjectId string on error).
- **`getGroupFromState`**: `findOne` by `_id` state → `group`.
- **`getTokenFromIras`**: resolves `group` from state; non-production `debug === "true"` short-circuit sets test tokens; else POST `${irasBaseUrl}/Authentication/CorpPassToken` with scope, callback, code, state; on success `setIrasToken` with scope and token from `response.data.data`.
- **`getIrasToken`**: `findOne({ group })`, rejects if missing or `expires_at` passed, returns **`aes.decrypt`** on stored `token`.
- **`setIrasToken`**: **`aes.encrypt`** on token, `expires_at` = now + 25 minutes; update or create by state/group.
- **`formCsSubmission`**: POST `${irasBaseUrl}/ct/submitformcs` with `access_token` header from `getIrasToken(group)`.

### `src/formcs-submission/iras-auth.schema.ts`

- **`IrasAuthToken`**: `code`, `state` (indexed), `group` (indexed), `scope`, `token`, `expires_at`; `timestamps: true`.

### `src/shared/lib/sleek-aes/aes.service.ts`

- **`SleekAesService`**: key from `app.sleekServiceEncryptionkey`; **`encrypt`** / **`decrypt`** using AES-256-GCM with PBKDF2-derived key (salt + IV + auth tag + ciphertext as base64).
