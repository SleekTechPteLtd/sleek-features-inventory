# Hosted authentication: login, PKCE, OAuth, and SSO hints

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Hosted login and OAuth/PKCE authentication |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user signing in via Sleek Auth–hosted UI or PKCE redirect flow |
| **Business Outcome** | Centralized identity for Sleek apps; supports password, PKCE, and provider-agnostic login without each app re-implementing OAuth |
| **Entry Point / Surface** | `sleek-auth-ui` login, PKCE callback, authorize callback, MFA entry; API `POST /login`, `prepare-auth`, PKCE/oauth routes |
| **Short Description** | User authenticates with credentials or PKCE; server resolves method via `prepare-auth`, issues tokens, handles password unification and pending states where applicable |
| **Variants / Markets** | Per-client/tenant SSO configuration; device/IP context on login |
| **Dependencies / Related Flows** | Token refresh; MFA; terms acceptance (cross-country); client URL resolution (`client` PKCE state helpers) |
| **Service / Repository** | `sleek-auth` (`login.controller`, `PkceService`, `LoginProviderAgnosticService`); `sleek-auth-ui` (`LoginForm`, `PkceCallbackHome`, `AuthorizeCallback`, `useSSO`); consumers use `@sleek-js-sdk/auth` |
| **DB - Collections** | TBD (user/session stores) |
| **Evidence Source** | Codebase, Bruno/API docs under `src/login/docs` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Migration vs legacy sleek-back login overlap |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/login/controllers/login.controller.ts` — `POST /login`, `prepare-auth`, PKCE/oauth/token exchange flows.
- `src/login/services/pkce.service.ts` — PKCE state and authentication orchestration.
- `src/client/controllers/client.controller.ts` — `getApplicationUrls`, `decodeAppOrigin` (PKCE state for redirects).

### sleek-auth-ui

- `src/features/auth/components/LoginForm.tsx`
- `src/features/auth/components/PkceCallbackHome.tsx`, `AuthorizeCallback.tsx`
- `src/features/auth/hooks/useSSO.tsx`
- `src/lib/auth-client.ts` — browser client wiring

### sdk-auth-nest

- Indirect: downstream Nest apps validate JWTs issued by this flow via `nest-sdk-jwt-guards-and-context.md`.
