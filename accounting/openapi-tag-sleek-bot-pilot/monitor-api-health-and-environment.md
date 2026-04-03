# Monitor API health and environment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Monitor API health and environment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations, System (load balancers, uptime monitors, deploy pipelines) |
| **Business Outcome** | Operators and automation can confirm the service is up and which environment instance is running, supporting reliable deployments and incident response. |
| **Entry Point / Surface** | HTTP `GET /api/health` on the Sleek Bot Pilot Nest API (no auth guards; intended for probes and ops). Swagger document uses tag `sleek-bot-pilot` (`main.ts` `DocumentBuilder`). |
| **Short Description** | Returns a fixed healthy status string, `NODE_ENV` as `currentEnv`, and a server `timeStamp`. Implemented in `HealthController` with response shape from `HealthDto` (Swagger `ApiProperty` on DTO fields). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | None in code (no downstream services, queues, or DB). Depends on process `NODE_ENV` at runtime. |
| **Service / Repository** | sleek-bot-pilot |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/main.ts`

- `app.setGlobalPrefix('api')` — health route is under `/api`.
- `SwaggerModule` with `DocumentBuilder` title `Sleek Bot Pilot`, single tag `sleek-bot-pilot`.

### `src/app.module.ts`

- Registers `HealthController` alongside `AppController`.

### `src/health/health.controller.ts`

- `@Controller('health')` — `GET /` handler `getHealth()` returns `{ status: "Healthy!", currentEnv: process.env.NODE_ENV, timeStamp: new Date() }`.
- No authentication or authorization decorators (public surface).

### `src/health/dto/health.dto.ts`

- `HealthDto`: `status`, `timeStamp`, `currentEnv` with `class-validator` and `@nestjs/swagger` `ApiProperty` for OpenAPI schema generation.

### `src/health/health.controller.spec.ts`

- Smoke test: controller is defined.

### Unknown columns (reason)

- **Disposition** — Unknown per pipeline default.
- **Variants / Markets** — No regional or tenant branching in this path; not inferrable from these files.
