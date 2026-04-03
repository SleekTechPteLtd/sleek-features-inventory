# SSO logout page

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | SSO logout page |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (browser) ending an SSO session |
| **Business Outcome** | Clears the local auth session cookie and presents a short client-side step that opens the configured IdP logout URL so the user can terminate the IdP session before returning to the referring app |
| **Entry Point / Surface** | Browser navigation to `GET /sso/logout` on `sleek-auth`; excluded from Swagger (`@ApiExcludeEndpoint`) |
| **Short Description** | Clears the `sauth_session_token` cookie by setting `maxAge: 0`, then renders the `logout` Handlebars view with the configured `logout_url` (IdP console logout) and the request `Referer` for post-logout redirect. |
| **Variants / Markets** | SG, HK, UK, AU (same tenant surface as other `sleek-auth` SSO flows; no country-specific branching in this handler) |
| **Dependencies / Related Flows** | Upstream: user or app linking to `/sso/logout`. Uses `auth.logout_url` from Nest `ConfigService` (`auth` key, `AuthConfig`). Downstream: client script in `views/logout.hbs` opens IdP logout in a new tab and redirects the window to `referer`. Related: `GET /sso/authorize` passes the same `logout_url` into the authorize template for in-flow logout links. |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Cookie clear uses only `{ maxAge: 0 }` without repeating path/options from `getSessionCookieConfig`; whether the browser reliably clears the same scoped cookie as set on login is not verified in code here — may warrant ops confirmation |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/modules/sso/sso.controller.ts` — `@Controller('sso')`; `@Get('/logout')` reads `referer` from `req.headers['referer']`, sets `res.cookie('sauth_session_token', { maxAge: 0 })`, then `res.render('logout', { logout_url: this.authConfig.logout_url, referer })`. Constructor loads `AuthConfig` via `configService.get('auth', { … defaults including logout_url })`.
- `src/modules/sso/sso.interface.ts` — `AuthConfig` includes `logout_url: string`.
- `views/logout.hbs` — Inline script: reads `logout_url` and `referer`, opens `logoutUrl` in `_blank`, closes the tab, calls `window.location.replace(referer)`; `setTimeout` fallback to same redirect after 1s.
