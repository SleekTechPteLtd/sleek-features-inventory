# Sign out from SSO

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Sign out from SSO |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (browser) |
| **Business Outcome** | Users end the Sleek SSO session locally and are guided through the IdP logout URL so the identity provider session can be terminated before they return to the app. |
| **Entry Point / Surface** | Browser navigation to `GET /sso/logout` on the Sleek auth service (`sleek-auth`); endpoint excluded from Swagger (`@ApiExcludeEndpoint`). |
| **Short Description** | Clears the `sauth_session_token` signed session cookie, then renders the `logout` view with the configured IdP logout URL and the request `Referer`. Client-side script opens the IdP logout page and returns the user to the referring surface. |
| **Variants / Markets** | SG, HK, UK, AU (same auth surface as other SSO flows; no country branch in this handler) |
| **Dependencies / Related Flows** | Upstream: user or app linking to `/sso/logout`. Config: `auth.logout_url` via Nest `ConfigService` (`AuthConfig`, default JumpCloud user console logout). Related: `GET /sso/authorize` injects the same `logout_url` into the authorize template for in-flow logout. |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Cookie is cleared with `res.cookie('sauth_session_token', { maxAge: 0 })` without repeating path/options from `SsoService.getSessionCookieConfig`; confirm in ops that the browser clears the same scoped cookie as set on login. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.controller.ts` — `@Controller('sso')`; `@Get('/logout')` reads `referer` from `req.headers['referer']`, sets `res.cookie('sauth_session_token', { maxAge: 0 })`, renders `logout` with `logout_url: this.authConfig.logout_url` and `referer`. Constructor resolves `AuthConfig` from `configService.get('auth', { … })` including default `logout_url` (JumpCloud user console logout).
- `src/modules/sso/sso.service.ts` — `getSessionCookieConfig` defines how `sauth_session_token` is set for authorize/continue flows; logout path does not call the service (no server-side IdP API call in these files).
- `src/modules/sso/sso.interface.ts` — `AuthConfig` includes `logout_url: string` (referenced by controller config typing).
- `views/logout.hbs` — Opens `logout_url` in a new window, then `window.location.replace(referer)`; `setTimeout` fallback after 1s.
