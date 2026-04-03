# PKCE validation and SSO token issuance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | PKCE validation and SSO token issuance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | OAuth client / end user (token exchange after IdP or session continue) |
| **Business Outcome** | Ensures only registered redirect URIs and correct PKCE verifiers can obtain access tokens, optionally persists a cached SSO session profile, and issues JWT access tokens bound to Sleek tenant users |
| **Entry Point / Surface** | `POST /sso/token` on `sleek-auth` (`@Controller('sso')`, `@ApiTags('SSO')`, `@ApiOperation` summary “Login”); related session/challenge material also consumed from `POST /sso/session/continue` and upstream SAML continue steps that mint the encrypted `code` challenge |
| **Short Description** | Resolves allowed redirect URIs per tenant from CMS OAuth config, validates the one-time challenge `code` and PKCE `code_verifier` (SHA-256), optionally writes the user profile to cache under `auth:session:{sessionIndex}`, and returns a JWT access token (`TokenSet`) produced from the user profile across tenants. `OauthConfigService` supplies redirect URL allowlists; `validateRedirectUrl` also enforces tenant CORS rules. |
| **Variants / Markets** | SG, HK, UK, AU (via `TENANT`: SGP, HKG, GBR, AUS on `CreateTokenDto.country_code` and related DTOs) |
| **Dependencies / Related Flows** | Upstream: SAML continue / session continue flows that issue encrypted challenge `code` and optional `session_index`. Downstream: API consumers use issued bearer token; `UserService` provisions/syncs users per tenant. Config: Sleek CMS app feature `oauth` (`AppFeatureService`). Related SSO docs: `start-saml-authorize-flow.md`, `process-saml-idp-callback.md`, `complete-saml-and-redirect.md` |
| **Service / Repository** | `sleek-auth`; Sleek CMS (OAuth redirect URLs via `@sleek-sdk/sleek-cms` `AppFeatureService`) |
| **DB - Collections** | Cache: keys `auth:session:*`, `auth:challenge:*` (challenge consumed at token exchange). MongoDB: user and group sync via `UserService.getOrCreateUserByEmail` / `syncUserGroups` during `generateAccessToken` — collection names not shown in cited files |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact MongoDB collection names for `UserService` in this deployment; whether Redis vs in-memory cache is used for `auth:*` keys in all environments |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.service.ts` — `createToken(dto)`: `validateRedirectUrl(dto.redirect_uri, dto.country_code)`; `validateChallengeToken<AuthChallenge>(dto.code)` reads and deletes `auth:challenge:{key}`; compares `challenge.redirect_uri` to `dto.redirect_uri`; `Crypto.verifySha256(challenge.code_challenge, dto.code_verifier)` for PKCE; on success, `createSession(challenge.session_index, challenge.profile)` when `session_index` present; returns `token_set: await this.generateAccessToken(challenge.profile)`. `generateAccessToken` builds JWT via `jwt.sign` with `jwt` config and `createTokenSet`. Helpers: `createSession` → `cacheManager.set('auth:session:${sessionIndex}', profile, session_buffer)`; `generateChallengeToken` / `validateChallengeToken` for encrypted challenge flow; `validateRedirectUrl` instantiates `new OauthConfigService(countryCode)` and calls `getRedirectUrls()`, plus `corsUrlsUtil.checkIfAllowedInTenant`.
- `src/modules/sso/services/oauth-config/oauth-config.service.ts` — `getAppFeature('oauth', APP_FEATURE_CATEGORY.GENERAL)` via `AppFeatureService`; `getRedirectUrls()` maps CMS `redirect_urls` to `URL[]`.
- `src/modules/sso/sso.controller.ts` — `POST /sso/token` → `ssoService.createToken(dto)`; JSON response exposes `access_token`, `expires_in`, `token_type`, `refresh_token: null`.
