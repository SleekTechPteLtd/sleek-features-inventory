# Roles administration (IAM)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Create roles and attach policies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin (`internal_authz` write) |
| **Business Outcome** | Reusable role bundles simplify assigning many permissions at once |
| **Entry Point / Surface** | `sleek-auth-ui` `AdminRolesPage`, `AdminRolePolicyPage`; API `roles` |
| **Short Description** | Role CRUD, assign/unassign policies to roles, scope queries |
| **Variants / Markets** | Per tenant/client |
| **Dependencies / Related Flows** | Policies; user-role assignments |
| **Service / Repository** | `sleek-auth` `src/role/role.controller.ts`, `RoleService`, `RolePolicyService`; `sleek-auth-ui` `src/features/roles/` |
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

- `src/role/role.controller.ts`

### sleek-auth-ui

- `src/features/roles/pages/admin/AdminRolesPage.tsx`, `AdminRolePolicyPage.tsx`
- `src/features/roles/components/RoleFormModal.tsx`, `RolePolicyFormModal.tsx`, etc.
- `src/features/roles/services/RoleService.ts`

### sdk-auth-nest

- Role permissions in JWT validated by `AuthzService` (`RolePermission` types).
