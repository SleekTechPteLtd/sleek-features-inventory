# Confirm auth service health

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Confirm auth service health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (orchestration, monitoring, load balancers) |
| **Business Outcome** | Orchestration and monitoring can confirm the Sleek Auth service is up and read deployment version and regional platform metadata without authenticating |
| **Entry Point / Surface** | HTTP `GET /api/health` on the Sleek Auth service (public probe; not in Swagger) |
| **Short Description** | Returns JSON `{ ok: true, version, platform }`. `version` comes from `app_version` in config (via `getAppVersion()`); `platform` defaults from `COUNTRY_CODE` env or `SGP`. Constructor caches values from `ConfigService`. No auth guards—suitable for probes. |
| **Variants / Markets** | Unknown (platform label is deploy-configured; default `SGP`) |
| **Dependencies / Related Flows** | Deploy-time config (`app_version`, `COUNTRY_CODE` / `platform`); may be composed with other service health checks in the same environment |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/app.controller.ts` — `AppController` at root `@Controller()`; `@Get('/api/health')` with `@ApiExcludeEndpoint()`; `apiHealth()` returns `{ ok: true, version: this.version, platform: this.platform }`. Constructor sets `version` from `configService.get('app_version', 'development')` and `platform` from `configService.get('platform', 'SGP')`.
- `src/config/config.ts` — `app_version: getAppVersion()`; `platform: process.env.COUNTRY_CODE || 'SGP'`.
- `src/specs/app.controller.spec.ts` — `apiHealth()` returns `ok: true`.
