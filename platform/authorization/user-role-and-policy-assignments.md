# User role and direct policy assignments

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Assign roles and policies to users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin |
| **Business Outcome** | Users receive correct effective permissions at token issuance / check time |
| **Entry Point / Surface** | `sleek-auth-ui` `AdminAssignmentsPage` and assignment modals; `user-role` / `user-policy` APIs |
| **Short Description** | Binds users to roles and optionally direct policies; supports listing and mutation per admin rules |
| **Variants / Markets** | Per tenant/client |
| **Dependencies / Related Flows** | Roles; policies; JWT claims population |
| **Service / Repository** | `sleek-auth` `src/user/controllers/user-role.controller.ts`, `user-policy.controller.ts`; `sleek-auth-ui` `src/features/assignments/` |
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

- `src/user/controllers/user-role.controller.ts`
- `src/user/controllers/user-policy.controller.ts`

### sleek-auth-ui

- `src/features/assignments/pages/admin/AdminAssignmentsPage.tsx`
- `src/features/assignments/components/AssignmentCard.tsx`, `RoleFormModal.tsx`, `PolicyFormModal.tsx`
- `src/features/assignments/services/AssignmentService.ts`, hooks under `hooks/`

### sdk-auth-nest

- `AuthzService` evaluates permissions from JWT payload (`nest-sdk-authorization-pdp.md`).
