# Nest SDK: authorization (PDP-style permission checks)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Evaluate resource/action permissions from JWT authz payload |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Backend engineer enforcing policy in Nest handlers |
| **Business Outcome** | Fine-grained access aligned with Sleek Auth IAM without a round-trip per request (local enforcer) |
| **Entry Point / Surface** | `AuthzService`, `NativeEnforcer`, `@Permission()` / permission decorator patterns, `CheckUserPermissionDto` |
| **Short Description** | Decompresses/reads authz claims from JWT, checks resource + `POLICY_ACTION`, supports role permission sets |
| **Variants / Markets** | TBD |
| **Dependencies / Related Flows** | Policies and assignments in `sleek-auth`; same `POLICY_ACTION` enum used in `RequireAdminPermission`; JWT validated first ([`../authentication/nest-sdk-jwt-guards-and-context.md`](../authentication/nest-sdk-jwt-guards-and-context.md)) |
| **Service / Repository** | `sdk-auth-nest` `src/services/authz.service.ts`, `src/enforcers/native.enforcer.ts`, `src/types/authz.ts`, `src/decorators/permission.decorator.ts` |
| **DB - Collections** | N/A (stateless from JWT) |
| **Evidence Source** | Codebase, `_test_/services/authz.service.spec.ts` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | When to use local enforcer vs central PDP API (if introduced) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `POLICY_ACTION` imported from `@sleek-nest-sdk/auth` in controllers (e.g. `policy.controller.ts`, `role.controller.ts`, `client.controller.ts`).

### sleek-auth-ui

- IAM UIs define what permissions exist; enforcement happens in APIs using SDK.

### sdk-auth-nest

- `src/services/authz.service.ts`
- `src/enforcers/native.enforcer.ts`
- `src/dto/check-user-permission.dto.ts`
- `src/types/authz.ts` — `POLICY_ACTION`, `RolePermission`, payloads
