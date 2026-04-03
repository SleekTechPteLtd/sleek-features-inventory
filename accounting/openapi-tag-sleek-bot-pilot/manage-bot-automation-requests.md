# Manage bot automation requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage bot automation requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can queue UiPath RPA work against companies and resources, then track and update automation status while downstream migration and export hooks stay in sync. |
| **Entry Point / Surface** | Sleek Bot Pilot API — `POST/GET/PUT /bot` (authenticated); consuming app or navigation path not determined from this service alone |
| **Short Description** | Persists bot resource requests in MongoDB, enqueues payloads to UiPath Orchestrator queues after OAuth, supports listing and filtering requests, finds in-flight work per company and resource types, and applies status or bot-detail updates that trigger SB migration, CIT, and Xero export webhooks. |
| **Variants / Markets** | UK (queue payload maps `gb` environment to `uk`); Unknown |
| **Dependencies / Related Flows** | UiPath Orchestrator (identity token + `AddQueueItem`); `SBMigrationService`, `CITService`, and `XeroExportService` webhooks on request update |
| **Service / Repository** | sleek-bot-pilot |
| **DB - Collections** | resourcerequests |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which product UI or internal tool calls these routes; call volume and SLOs; full regional rollout beyond UK/gb mapping |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/resource-request/resource-request.controller.ts`

- `@Controller('bot')` with `@UseGuards(new AuthGuard())` on the class: all routes require authentication.
- `POST /` → `createAndQueue`: creates a request and enqueues to UiPath (returns `{ _id }`).
- `PUT /:id` → `update`: status, failure reason, bot details.
- `GET /:id` → `findById`.
- `GET /` with query (`GetBotDto`: user, company, resource, status, limit default 3, sort ASC/DESC) → `findAll`.
- `POST /open` with body (`GetOpenBotDto`: company + resources[]) → `findOpenBots` (in-flight lookups).

### Service — `src/resource-request/resource-request.service.ts`

- `create` / `createAndQueue`: saves `ResourceRequest`, injects Mongo `_id` into `payload.itemData.SpecificContent.UpdateId`, maps `Environment` from `gb` to `uk`, obtains UiPath token via `UipathService.getAuthToken`, calls `addToQueue`.
- `findAll`: `rrModel.find(query)` with sort on `createdAt` and limit.
- `findOpenBots`: per resource, `findOne` with `status` in `QUEUED` or `IN_PROGRESS`, matching `company` and `resource`.
- `update`: sets `status`, `failure_reason`, `bot_details` when provided; awaits `sbMigrationService.pushRequest`, `citService.pushRequest`, `xeroExportService.pushRequest` before `save`.

### Schema — `src/resource-request/resource-request.schema.ts`

- Mongoose model `ResourceRequest`: `status` enum `FAILED`, `SUCCESS`, `IN_PROGRESS`, `QUEUED`, `CREATED`; indexed `company`, `user`, `resource`; `payload`, `bot_details` flexible objects; `failure_reason`, `is_archived`; `timestamps: true`.

### UiPath integration — `src/queue/uipath.service.ts`

- `getAuthToken`: client-credentials POST to `{RPA_UIPATH_BASE_URL}/identity_/connect/token` with scopes for queues, robots, jobs, etc.
- `addToQueue`: POST to Orchestrator OData `Queues/UiPathODataSvc.AddQueueItem` with `Authorization` bearer token and `X-UIPATH-OrganizationUnitId`.

### DTOs

- `CreateResourceDto`, `GetBotDto`, `GetOpenBotDto`, `UpdateResourceDto` under `src/resource-request/dto/` — shape query/body validation for the above operations.
