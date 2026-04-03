# Complete SAML and redirect

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Complete SAML and redirect |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user completing SAML IdP sign-in in the browser |
| **Business Outcome** | Finishes the SAML leg of login by binding a session cookie and sending the user back to the client app with an OAuth-style authorization code for PKCE token exchange. |
| **Entry Point / Surface** | Browser POST to `POST /sso/saml/continue` (form post from `saml-continue` view after `POST /sso/saml/callback`); not exposed in Swagger (`@ApiExcludeEndpoint`). |
| **Short Description** | Validates encrypted continue token and PKCE-related fields, verifies the redirect URI for the tenant, consumes the CSRF challenge to recover the user profile, mints a session JWT and PKCE authorization `code`, sets the signed `httpOnly` `sauth_session_token` cookie, and redirects to `redirect_uri` with `code` and `state`. |
| **Variants / Markets** | SGP, HKG, AUS, GBR (`TENANT` on `country_code` in `SamlContinueDto` / `InitAuthBaseDto`) |
| **Dependencies / Related Flows** | Upstream: `POST /sso/saml/callback` (`handleSamlCallback`) and SAML init (`GET /sso/authorize` / `initSaml`). Downstream: client calls `POST /sso/token` with `code` and `code_verifier` (`createToken`), which may persist `auth:session:{sessionIndex}` in cache when `session_index` is present on the challenge. |
| **Service / Repository** | `sleek-auth` (`modules/sso/sso.controller.ts`, `modules/sso/sso.service.ts`); related DTOs `SamlContinueDto`, `InitAuthBaseDto`; `UserService` / `OauthConfigService` used indirectly inside `SsoService` for redirect validation and profile handling in other methods. |
| **DB - Collections** | None — ephemeral state in Nest cache manager (Redis): `auth:challenge:*` for CSRF/PKCE tokens; session profiles stored under `auth:session:*` after successful `createToken`, not in this handler. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Controller comment says cookie path scoped for authorize URL, but `getSessionCookieConfig` sets cookie `path` to `/` (verify intentional vs comment). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `sleek-auth` — `SsoController`

- `POST /sso/saml/continue` — `samlContinue`: calls `ssoService.continueSamlAuth(dto)`, then `getSessionCookieConfig` with `path: '/sso/authorize'`, sets `sauth_session_token` from `session_token.access_token`, returns `res.redirect(uri)` to the client application URL with query params. Errors render `authorize-error` with 500. `@ApiExcludeEndpoint()` (no public OpenAPI surface).

### `sleek-auth` — `SsoService.continueSamlAuth`

- Validates `continue_token` stateless encrypted payload against `code_challenge`, `redirect_uri`, `country_code`, `state` (`validateStatelessToken`).
- `validateRedirectUrl` — OAuth redirect allowlist via `OauthConfigService.getRedirectUrls` and `corsUrlsUtil.checkIfAllowedInTenant`.
- Loads user profile from `csrf_token` via `validateChallengeToken` (cache key `auth:challenge:*`, one-time delete).
- `generateSessionToken` — JWT (id-token config) for session; `generateChallengeToken` builds PKCE `code` with `AuthChallenge` including `session_index` for new sessions.
- Returns `{ uri: redirect_uri?code&state, session_token }` for controller to set cookie and redirect.

### Configuration touched at runtime

- `cookies` config: `signed`, `httpOnly`, `sameSite`, `secure` defaults (`CookiesConfig` in `sso.service.ts` constructor).
- `auth`, `jwt`, `id_token` config for token lifetimes and signing (see `SsoService` constructor).

### Related files (DTOs / views)

- `src/modules/sso/dto/saml-continue.dto.ts` — `csrf_token`, `continue_token`, plus `InitAuthBaseDto`: `country_code`, `state`, `redirect_uri`, `code_challenge`.
- SAML callback renders `saml-continue` with challenge `token` consumed by the continue step (controller `samlCallback`).
