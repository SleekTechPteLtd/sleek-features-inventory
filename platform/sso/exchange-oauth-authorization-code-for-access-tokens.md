# Exchange OAuth authorization code for access tokens

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Exchange OAuth authorization code for access tokens |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (via OAuth/PKCE client application) after IdP login; the client app calls the token endpoint on the user’s behalf |
| **Business Outcome** | After SAML/PKCE redirect, the client obtains a signed JWT access token it can use for Sleek platform APIs, with optional server-side session caching when the flow carried a session index |
| **Entry Point / Surface** | `sleek-auth` OpenAPI **SSO** tag — `POST /sso/token` (operation **Login**, “This API will create new session”); JSON body `CreateTokenDto` (`code`, `code_verifier`, `redirect_uri`, `country_code`) |
| **Short Description** | Validates the redirect URI against tenant OAuth config from CMS and CORS rules, decrypts and consumes the one-time encrypted authorization `code` from cache, confirms it matches `redirect_uri`, verifies PKCE by SHA-256 comparing stored `code_challenge` to `code_verifier`, optionally stores the user profile under `auth:session:{sessionIndex}` when the challenge includes a session index, then returns `access_token`, `expires_in`, `token_type`, and `refresh_token: null` from a multi-tenant JWT built via `UserService` |
| **Variants / Markets** | SG, HK, UK, AU (`TENANT` on `country_code` in `CreateTokenDto` / `InitAuthBaseDto`) |
| **Dependencies / Related Flows** | Upstream: `POST /sso/saml/continue` and `POST /sso/session/continue` append encrypted `code` to `redirect_uri`; challenges at `auth:challenge:{key}`. CMS app feature `oauth` (GENERAL) supplies redirect allowlist. `generateAccessToken` → `getOrCreateUser` / `syncUserGroups` per tenant via `UserService` (sleek-back). Downstream: bearer `access_token` on platform APIs |
| **Service / Repository** | `sleek-auth`; `sleek-back` (user and group sync via `UserService`); `@sleek-sdk/sleek-cms` for OAuth redirect URL configuration |
| **DB - Collections** | None in `sleek-auth` for this flow; cache keys `auth:challenge:*` (consumed), optional `auth:session:*`; user persistence delegated to sleek-back (collections not defined in cited files) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.controller.ts` — `POST /sso/token` `createToken`: `@ApiOperation({ summary: 'Login', description: 'This API will create new session' })`, `@ApiBody` `CreateTokenDto`, `@ApiOkResponse` `CreateTokenResponseDoc`; response `200` JSON `access_token`, `expires_in`, `token_type`, `refresh_token: null` from `ssoService.createToken(dto)`.
- `src/modules/sso/sso.service.ts` — `createToken(dto)`: `validateRedirectUrl(dto.redirect_uri, dto.country_code)`; `validateChallengeToken<AuthChallenge>(dto.code)` (loads and deletes `auth:challenge:{key}`); `challenge.redirect_uri` must equal `dto.redirect_uri` or `UnauthorizedClientError` (`INVALID_REDIRECT_URI`); `Crypto.verifySha256(challenge.code_challenge, dto.code_verifier)` for PKCE; on success, if `challenge.session_index` then `createSession(challenge.session_index, challenge.profile)`; returns `{ profile, token_set: await generateAccessToken(challenge.profile) }`; verifier mismatch → `CHALLENGE_FAILED`. `validateRedirectUrl` uses `new OauthConfigService(countryCode)` and `corsUrlsUtil.checkIfAllowedInTenant`. `generateAccessToken` signs JWT with `jwt` config after `getOrCreateUser` / `syncUserGroups` per `TENANT`.
- `src/modules/sso/services/oauth-config/oauth-config.service.ts` — `getRedirectUrls()` via `AppFeatureService.getAppFeature('oauth', APP_FEATURE_CATEGORY.GENERAL)` and `getValue<OauthConfigValue>({ redirect_urls: [] })`, mapping CMS `redirect_urls` to `URL[]` (used by `validateRedirectUrl` before token exchange).
- `src/modules/sso/dto/create-token.dto.ts` — `CreateTokenDto` extends `InitAuthBaseDto` without `state` / `code_challenge`; requires `code` and `code_verifier`.
