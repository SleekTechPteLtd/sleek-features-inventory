# Verify IRAS integration service health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Verify IRAS integration service health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (load balancers, monitoring, orchestration); Operations User |
| **Business Outcome** | Confirms the IRAS integration HTTP service is up and reports its runtime environment so deployments, traffic routing, and manual checks can proceed before relying on Form CS and related workflows. |
| **Entry Point / Surface** | HTTP `GET /api/health` on sleek-iras-service (port 6005 in `main.ts`; no Sleek app navigation—programmatic liveness and environment probes). |
| **Short Description** | An unauthenticated GET returns a fixed status string, `NODE_ENV` as `currentEnv`, and a server timestamp. Intended for liveness and basic environment visibility, not deep dependency checks. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Independent of Form CS submission routes (`formcs-submission` is excluded from the global `/api` prefix and mounted separately). MongoDB and other modules load in `AppModule` but this handler does not touch them. |
| **Service / Repository** | sleek-iras-service |
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

- `app.setGlobalPrefix('api', { exclude: ['formcs-submission'] })` — `HealthController` is not excluded, so the route is **`GET /api/health`** (controller path `health`).
- `DocumentBuilder` adds OpenAPI tag `sleek-iras-service`; `SwaggerModule.setup('api', app, document)` serves Swagger under the `api` path segment.
- `listen(6005)` — default listen port for local/runtime reference.

### `src/health/health.controller.ts`

- `@Controller('health')` → `HealthController`.
- `@Get()` → `getHealth(): HealthDto` returns `{ status: "Healthy!", currentEnv: process.env.NODE_ENV, timeStamp: new Date() }`.
- No guards or auth decorators — **unauthenticated** surface.

### `src/health/dto/health.dto.ts`

- `HealthDto`: `status` (string), `timeStamp` (Date), `currentEnv` (string) with `@ApiProperty()` for Swagger schema generation and `@IsString()` / `@IsDate()` for validation metadata (response is built inline, not class-transformed from a typical request DTO).

### `src/app.module.ts`

- `HealthController` registered alongside `AppController`; global `SentryInterceptor` applies unless configured otherwise.

### Tests

- `src/health/health.controller.spec.ts` — unit test instantiates `HealthController` and exercises `getHealth` (referenced for coverage; behavior matches controller implementation).
