# Token service: M2M credentials and refresh

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Machine-to-machine tokens and refresh tokens |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Backend services, scripts, trusted clients using client id/secret |
| **Business Outcome** | Secure service-to-service and automation access to Sleek Auth–protected APIs without user browsers |
| **Entry Point / Surface** | `POST /token` (with `sleek-client-id` / `sleek-tenant-id` headers), `POST /token/refresh` |
| **Short Description** | Issues JWT access tokens from client credentials; refresh endpoint rotates access using refresh token |
| **Variants / Markets** | Tenant-scoped clients |
| **Dependencies / Related Flows** | OAuth client registration and secret rotation; audit logging of M2M issuance |
| **Service / Repository** | `sleek-auth` (`token.controller`, `TokenProviderAgnosticService`) |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase, Swagger `@ApiTags('Token')` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Token lifetime and rotation policy per environment |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/token/controllers/token.controller.ts` — `generateToken`, `refreshToken`.

### sleek-auth-ui

- Not typically end-user; no primary UI surface.

### sdk-auth-nest

- `src/guards/m2m.guard.ts`, `src/decorators/m2m-authenticated.decorator.ts` — protect routes with M2M JWTs.
- `nest-sdk-m2m-flexible-auth.md` for combined patterns.
