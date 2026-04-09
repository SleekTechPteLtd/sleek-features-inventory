# Submit Form CS to IRAS

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit Form CS to IRAS |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System, Finance User (submission and token flows are API-driven; consent/token retrieval routes use M2M auth) |
| **Business Outcome** | Corporate income tax Form CS filing data is transmitted to IRAS for a client group using a stored, encrypted IRAS access token tied to that group. |
| **Entry Point / Surface** | sleek-iras-service HTTP API: `POST /formcs-submission/:group` with `FormCsRequestDto` body submits to IRAS; OAuth-style consent and token maintenance live on `GET /formcs-submission/consent`, `GET /formcs-submission` (callback), `GET /formcs-submission/token`. Exact Sleek App or upstream service navigation path to these endpoints is not defined in these files. |
| **Short Description** | Loads the IRAS access token for the given `group` from MongoDB (decrypts with `SleekAesService`), rejects expired tokens, and POSTs the Form CS payload to IRAS `…/ct/submitformcs` with IBM client credentials and `access_token` header. Consent URL generation and token exchange persist encrypted tokens and metadata on `IrasAuthToken` documents keyed by `group` and OAuth `state`. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **External** — IRAS APIs: `Authentication/CorpPassAuth`, `Authentication/CorpPassToken`, `ct/submitformcs`; config: `app.irasBaseUrl`, `app.irasScope`, `app.irasCallbackUrl`, `app.irasClientId`, `app.irasClientSecret`. **Upstream** — CorpPass / IRAS consent and callback must complete before a valid token exists for submission. **Cross-repo** — callers that supply `group` and JSON body are not identified here. **Related** — AES encryption for tokens at rest (`SleekAesModule`). |
| **Service / Repository** | sleek-iras-service |
| **DB - Collections** | `irasauthtokens` (Mongoose model `IrasAuthToken`; default pluralized collection name — not overridden in schema) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST /formcs-submission/:group` has no `UseGuards` in the controller — is every caller expected to be network-trusted or is protection applied elsewhere (gateway, internal-only)? Non-production `debug=true` on token callback short-circuits with placeholder values — confirm this cannot be enabled in production deployments. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/formcs-submission/formcs-submission.controller.ts`

- **`GET /formcs-submission/consent`** — `@UseGuards(new M2MAuthGuard())`, `@ApiOperation` “generates IRAS consent url”; `getConsentUrl` → `formcsSubmissionService.getConsentUrl(query?.tax_agent, query?.group)`; optional redirect to IRAS consent URL or JSON `{ consentUrl }`.
- **`GET /formcs-submission`** — `@ApiOperation` “generates IRAS Token”; `generateToken` → `getTokenFromIras(query?.state, query?.code, query?.debug)`; **no M2M guard** (callback-style route).
- **`GET /formcs-submission/token`** — `@UseGuards(new M2MAuthGuard())`, `@ApiOperation` “Get IRAS Token”; `getIrasToken(query?.group)` returns decrypted token JSON or `400` “Token Expired!”.
- **`POST /formcs-submission/:group`** — `@ApiOperation` “submit formcs to IRAS”; `formCsSubmission(payload, params?.group)` → `200` with IRAS response data or `400` “Form CS Submission Failed!”; **no guards** on this handler in the file.

### `src/formcs-submission/formcs-submission.service.ts`

- **`formCsSubmission`**: builds URL `${irasBaseUrl}/ct/submitformcs`, obtains token via `getIrasToken(group)`, POSTs `payload` with headers `X-IBM-Client-Id`, `X-IBM-Client-Secret`, `access_token` (decrypted token). Success when `response?.data?.returnCode == 10`.
- **`getIrasToken`**: `irasAuthTokenModel.findOne({ group })`; throws if missing or `expires_at` not after now (`moment`); returns `aes.decrypt(irasAuthToken.token)`.
- **`getConsentUrl`**: `generateState(group)` then GET IRAS `…/Authentication/CorpPassAuth` with query params `scope`, `callback_url`, `tax_agent`, `state`; success `returnCode == 10` yields redirect `url`.
- **`generateState`**: `updateOne({ group }, { group }, { upsert: true })`, then `findOne({ group })`, returns `_id` as OAuth `state` string (fallback hard-coded ID on error).
- **`getTokenFromIras`**: resolves `group` via `getGroupFromState(state)`; non-production `debug === "true"` calls `setIrasToken` with `"test"` token; else POST `…/Authentication/CorpPassToken` with `scope`, `callback_url`, `code`, `state`; on success `setIrasToken` with real scope/token.
- **`setIrasToken`**: encrypts token with `aes.encrypt`, sets `expires_at` to now + 25 minutes, updates or creates `IrasAuthToken` by `_id` / state.

### `src/formcs-submission/dto/submission-request.dto.ts`

- **`FormCsRequestDto`**: `filingInfo` (`FilingInfo`: UEN, YA, contact, declarant ref, etc.), `declaration` (`Declaration`: boolean-like string flags for Form CS declarations), `dataFormCS` (`DataFormCs`: extensive P&L and tax line fields for Form CS data).

### `src/formcs-submission/iras-auth.schema.ts`

- **`IrasAuthToken`**: `code`, `state`, `group`, `scope`, `token`, `expires_at`; `timestamps: true`; indexes on `state` and `group`.

### `src/formcs-submission/formcs-submission.module.ts`

- Registers `MongooseModule.forFeature([{ name: IrasAuthToken.name, schema: IrasAuthTokenSchema }])`, `HttpModule`, `SleekAesModule`, `LoggerModule`.
