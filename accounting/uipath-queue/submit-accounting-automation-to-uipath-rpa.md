# Submit accounting automation to UiPath RPA queues

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit accounting automation to UiPath RPA queues |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System / internal integration (callers that hold the Sleek Bot Pilot API key). `ResourceRequestController` uses `AuthGuard`, which validates `SLEEK_BOT_PILOT_API_KEY` via `Authorization` header or `api_key` query — not end-user session auth. |
| **Business Outcome** | Work is persisted and handed off to UiPath Orchestrator queues so unattended RPA bots can run accounting automation jobs without manual handover. |
| **Entry Point / Surface** | **Sleek Bot Pilot** HTTP API: global prefix `api` → **`POST /api/bot`** creates a resource request and enqueues to UiPath. Related: **`PUT /api/bot/:id`**, **`GET /api/bot/:id`**, **`GET /api/bot`**, **`POST /api/bot/open`** for lifecycle and queries (see `resource-request.controller.ts`). |
| **Short Description** | On create, the service saves a `ResourceRequest` in MongoDB, enriches the queue payload with the saved document id (and normalizes `gb` environment to `uk` for UiPath), obtains an OAuth2 client-credentials token from UiPath Identity, then calls UiPath OData **`AddQueueItem`** so bots can process the item. Queue submission failures surface as errors from `createAndQueue`. |
| **Variants / Markets** | Payload may carry `itemData.SpecificContent.Environment`; **`gb` is mapped to `uk`** before enqueue. Other markets: **Unknown** without broader product matrix. |
| **Dependencies / Related Flows** | **UiPath Orchestrator** (Identity token endpoint, Queues OData API); **`RequestCreatorService`** for HTTP. On **`update`**, completion hooks call **`SBMigrationService`**, **`CITService`**, and **`XeroExportService`** `pushRequest` by resource type — downstream migration/CIT/Xero flows when bot status changes. |
| **Service / Repository** | sleek-bot-pilot |
| **DB - Collections** | **`resourcerequests`** (Mongoose model `ResourceRequest`: `status`, `company`, `user`, `resource`, `payload`, `failure_reason`, `is_archived`, `bot_details`, timestamps). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | **`UipathController` is registered but defines no routes** — intentional stub or dead code? Whether the hardcoded tenant path segment `sleektechpteltd/DefaultTenant` in `addToQueue` should vary per environment or region. Full list of `resource` values and how they map to downstream webhooks. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/queue/uipath.service.ts`

- **`getAuthToken`**: **POST** `{RPA_UIPATH_BASE_URL}/identity_/connect/token` with `client_credentials`, scopes including `OR.Queues`, `OR.Queues.Write`, `OR.Execution`, `OR.Jobs`, etc.; uses `RPA_UIPATH_CLIENTID`, `RPA_UIPATH_AUTH` (secret), `RPA_UIPATH_BASE_URL`.
- **`addToQueue`**: **POST** `{RPA_UIPATH_BASE_URL}/sleektechpteltd/DefaultTenant/odata/Queues/UiPathODataSvc.AddQueueItem` with JSON OData headers, **`Authorization`** bearer token, **`X-UIPATH-OrganizationUnitId`** from `RPA_UIPATH_ORGANIZATION_UNIT_ID`.

### `src/queue/uipath.controller.ts`

- **`UipathController`**: `@Controller()` with **no HTTP handlers** — only injects `UipathService` (unused at controller level).

### `src/resource-request/resource-request.service.ts`

- **`createAndQueue`**: Reads nested **`payload`** for UiPath queue item shape; **`create`** persists DTO; sets **`queueItem.itemData.SpecificContent.UpdateId`** to saved **`_id`**; maps **`Environment`** from **`gb`** → **`uk`**; **`getAuthToken`** then **`addToQueue`**; validates response has **`data.QueueDefinitionId`**.
- **`update`**: Persists status / `failure_reason` / `bot_details`; invokes **`sbMigrationService.pushRequest`**, **`citService.pushRequest`**, **`xeroExportService.pushRequest`** by **`resource`**.

### `src/resource-request/resource-request.controller.ts`

- **`@Controller('bot')`** + **`@UseGuards(new AuthGuard())`**.
- **`POST /`** → **`createAndQueue`** (returns `{ _id }`).

### `src/shared/guards/auth.guard.ts`

- Validates **`Authorization`** or **`api_key`** against **`SLEEK_BOT_PILOT_API_KEY`**.

### `src/main.ts`

- **`app.setGlobalPrefix('api')`** — routes under **`/api/...`**.

### `src/resource-request/resource-request.schema.ts`

- Mongoose **`ResourceRequest`** schema fields as listed in master sheet (status enum includes `QUEUED`, `IN_PROGRESS`, etc.).
