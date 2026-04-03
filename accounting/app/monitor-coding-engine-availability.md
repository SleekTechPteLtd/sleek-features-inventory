# Monitor coding engine availability

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Monitor coding engine availability |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (monitoring, load balancers, orchestration); developers and operators calling the endpoints |
| **Business Outcome** | Confirms the accounting coding engine HTTP process is reachable and exposes minimal runtime state so platform checks and operators can verify the service is running. |
| **Entry Point / Surface** | HTTP `GET /` and `GET /api/health` on `acct-coding-engine` (no Sleek app navigation; public programmatic probes). |
| **Short Description** | `GET /api/health` returns plain text `Server is running!` as a simple liveness signal. `GET /` returns JSON with listening port (`PORT`), environment (`NODE_ENV`), and a server timestamp from `ConfigService`. Controller is tagged `health` in Swagger. Neither route uses auth guards. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `ConfigService` (global config); callers typically include infrastructure health checks and deployment verification alongside other services. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /` exposes `PORT` and `NODE_ENV` without authentication—confirm this matches production security and exposure expectations. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/app.controller.ts`

- `@Controller()`; `@ApiTags('health')`.
- `GET /` → `home()` returns `{ currentPortValue, currentEnv, timeStamp }` from `ConfigService.get('PORT')`, `get('NODE_ENV')`, and `new Date()`.
- `GET /api/health` → `healthcheck()` returns the string `'Server is running!'`.
- `POST /api/logout` uses `AuthGuard` and `AuthCacheService` — separate from health probes.

### `src/docs/openapi.yaml`

- Documents `GET /` (`AppController_home`) and `GET /api/health` (`AppController_healthcheck`) under tag `health`.

### `test/app.controller.spec.ts`

- `home()` test asserts `currentPortValue`, `currentEnv`, and `timeStamp`.
- `healthcheck()` test asserts return value `'Server is running!'`.
