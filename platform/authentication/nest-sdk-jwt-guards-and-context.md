# Nest SDK: JWT verification, guards, and request context

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Verify Sleek Auth JWTs and attach user/tenant/client to Nest requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Backend engineer integrating Nest services |
| **Business Outcome** | Consistent, secure API protection across microservices consuming Sleek Auth tokens |
| **Entry Point / Surface** | `AuthModule.register`, `@Authenticated()`, `UserAuthGuard`, `RequestContextMiddleware` |
| **Short Description** | Validates JWT (JWKS / config), exposes decorators for user id, tenant id, client id; optional request context bag |
| **Variants / Markets** | RS256 / JWKS configuration (see sdk branch notes in repo) |
| **Dependencies / Related Flows** | Token issuance from `sleek-auth`; AuthZ checks ([`../authorization/nest-sdk-authorization-pdp.md`](../authorization/nest-sdk-authorization-pdp.md)) |
| **Service / Repository** | `sdk-auth-nest` `src/auth.module.ts`, `src/guards/user-auth.guard.ts`, `src/guards/base.guard.ts`, `src/context/`, `src/decorators/authenticated.decorator.ts`, `src/services/auth.service.ts` |
| **DB - Collections** | N/A |
| **Evidence Source** | Codebase, unit tests under `_test_/` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- Issues JWTs consumed by this SDK (`token`, `login` modules).

### sleek-auth-ui

- N/A (browser uses `@sleek-js-sdk/auth`, not Nest SDK).

### sdk-auth-nest

- `src/auth.module.ts`
- `src/guards/user-auth.guard.ts`, `src/guards/base.guard.ts`
- `src/context/request-context.middleware.ts`, `src/context/request-context.ts`
- `src/decorators/request-user.decorator.ts`, `request-tenant-id.decorator.ts`, `request-client.decorator.ts`
- `src/services/auth.service.ts`
