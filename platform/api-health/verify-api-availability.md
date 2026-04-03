# Verify API availability

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Verify API availability |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (monitoring, load balancers); developers and integrators calling the endpoint |
| **Business Outcome** | Confirms the auth API process is responding and surfaces deployment version and platform label for operations and debugging |
| **Entry Point / Surface** | HTTP `GET /api/health` on `sleek-auth` (no app navigation; public probe) |
| **Short Description** | Returns JSON with `ok: true`, `version`, and `platform`. Values come from Nest `ConfigService` keys `app_version` (default `development`) and `platform` (default `SGP`). Excluded from Swagger (`@ApiExcludeEndpoint`). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `ConfigService` configuration at deploy time; callers may pair with other service health checks |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/app.controller.ts` — `@Controller()`; `@Get('/api/health')` → `apiHealth()` returns `{ ok: true, version: this.version, platform: this.platform }`; constructor reads `app_version` and `platform` from `ConfigService`.
- `src/specs/app.controller.spec.ts` — unit test asserts `response.ok === true` for `apiHealth()`.
