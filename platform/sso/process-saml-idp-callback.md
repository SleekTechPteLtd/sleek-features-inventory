# Process SAML IdP callback

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Process SAML IdP callback |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (SAML IdP browser POST back to assert endpoint) |
| **Business Outcome** | Completes the SAML assertion step by verifying the IdP response and issuing a short-lived encrypted continuation token so the browser can proceed to the next SSO step without exposing raw profile data in the redirect. |
| **Entry Point / Surface** | `sleek-auth` HTTP API: `POST /sso/saml/callback` (form/body consumed by SAML library; not an in-app navigation path — follows IdP redirect after user signs in) |
| **Short Description** | Accepts the SAML POST body, verifies the assertion via `saml2-js`, maps attributes to `UserProfile`, stores that profile under a one-time challenge key in cache, and returns an HTML view that embeds the encrypted continuation token for the next browser step (`saml-continue` template). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: `GET /sso/authorize` (`initSaml`) prepares redirect and stateless `continue_token`. External: configured SAML IdP (`SamlConfig` — e.g. JumpCloud). Downstream: `POST /sso/saml/continue` consumes `continue_token` and `csrf_token` (challenge) to complete PKCE-style handoff. Related: `SamlClient.verifyResponse` → `UserService` not invoked on this path (user sync happens later in token exchange). |
| **Service / Repository** | `sleek-auth` — `src/modules/sso/sso.controller.ts`, `sso.service.ts`, `clients/saml.client.ts`, `clients/saml.interface.ts`, view `saml-continue` (rendered by controller) |
| **DB - Collections** | N/A — profile is held in cache only for the challenge token (`auth:challenge:*`); no MongoDB write on this path |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `SamlRequestBody` types the body field as `SAMLRequest`; SAML POST-back assertions are usually named `SAMLResponse` in the spec — confirm naming matches runtime IdP payloads and saml2-js expectations, or none if intentional. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `sso.controller.ts`

- `POST /sso/saml/callback` — `@ApiExcludeEndpoint()` (not in public Swagger surface).
- `@Body() dto: SamlRequestBody` passed to `this.ssoService.handleSamlCallback(dto)`.
- Success: `res.render('saml-continue', { token: token })` — HTML response carrying the continuation token for the next step.
- Failure: `500` + `authorize-error` template with trace id from `requestTracerUtil`.

### `sso.service.ts`

- `handleSamlCallback(dto)` — `const profile = await this.samlClient.verifyResponse(dto)`; `const token = this.generateChallengeToken<UserProfile>(profile)`; returns `{ token }`.
- `generateChallengeToken` — stores payload at `auth:challenge:${key}` with `reconnect_buffer` TTL, encrypts `key` with `Crypto`, URL-encodes — this is the continuation/challenge token passed to the view.
- On error from verify path: logs and throws `AuthenticationError()` (generic failure).

### `clients/saml.client.ts`

- `verifyResponse(requestBody)` — `serviceProvider.post_assert(identityProvider, { request_body: requestBody, allow_unencrypted_assertion: true }, callback)` (saml2-js).
- On success: `serializeProfile` builds `UserProfile` from SAML user (`session_index`, email, names, `group` attributes parsed into per-tenant group slugs via `tenant.group` naming).

### `clients/saml.interface.ts`

- `SamlRequestBody` — documents the expected body shape for the callback DTO.
