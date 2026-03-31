# OAuth client administration

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Register and manage OAuth clients (secrets, PKCE helpers) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Platform / internal admin with `internal_authz` write |
| **Business Outcome** | Each integrated app gets client credentials and redirect metadata for secure OAuth |
| **Entry Point / Surface** | `POST /client`, secret rotation, URL mapping endpoints; admin UI may live in platform-admin or auth-ui remote |
| **Short Description** | Creates clients per tenant, validates tenant scope, updates secrets, exposes PKCE state decoding for app URLs |
| **Variants / Markets** | Country URL configs on client |
| **Dependencies / Related Flows** | M2M token issuance; hosted login |
| **Service / Repository** | `sleek-auth` (`client.controller`, `ClientService`); `@RequireAdminPermission` uses SDK `POLICY_ACTION` |
| **DB - Collections** | TBD (client, tenant entities) |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Whether all CRUD is exposed in `sleek-auth-ui` Admin remote vs external tools |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/client/controllers/client.controller.ts` — create client, update secret, `getApplicationUrls`, `decodeAppOrigin`.
- `src/client/services/client.service.ts`

### sleek-auth-ui

- `src/remote/Admin.tsx` — module federation admin surface (authorization admin; client admin may be adjacent tooling).

### sdk-auth-nest

- `POLICY_ACTION`, permission decorators used by `RequireAdminPermission` in sleek-auth (`policy.controller`, `role.controller`, `client.controller` imports).
