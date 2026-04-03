# Start SAML authorize flow

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Start SAML authorize flow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (browser) initiating SAML SSO |
| **Business Outcome** | Begins the SAML login path so users can authenticate via the configured IdP and continue the PKCE-style OAuth flow back to the client app |
| **Entry Point / Surface** | Browser navigation to `GET /sso/authorize` on `sleek-auth` with OAuth-style query params (`country_code`, `state`, `redirect_uri`, `code_challenge`); excluded from Swagger (`@ApiExcludeEndpoint`) |
| **Short Description** | Validates the client redirect URI for the tenant, builds a stateless `continue_token`, resolves the IdP login URL, optionally reuses an existing session from the signed `sauth_session_token` cookie, may set that cookie when a session is restored, and renders the `authorize` view with the IdP login link and flow metadata. On failure, renders `authorize-error`. |
| **Variants / Markets** | SG, HK, UK, AU (via `TENANT`: SGP, HKG, GBR, AUS on `InitAuthBaseDto.country_code`) |
| **Dependencies / Related Flows** | Upstream: client app redirect with PKCE params. Downstream: `POST /sso/saml/callback` (SAML assertion), `POST /sso/saml/continue` (code exchange + cookie), `POST /sso/token` (token), `POST /sso/session/continue`. Uses `OauthConfigService` redirect URL allowlist, `SamlClient` for IdP URL and provider label, signed cookie config from `cookies` + `getSessionCookieConfig` |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None (session profile for returning users is read from cache key `auth:session:{sessionIndex}` when validating the ID-token session cookie; no MongoDB in this path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.controller.ts` — `@Controller('sso')`; `@Get('/authorize')` reads `InitAuthBaseDto` from query, optional `req.signedCookies['sauth_session_token']` passed into `ssoService.initSaml`. On success: if `profile` is returned, sets cookie `sauth_session_token` via `getSessionCookieConfig` (path scoped for session continue); `res.render('authorize', { profile, login_url: uri, auto_redirect, continue_token, logout_url, referer, provider })`. On error: `res.status(500).render('authorize-error', ...)`.
- `src/modules/sso/sso.service.ts` — `initSaml(dto)` calls `validateRedirectUrl`, `generateStatelessToken` for `continue_token`, `samlClient.generateAuthUrl()` as default IdP URI; if `dto.session_token` present and `validateSessionToken` succeeds, returns `auto_redirect: false`, existing `profile`, and `session_token`; else `auto_redirect: true`, `profile: null`, `saml_provider: this.samlClient.provider`.
- `src/modules/sso/clients/saml.client.ts` — Constructs `ServiceProvider` / `IdentityProvider` from `saml` config (`saml2-js`); `generateAuthUrl()` returns `config.assert_endpoint` (IdP SSO target in config); `provider` getter exposes configured provider name (e.g. JumpCloud default in config defaults).
- `src/modules/sso/dto/init-auth-dto.ts` — `InitAuthBaseDto` requires `country_code` (`TENANT`), `state`, `redirect_uri`, `code_challenge`; `InitAuthDto` adds optional `session_token` for the service layer.
