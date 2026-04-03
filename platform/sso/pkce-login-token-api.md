# PKCE login token API

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | PKCE SSO token exchange |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (via OAuth/PKCE client app) completing login by exchanging the one-time authorization code for API credentials |
| **Business Outcome** | Completes the SAML/PKCE redirect flow by issuing a signed JWT access token the client can use for Sleek platform APIs, after proving possession of the PKCE code verifier |
| **Entry Point / Surface** | `sleek-auth` OpenAPI/Swagger **SSO** tag — `POST /sso/token` (documented **Login** operation); JSON body per `CreateTokenDto` |
| **Short Description** | Accepts `code`, `code_verifier`, `redirect_uri`, and `country_code`. Validates the client redirect URL for the tenant (`OauthConfigService` + CORS), loads and consumes the encrypted challenge from cache, confirms `redirect_uri` matches the challenge, verifies SHA-256 PKCE (`code_verifier` vs stored `code_challenge`), optionally writes the user profile to the session cache when the challenge carried a `session_index`, then returns JSON with `access_token`, `expires_in`, `token_type`, and `refresh_token: null` after generating a multi-tenant JWT via `UserService` |
| **Variants / Markets** | SG, HK, UK, AU (via `TENANT` on `country_code` in `CreateTokenDto` / `InitAuthBaseDto`) |
| **Dependencies / Related Flows** | Upstream: `POST /sso/saml/continue` and `POST /sso/session/continue` append `code` to `redirect_uri`; challenges live under cache key `auth:challenge:{key}`. `OauthConfigService` loads allowlisted redirect URLs from Sleek CMS app feature `oauth` (GENERAL). `generateAccessToken` → `getOrCreateUser` / `syncUserGroups` per tenant via `UserService` → sleek-back repository client. Downstream: clients use bearer `access_token` against platform APIs |
| **Service / Repository** | `sleek-auth`; `sleek-back` (user/group sync via `UserService`); `@sleek-sdk/sleek-cms` / CMS config for OAuth redirect URLs |
| **DB - Collections** | None in `sleek-auth` (challenge storage: cache `auth:challenge:*`; optional session write `auth:session:{sessionIndex}`; user persistence delegated to sleek-back, not MongoDB in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.controller.ts` — `@Post('/token')` `createToken`: `@ApiOperation({ summary: 'Login', description: 'This API will create new session' })`, `@ApiBody` `CreateTokenDto`, `@ApiOkResponse` `CreateTokenResponseDoc`; returns `200` JSON with `access_token`, `expires_in`, `token_type`, `refresh_token: null` from `ssoService.createToken(dto)`.
- `src/modules/sso/sso.service.ts` — `createToken(dto)`: `validateRedirectUrl(dto.redirect_uri, dto.country_code)`; `validateChallengeToken<AuthChallenge>(dto.code)`; mismatch `redirect_uri` → `UnauthorizedClientError` (`INVALID_REDIRECT_URI`); `Crypto.verifySha256(challenge.code_challenge, dto.code_verifier)`; on match, if `challenge.session_index` then `createSession(challenge.session_index, challenge.profile)`; returns `{ profile, token_set: await generateAccessToken(challenge.profile) }`; on verifier mismatch → `CHALLENGE_FAILED`.
- `src/modules/sso/dto/create-token.dto.ts` — extends `InitAuthBaseDto` omitting `state` and `code_challenge`; adds required `code` and `code_verifier`.
- `src/modules/sso/dto/init-auth-dto.ts` — `InitAuthBaseDto` provides `country_code` (`TENANT` enum), `redirect_uri`, and (for init flows) `state` / `code_challenge`.
- `src/modules/sso/services/oauth-config/oauth-config.service.ts` — `getRedirectUrls()` from CMS `AppFeatureService.getAppFeature('oauth', APP_FEATURE_CATEGORY.GENERAL)`; used indirectly through `validateRedirectUrl` in `createToken`.
