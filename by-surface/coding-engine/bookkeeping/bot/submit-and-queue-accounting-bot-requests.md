# Submit and queue accounting bot requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit and queue accounting bot requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Accounting / finance workflows (end users initiate work upstream); HTTP callers are **API key–authenticated clients** (`AuthGuard`: `Authorization` or `query.api_key` must match `SLEEK_BOT_PILOT_API_KEY`). |
| **Business Outcome** | Resource requests for accounting automation are recorded and handed off to **UiPath** queue processing so RPA can execute the requested work and downstream systems can react to completion. |
| **Entry Point / Surface** | **Sleek Bot Pilot** Nest API (global prefix `api`): **POST** `/api/bot` (create + queue), **GET** `/api/bot`, **GET** `/api/bot/:id`, **PUT** `/api/bot/:id`, **POST** `/api/bot/open`. Swagger at `/api`. |
| **Short Description** | Persists a **resource request** (company, user, resource type, payload, status) in MongoDB, then for the primary create path enriches the UiPath queue payload with the saved document id, obtains an OAuth token from UiPath, and posts an **AddQueueItem** job. Supports listing and filtering requests, finding “open” queued/in-progress work per company and resource types, and updating status, failure reason, and bot details—triggering optional webhooks for migration and export flows. |
| **Variants / Markets** | Code maps payload environment `gb` → `uk` before queueing; other regions not enumerated in these files — **Unknown** for full market matrix. |
| **Dependencies / Related Flows** | **UiPath Orchestrator** (OAuth `client_credentials`, OData `Queues/UiPathODataSvc.AddQueueItem`); **`SBMigrationService`**, **`CITService`**, **`XeroExportService`** webhook push helpers on **update** (by `resource`). Upstream: any product or service that calls Bot Pilot with the API key and a valid `payload` shape for UiPath. |
| **Service / Repository** | sleek-bot-pilot |
| **DB - Collections** | Mongoose model **`ResourceRequest`** → default collection **`resourcerequests`** (not renamed in schema). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact contract for `payload` / queue item shape beyond `itemData.SpecificContent` usage; full list of `resource` values and how each maps to the three webhook services; whether any caller uses `create()` without queue (not exposed on controller). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `resource-request/resource-request.controller.ts`

- **`@Controller('bot')`** + **`@UseGuards(new AuthGuard())`** on the class: all routes require API key.
- **POST** `/` → `createAndQueue` → returns `{ _id }`.
- **PUT** `/:id` → `update` (status, `failure_reason`, `bot_details`).
- **GET** `/:id` → `findById`.
- **GET** `/` → `findAll` with **`GetBotDto`** query (`user`, `company`, `resource`, `status`, `limit` default 3, `sort` ASC/DESC for `createdAt`).
- **POST** `open` → `findOpenBots` with **`GetOpenBotDto`** (`company`, `resources[]`).

### `resource-request/resource-request.service.ts`

- **`create`**: `new this.rrModel(createResourceDto).save()`.
- **`createAndQueue`**: After save, sets `queueItem.itemData.SpecificContent.UpdateId` to saved **`_id`** string; if `payload.itemData.SpecificContent.Environment == 'gb'`, sets **`Environment`** to **`uk`**; **`uipathService.getAuthToken()`** then **`addToQueue(token, queueItem)`**; throws if auth or queue response missing `data.QueueDefinitionId`.
- **`findOpenBots`**: For each resource in `resources`, **`findOne`** with `company`, `resource`, status **`QUEUED`** or **`IN_PROGRESS`**, latest by `createdAt`.
- **`update`**: Patches status / failure / bot_details; **`sbMigrationService.pushRequest`**, **`citService.pushRequest`**, **`xeroExportService.pushRequest`** with `(resource, document)` before **`save()`**.

### `resource-request/resource-request.schema.ts`

- **`status`**: enum `FAILED`, `SUCCESS`, `IN_PROGRESS`, `QUEUED`, `CREATED` (indexed).
- **`company`**, **`user`**: `ObjectId`, required, indexed.
- **`resource`**: string, indexed.
- **`payload`**, **`bot_details`**: loose objects; **`failure_reason`**, **`is_archived`**; **`timestamps: true`**.

### `queue/uipath.service.ts`

- **`getAuthToken`**: POST to **`${RPA_UIPATH_BASE_URL}/identity_/connect/token`** (form: `client_credentials`, client id/secret, broad Orchestrator scopes).
- **`addToQueue`**: POST to **`.../sleektechpteltd/DefaultTenant/odata/Queues/UiPathODataSvc.AddQueueItem`** with Bearer token, **`X-UIPATH-OrganizationUnitId`** from config.

### `resource-request/dto/createResource.dto.ts`

- Required: `user`, `company`, `resource`, `status`; optional `payload`, `failure_reason` (strings for ids/status where applicable).

### `main.ts`

- Global prefix **`api`** → routes above are under **`/api/bot`**.
