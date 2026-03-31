# Nest SDK: M2M and flexible authentication

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Machine and mixed authentication modes for Nest routes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Backend engineer |
| **Business Outcome** | Same service can accept service tokens or user tokens where policy allows |
| **Entry Point / Surface** | `@M2MAuthenticated()`, `M2mGuard`, `@FlexibleAuthenticated()`, `FlexibleAuthGuard` |
| **Short Description** | M2M guard validates client/service JWTs; flexible guard combines patterns for dual-mode endpoints |
| **Variants / Markets** | TBD |
| **Dependencies / Related Flows** | `POST /token` M2M issuance in `sleek-auth` |
| **Service / Repository** | `sdk-auth-nest` `src/guards/m2m.guard.ts`, `src/guards/flexible-auth.guard.ts`, `src/decorators/m2m-authenticated.decorator.ts`, `flexible-authenticated.decorator.ts` |
| **DB - Collections** | N/A |
| **Evidence Source** | Codebase, `_test_/guards/` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/token/controllers/token.controller.ts` — M2M token minting.

### sleek-auth-ui

- N/A.

### sdk-auth-nest

- `src/guards/m2m.guard.ts`
- `src/guards/flexible-auth.guard.ts`
- `src/decorators/m2m-authenticated.decorator.ts`
- `src/decorators/flexible-authenticated.decorator.ts`
