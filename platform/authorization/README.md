# Authorization (category)

**Who may do what** after authentication: policy definitions, roles, permission catalog, assigning roles/policies to users and organizations, and **local enforcement** from JWT authz claims in Nest (`AuthzService` / enforcer).

Authentication (login, tokens, MFA, Nest JWT verification guards) lives in [../authentication/](../authentication/).

## Capability documents

| Document | Short description |
|----------|-------------------|
| [policies-administration.md](./policies-administration.md) | Policies, nodes, permission bindings |
| [roles-administration.md](./roles-administration.md) | Roles, role–policy links |
| [permissions-api.md](./permissions-api.md) | Permission catalog API |
| [user-role-and-policy-assignments.md](./user-role-and-policy-assignments.md) | Per-user roles and direct policies |
| [organizations.md](./organizations.md) | Organizations API |
| [organization-assignments.md](./organization-assignments.md) | Org–user assignments |
| [nest-sdk-authorization-pdp.md](./nest-sdk-authorization-pdp.md) | Nest AuthZ service, `NativeEnforcer`, `POLICY_ACTION` |

## Admin UI (sleek-auth-ui) — quick map

| Area | Typical paths | Doc |
|------|----------------|-----|
| Policies | `src/features/policies/pages/admin/*`, `components/*` | policies-administration |
| Roles | `src/features/roles/pages/admin/*` | roles-administration |
| Assignments | `src/features/assignments/pages/admin/*` | user-role-and-policy-assignments |
| Admin shell | `src/remote/Admin.tsx` | (IAM docs above) |
