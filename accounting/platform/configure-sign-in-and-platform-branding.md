# Configure sign-in and platform branding

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Configure sign-in and platform branding |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | SleekBooks client application (app bootstrap); end users indirectly via any screen that relies on Auth0 and product identity |
| **Business Outcome** | Clients obtain Auth0 settings and a fixed SleekBooks product identity so sign-in and branding can be configured without embedding secrets or product names in front-end source alone. |
| **Entry Point / Surface** | Sleek App (or any API consumer) on startup: HTTP `GET /platform/config` under tag `platform` in Swagger; not a specific in-app navigation path. |
| **Short Description** | `PlatformService.getConfig()` reads `AUTH0_CONFIG` from the environment, parses it as JSON, and returns `{ auth0, platformName: 'SleekBooks' }`. `PlatformController` exposes this at `GET /platform/config` with no auth guard. A separate `GET /platform/user` route returns `request.user` behind `SleekBackAuthGuard` and is not required to read public platform config. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Auth0 configuration supplied via deployment env `AUTH0_CONFIG`; client-side Auth0 SDK and SleekBooks UI consume the payload. Related authenticated identity is surfaced via `GET /platform/user` (same controller module). |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `JSON.parse(process.env.AUTH0_CONFIG || '')` will throw if `AUTH0_CONFIG` is unset or empty—confirm runtime guarantees and whether a safer default or explicit error response is desired. `HttpService` is injected on `PlatformService` but not used by `getConfig`; clarify if future HTTP calls are planned or if dependency is vestigial. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/platform/platform.controller.ts`

- `@ApiTags('platform')`; `@Controller('platform')`.
- `GET /platform/config` → `getConfig()`: calls `platformService.getConfig()`, returns JSON with `HttpStatus.OK`. No `@UseGuards` (public config surface).
- `GET /platform/user` → `getUser()`: `@UseGuards(SleekBackAuthGuard)`; returns `request.user` as JSON. `@ApiOperation` summaries: “Get Platform Config” / “Get User”.

### `src/platform/platform.service.ts`

- `@Injectable()`; constructor injects `HttpService` (not referenced in `getConfig`).
- `getConfig()`: `authConfig = JSON.parse(process.env.AUTH0_CONFIG || '')`; return value `{ auth0: authConfig, platformName: 'SleekBooks' }`.

### Tests / OpenAPI

- No `platform.controller.spec.ts` or `platform.service.spec.ts` observed under `src/platform/` in this pass; confirm with repo test layout if needed.
