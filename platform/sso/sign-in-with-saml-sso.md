# Sign in with SAML SSO

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Sign in with SAML SSO |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | User (end user signing in via corporate IdP) |
| **Business Outcome** | Employees and approved users can authenticate with the organization’s SAML identity provider and return to Sleek client apps with a secure OAuth-style authorization code (PKCE), optional reuse of an existing Sleek session, and HTTP-only session cookies for follow-up steps. |
| **Entry Point / Surface** | Client application → redirect to Sleek Auth `GET /sso/authorize` with PKCE `code_challenge`, `state`, `redirect_uri`, and `country_code`; HTML flows for SAML postback and continuation; `POST /sso/token` for code exchange (documented in Swagger under SSO). |
| **Short Description** | Init validates the client redirect against CMS OAuth config and CORS; starts SAML via configured IdP (`SamlClient`). After IdP assertion, the service verifies the SAML response, maps profile and tenant groups, then issues encrypted challenge tokens and optional session cookies. Users complete PKCE at `/sso/token` to receive JWT access tokens; `UserService` provisions/syncs users per tenant via Sleek Back. Optional session reuse skips re-auth when a valid `sauth_session_token` cookie exists. |
| **Variants / Markets** | SG, HK, AU, UK (tenant codes `SGP`, `HKG`, `AUS`, `GBR` in code) |
| **Dependencies / Related Flows** | SAML IdP (`saml2-js` SP/IdP config); Sleek CMS app feature `oauth` (general) for allowed redirect URLs; `corsUrlsUtil` for tenant allowlists; Sleek Back API for user/group persistence; cache store for `auth:session:*` and `auth:challenge:*`; client apps implementing PKCE OAuth redirect. |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None in this service (sessions and PKCE challenges in application cache; user records via Sleek Back HTTP API, not MongoDB in-repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth — `SsoController` (`@Controller('sso')`, `@ApiTags('SSO')`)

- `GET /sso/authorize` — `@ApiExcludeEndpoint()`; calls `ssoService.initSaml` with `code_challenge`, `state`, `redirect_uri`, `country_code`, and `session_token` from signed cookie `sauth_session_token` (`InitAuthBaseDto`). Renders `authorize` with `login_url`, `continue_token`, optional `profile` for session reuse, `sauth_session_token` cookie when profile present (path scoped for `/sso/session/continue`). Errors render `authorize-error`.
- `GET /sso/logout` — clears `sauth_session_token`; renders `logout`.
- `POST /sso/session/continue` — `continueSession` with `ContinueSessionDto`; uses signed cookie; redirects to `continue_uri`.
- `POST /sso/token` — `@ApiOperation` summary “Login”; PKCE `CreateTokenDto`; JSON `access_token`, `expires_in`, `token_type`.
- `POST /sso/saml/callback` — SAML POST body; `handleSamlCallback` → renders `saml-continue` with challenge `token`.
- `POST /sso/saml/continue` — `continueSamlAuth`; sets `sauth_session_token` with path for `/sso/authorize`; redirects with `code` and `state` query params.

### sleek-auth — `SsoService`

- `initSaml` — `validateRedirectUrl`; stateless `continue_token` (encrypted payload: code_challenge, redirect_uri, country_code, state); `samlClient.generateAuthUrl()`; optional `validateSessionToken` for reuse (`auto_redirect: false` when session valid).
- `handleSamlCallback` — `samlClient.verifyResponse` → `generateChallengeToken<UserProfile>`.
- `continueSamlAuth` — validates stateless continue token and CSRF challenge token; `validateRedirectUrl`; `generateSessionToken`; `generateChallengeToken<AuthChallenge>` with `session_index` for new session; redirect URI with OAuth `code` and `state`.
- `continueSession` — reuse path: `validateSessionToken` with `session_index: null` in challenge to avoid new session init; `SessionExpiredError` if no profile in cache.
- `createToken` — `validateRedirectUrl`; `validateChallengeToken`; `Crypto.verifySha256` PKCE; `createSession` when `session_index` present; `generateAccessToken` → `getOrCreateUser` / `syncUserGroups` per `TENANT` via `UserService`.
- Cache keys: `auth:session:${sessionIndex}` (profile), `auth:challenge:${key}` (PKCE/challenge payloads); TTL from `auth.reconnect_buffer` / `session_buffer`.
- `getSessionCookieConfig` — signed, httpOnly, sameSite, secure from `cookies` config.

### sleek-auth — `SamlClient`

- `saml2-js` `ServiceProvider` / `IdentityProvider`; config from `saml` config (`entity_id`, `assert_endpoint`, certificates, `sso_login_url`, `sso_logout_url`, `provider`).
- `verifyResponse` — `post_assert` with `request_body`, `allow_unencrypted_assertion: true`; `serializeProfile` maps email, names, `group` attributes into per-tenant `groups` (`tenant.groupSlug` segments).

### sleek-auth — `OauthConfigService`

- `AppFeatureService` CMS: `getAppFeature('oauth', APP_FEATURE_CATEGORY.GENERAL)`; `getRedirectUrls()` from feature value `redirect_urls` for `validateRedirectUrl` (exact URL match + `corsUrlsUtil.checkIfAllowedInTenant`).
