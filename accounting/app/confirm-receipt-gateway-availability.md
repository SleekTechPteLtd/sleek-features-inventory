# Confirm receipt gateway availability

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Confirm receipt gateway availability |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (load balancers, monitoring, orchestration); developers and operators probing the service |
| **Business Outcome** | Confirms the Sleek receipt gateway HTTP process is reachable and exposes minimal runtime metadata so infrastructure and operators can validate the service before routing receipt-related traffic. |
| **Entry Point / Surface** | HTTP `GET /` and `GET /api/health` on `sleek-receipt-gateway` (no Sleek app navigation; public programmatic health probes). |
| **Short Description** | `GET /api/health` returns plain text `Server is running!` as a simple liveness signal. `GET /` returns JSON with listening port (`PORT`), environment (`NODE_ENV`), and a server timestamp from `ConfigService`. Controller is tagged `health` in Swagger. Neither route uses auth guards. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `ConfigService` (global config from `@nestjs/config`); bootstrap in `main.ts` listens on `PORT` and serves Swagger; downstream receipt/email/Google routes are separate modules. Callers typically include load balancer health checks and deployment verification. |
| **Service / Repository** | sleek-receipt-gateway |
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
- No guards on these routes; constructor injects `ConfigService` only.

### `src/main.ts`

- `NestFactory.create(AppModule, { cors: true })`; listens on `configService.get('PORT')`.
- Swagger title: `Sleek Receipt Gateway Service`; OpenAPI written to `./src/docs/openapi.yaml` at bootstrap.

### `src/docs/openapi.yaml`

- Documents `GET /` (`AppController_home`) and `GET /api/health` (`AppController_healthcheck`) under tag `health`.

### Tests

- No `app.controller.spec.ts` in this repo; other modules have dedicated `*.spec.ts` files under `test/`.
