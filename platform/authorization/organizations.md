# Organizations

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Organization directory and membership context |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin operator; APIs consumed by UIs assigning users |
| **Business Outcome** | Structured tenancy below tenant/client for RBAC and org-scoped access |
| **Entry Point / Surface** | `organization` controllers under `sleek-auth` |
| **Short Description** | CRUD/list organizations and relate users (see also organization-assignments) |
| **Variants / Markets** | TBD |
| **Dependencies / Related Flows** | User–org assignments; policies scoped by org where applicable |
| **Service / Repository** | `sleek-auth` `src/organization/controllers/organization.controller.ts` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | Product mapping: org vs “company” in other domains |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/organization/controllers/organization.controller.ts`
- `src/organization/organization.module.ts`

### sleek-auth-ui

- No dedicated org pages found in quick pass; assignments UI may reference orgs indirectly — confirm with product.

### sdk-auth-nest

- JWT / context may carry org claims depending on token shape (`src/types/jwt-token-payload.ts`).
