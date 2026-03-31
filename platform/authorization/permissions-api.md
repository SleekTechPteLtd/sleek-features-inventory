# Permissions catalog API

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Permission definitions exposed for IAM UIs and integrations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin UI; integrators building policy screens |
| **Business Outcome** | Single source of truth for permission strings/actions bound to policies |
| **Entry Point / Surface** | `permission` controller on `sleek-auth` |
| **Short Description** | Lists/searches permissions used when editing policies and assignments |
| **Variants / Markets** | TBD |
| **Dependencies / Related Flows** | Policies; SDK `POLICY_ACTION` |
| **Service / Repository** | `sleek-auth` `src/permission/controllers/permission.controller.ts` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/permission/controllers/permission.controller.ts`

### sleek-auth-ui

- Consumed indirectly by policy/role hooks (`usePolicyPermissions`, `useRolePermissions`, etc.).

### sdk-auth-nest

- `src/types/authz.ts` — `POLICY_ACTION`, permission check DTOs align with catalog semantics.
