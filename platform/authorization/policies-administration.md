# Policies administration (IAM)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Create and maintain authorization policies and segments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin (`internal_authz` write) |
| **Business Outcome** | Central policy definitions drive fine-grained access across Sleek products |
| **Entry Point / Surface** | `sleek-auth-ui` `AdminPoliciesPage`, `AdminPolicyPage`, policy modals; API `policies` controller |
| **Short Description** | Policy CRUD, policy nodes, permission bindings; Swagger docs under `src/policy/docs` |
| **Variants / Markets** | Per tenant/client |
| **Dependencies / Related Flows** | Roles (role–policy); permissions catalog; SDK enforcer |
| **Service / Repository** | `sleek-auth` `src/policy/policy.controller.ts`, services; `sleek-auth-ui` `src/features/policies/` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/policy/policy.controller.ts` — `@RequireAdminPermission('internal_authz', POLICY_ACTION.WRITE)` on mutating routes.
- `src/policy/services/policy.service.ts`, `policy-node.service.ts`

### sleek-auth-ui

- `src/features/policies/pages/admin/AdminPoliciesPage.tsx`, `AdminPolicyPage.tsx`
- `src/features/policies/components/*.tsx`, `src/features/policies/services/PolicyService.ts`

### sdk-auth-nest

- `POLICY_ACTION`, `AuthzService`, `NativeEnforcer` consume policy-shaped permissions from JWT or checks.
