# Submit corporate tax Form CS to IRAS

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit corporate tax Form CS to IRAS |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Corporate income tax return data (Form CS) is delivered to IRAS so the company meets Singapore filing obligations and national tax authority records stay current. |
| **Entry Point / Surface** | **HTTP API (sleek-iras-service):** `POST /formcs-submission/:group` with `FormCsRequestDto` body (filing info, declaration, Form CS line items). **Prerequisite flows (same controller):** `GET /formcs-submission/consent` (M2M) for IRAS CorpPass consent URL; `GET /formcs-submission` OAuth callback to exchange `code`/`state` for tokens; `GET /formcs-submission/token` (M2M) to read stored token. Integrated callers (e.g. accounting/compliance automation) supply `group` and payload. |
| **Short Description** | Accepts a structured Form CS payload (`filingInfo`, `declaration`, `dataFormCS`), resolves a decrypted IRAS access token for the tenant `group` from MongoDB (with expiry check), and POSTs to IRAS `…/ct/submitformcs` with IBM client credentials and `access_token` header. Returns IRAS response when `returnCode == 10`; otherwise logs and returns failure to the client. Token lifecycle and CorpPass consent are handled in the same module. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **External:** IRAS APIs — `Authentication/CorpPassAuth`, `Authentication/CorpPassToken`, `ct/submitformcs` (base URL from `app.irasBaseUrl`). **Same service:** `SleekAesService` encrypts/decrypts stored tokens; `ConfigService` (`app.irasBaseUrl`, `app.irasScope`, `app.irasCallbackUrl`, `app.irasClientId`, `app.irasClientSecret`, `app.nodeEnv`). **Upstream:** CorpPass consent and callback must complete before submission can use a valid token. |
| **Service / Repository** | sleek-iras-service |
| **DB - Collections** | `irasauthtokens` (Mongoose model `IrasAuthToken`: `group`, `state`, `code`, `scope`, encrypted `token`, `expires_at`; used for OAuth state, token storage, and lookup by `group` for submission) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST /formcs-submission/:group` declares no route guard in the controller (unlike `GET …/consent` and `GET …/token` which use `M2MAuthGuard`); confirm whether access is enforced at gateway, network, or is an oversight. Non-production `debug=true` path in `getTokenFromIras` stores test tokens — confirm it cannot run in production. Whether the OpenAPI tag `openapi-tag-sleek-iras-service` is declared in a separate spec bundle is not verified from these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/formcs-submission/formcs-submission.controller.ts`

- **`GET /formcs-submission/consent`** — `M2MAuthGuard`; `@ApiOperation` “generates IRAS consent url”; optional `redirect`, `tax_agent`, `group`; redirects or returns JSON `consentUrl`.
- **`GET /formcs-submission`** — `@ApiOperation` “generates IRAS Token”; query `state`, `code`, `debug`; success JSON or 400.
- **`GET /formcs-submission/token`** — `M2MAuthGuard`; `@ApiOperation` “Get IRAS Token”; query `group`; returns `token` or 400 “Token Expired!”.
- **`POST /formcs-submission/:group`** — `@ApiOperation` “submit formcs to IRAS”; body `FormCsRequestDto`; delegates to `formCsSubmission`.

### `src/formcs-submission/formcs-submission.service.ts`

- **`formCsSubmission`:** `POST` `${irasBaseUrl}/ct/submitformcs` with `getIrasToken(group)`, headers `X-IBM-Client-Id`, `X-IBM-Client-Secret`, `access_token`; success when `response?.data?.returnCode == 10`.
- **`getIrasToken`:** `findOne({ group })`, rejects missing or expired token (`expires_at` vs now), returns `aes.decrypt(irasAuthToken.token)`.
- **`getConsentUrl` / `getTokenFromIras` / `setIrasToken`:** CorpPass OAuth against IRAS `Authentication/CorpPassAuth` and `Authentication/CorpPassToken`; `generateState` / `getGroupFromState` use `irasAuthTokenModel` for state ↔ group mapping.
- **`HttpService` (Axios)** for all IRAS HTTP calls.

### `src/formcs-submission/dto/submission-request.dto.ts`

- **`FormCsRequestDto`:** `filingInfo` (`FilingInfo`: UEN, YA, contact, declarant ref, etc.), `declaration` (`Declaration`: boolean flags as strings), `dataFormCS` (`DataFormCs`: revenue, P&L, deductions, donations, R&D, and other Form CS fields as strings).

### `src/formcs-submission/iras-auth.schema.ts`

- **`IrasAuthToken`:** `code`, `state`, `group`, `scope`, `token`, `expires_at`; timestamps enabled.

### `src/formcs-submission/formcs-submission.module.ts`

- Registers `FormcsSubmissionController`, `FormcsSubmissionService`, `MongooseModule.forFeature([IrasAuthToken])`, `HttpModule`, `SleekAesModule`.
