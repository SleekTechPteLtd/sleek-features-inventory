# Continue SSO session

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Continue SSO session |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (browser) with an active Sleek Auth session cookie continuing the PKCE OAuth handoff without re-authenticating at the IdP |
| **Business Outcome** | Lets returning SAML/PKCE users skip another IdP round-trip when the session cookie is still valid, by redirecting straight to the client callback with a one-time authorization code |
| **Entry Point / Surface** | Form POST from the `authorize` view to `POST /sso/session/continue` on `sleek-auth` (body: `ContinueSessionDto`); excluded from Swagger (`@ApiExcludeEndpoint`). Requires signed HTTP-only cookie `sauth_session_token` (path allows this route via cookie config from `GET /sso/authorize`). |
| **Short Description** | Validates the encrypted `continue_token` against the PKCE context (`code_challenge`, `redirect_uri`, `country_code`, `state`), validates the client redirect URI for the tenant, verifies the ID-token JWT in `sauth_session_token` and loads the user profile from cache, then issues a short-lived challenge `code` and redirects to `redirect_uri` with `code` and `state`. If the session is missing or expired, throws `SessionExpiredError` (500 + `authorize-error` view). |
| **Variants / Markets** | SG, HK, UK, AU (via `TENANT`: SGP, HKG, GBR, AUS on `ContinueSessionDto.country_code`) |
| **Dependencies / Related Flows** | Upstream: `GET /sso/authorize` (sets cookie path for `/sso/session/continue`, supplies `continue_token` to the authorize template). Downstream: client app receives `code` on `redirect_uri`; `POST /sso/token` exchanges the code (PKCE) for access tokens. Uses `OauthConfigService` redirect allowlist, `validateRedirectUrl`, cache keys `auth:challenge:*` and `auth:session:{sessionIndex}`. |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None (session user profile is read from cache via JWT `sub` → `auth:session:{sessionIndex}`; challenge codes stored under `auth:challenge:{key}`; no MongoDB in this path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.controller.ts` — `@Post('/session/continue')` `continueSession`: reads `req.signedCookies['sauth_session_token']`, passes to `ssoService.continueSession` with `ContinueSessionDto`; on success `res.redirect(continue_uri)`; on error `res.status(500).render('authorize-error', ...)`.
- `src/modules/sso/sso.service.ts` — `continueSession(sessionToken, dto)`: `validateStatelessToken(dto.continue_token, { code_challenge, redirect_uri, country_code, state })`; `validateRedirectUrl(dto.redirect_uri, dto.country_code)`; `validateSessionToken(sessionToken)` (JWT verify with `id_token` config, profile from `cacheManager` `auth:session:${payload.sub}`); on success `generateChallengeToken` with `AuthChallenge` including `session_index: null` (no new server session row for this branch); returns `continue_uri` as `redirect_uri` with `code` and `state` query params; on missing session `throw new SessionExpiredError()`.
- `src/modules/sso/dto/continue-session.dto.ts` — extends `InitAuthBaseDto` with required `continue_token`.
- `src/modules/sso/dto/init-auth-dto.ts` — `InitAuthBaseDto` supplies `country_code`, `state`, `redirect_uri`, `code_challenge` for both init and continue flows.
