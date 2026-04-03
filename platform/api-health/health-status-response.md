# Health status response

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Health status response |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Enables load balancers, orchestration probes, and monitoring to verify liveness and see which build and region are running without authenticating. |
| **Entry Point / Surface** | `GET /api/health` on the sleek-auth API (public; not listed in Swagger) |
| **Short Description** | Returns JSON with `ok: true`, the configured app version, and the platform/country code used for deployment visibility. Intended for probes and operational checks. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Nest `ConfigService`; global config supplies `app_version` (via `getAppVersion()`) and `platform` from `COUNTRY_CODE` (default `SGP`). No downstream services or DB. |
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

### `sleek-auth`

- `src/app.controller.ts` — `@Controller()`; `@Get('/api/health')` with `@ApiExcludeEndpoint()`; handler `apiHealth()` returns `{ ok: true, version: this.version, platform: this.platform }`. Constructor reads `app_version` (default `'development'`) and `platform` (default `'SGP'`) from `ConfigService`.
- `src/config/config.ts` — `getConfig()` sets `app_version: getAppVersion()` and `platform: process.env.COUNTRY_CODE || 'SGP'`, which feed the same keys consumed by `AppController`.
