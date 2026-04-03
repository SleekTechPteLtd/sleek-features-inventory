# Report service health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Report service health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / orchestration (HTTP probes, monitoring); **no authentication** on this controller. |
| **Business Outcome** | Confirm the Sleek Bot Pilot API process is running and expose minimal runtime context (`NODE_ENV`, server time) for uptime checks and incident triage. |
| **Entry Point / Surface** | **Sleek Bot Pilot** Nest API (global prefix `api`): **GET** `/api/health`. Swagger UI is served at `/api` alongside the OpenAPI document. |
| **Short Description** | Returns a fixed status string, `process.env.NODE_ENV`, and a `Date` timestamp. Intended for load balancers, Kubernetes probes, and operators—not a deep dependency or readiness check (no DB or downstream calls). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | None in code path; global **Sentry** interceptor applies at app level (`AppModule`). |
| **Service / Repository** | sleek-bot-pilot |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/health/health.controller.ts`

- **`@Controller('health')`** — no **`@UseGuards`**; endpoint is **public**.
- **`@Get()`** → **`getHealth()`** returns **`HealthDto`**: `status: "Healthy!"`, **`currentEnv: process.env.NODE_ENV`**, **`timeStamp: new Date()`**.

### `src/health/dto/health.dto.ts`

- **`HealthDto`**: `status`, `timeStamp`, `currentEnv` with **`@ApiProperty()`** for Swagger; class-validator decorators present (`IsString`, `IsDate`) — response is built in the controller, not validated inbound.
- Imports include **`IsInt`** but it is not used on any property.

### `src/main.ts`

- **`app.setGlobalPrefix('api')`** — route is **`GET /api/health`**.
- **`SwaggerModule.setup('api', app, document)`** — API docs under `/api`.

### `src/app.module.ts`

- **`HealthController`** registered in **`controllers`** array alongside **`AppController`**.

### `src/health/health.controller.spec.ts`

- Smoke test: controller is defined.
