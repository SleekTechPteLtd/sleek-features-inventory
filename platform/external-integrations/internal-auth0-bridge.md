# Internal Auth0 bridge (custom database)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Auth0 custom database login and user claims |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Auth0 Actions / custom DB scripts (server-to-server) |
| **Business Outcome** | Auth0 can authenticate users without holding primary DB credentials; claims stay aligned with Sleek user model |
| **Entry Point / Surface** | `POST /internal/auth0/verify-credentials`, `POST /internal/auth0/user-claims` with API key guard |
| **Short Description** | Validates identifier/password and returns Auth0 profile shape; separate endpoint enriches user claims |
| **Variants / Markets** | Optional `country_code` on verify |
| **Dependencies / Related Flows** | User store; Auth0 tenant configuration |
| **Service / Repository** | `sleek-auth` `src/auth0-internal/auth0-internal.controller.ts`, `Auth0InternalApiKeyGuard`, service layer |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase, inline API docs on controller |
| **Criticality** | High |
| **Usage Confidence** | Medium (env-specific) |
| **Disposition** | Must Keep |
| **Open Questions** | Long-term position vs full migration to native Sleek Auth only |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/auth0-internal/auth0-internal.controller.ts`
- `src/auth0-internal/guards/auth0-internal-api-key.guard.ts`

### sleek-auth-ui

- N/A (not a human UI surface).

### sdk-auth-nest

- N/A for Auth0 bridge directly; issued user JWTs still verified by SDK in downstream services.
