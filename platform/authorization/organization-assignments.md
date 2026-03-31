# Organization assignments

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Assign users to organizations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin configuring org membership |
| **Business Outcome** | Users operate within correct org context for authorization |
| **Entry Point / Surface** | `organization-assignments` controller routes |
| **Short Description** | Administrative APIs to link users and organizations |
| **Variants / Markets** | TBD |
| **Dependencies / Related Flows** | Organizations; user-role assignments |
| **Service / Repository** | `sleek-auth` `src/organization/controllers/organization-assignments.controller.ts` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | UI ownership (platform-admin vs auth-ui remote) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/organization/controllers/organization-assignments.controller.ts`

### sleek-auth-ui

- Confirm if exposed via `Admin` remote or separate host — not enumerated in `features/organizations`.

### sdk-auth-nest

- Enforcement via JWT + AuthZ when org appears in claims or permission scope.
