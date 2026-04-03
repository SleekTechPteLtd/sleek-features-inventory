# Track bot job outcomes and sync integrations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Track bot job outcomes and sync integrations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System |
| **Business Outcome** | Downstream accounting and migration products get timely completion signals when automation jobs finish, so workflows (SleekBooks migration, CIT, bank-statement Xero export) can continue without manual polling. |
| **Entry Point / Surface** | `sleek-bot-pilot` HTTP API `POST/GET/PUT /api/bot`, `POST /api/bot/open` — authenticated with `SLEEK_BOT_PILOT_API_KEY` via `Authorization` header or `api_key` query |
| **Short Description** | Persists bot resource requests in MongoDB, queues work to UiPath on create, and lets callers list or look up requests and open work by company and resource. On status or detail updates, conditionally notifies SleekBooks migration, CIT, and regional BSM Xero export services so they receive the updated request payload. |
| **Variants / Markets** | SG, HK, UK, AU (Xero export webhook uses per-country BSM base URL and token from payload `Country`, default `SG`; `gb` queue payload is normalised to `uk` for environment) |
| **Dependencies / Related Flows** | UiPath queue (`UipathService.addToQueue`); outbound HTTP: SleekBooks `XERO_SB_URL` migration dext-setup; CIT `CIT_BASE_URL` ECI bot API; BSM bank-transaction-export Xero webhook per region |
| **Service / Repository** | sleek-bot-pilot |
| **DB - Collections** | resourcerequests (Mongoose model `ResourceRequest`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether all resource types beyond those in webhook services rely solely on DB/API reads; full client list for the protected API is not in repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** (`src/resource-request/resource-request.controller.ts`): `@Controller('bot')` with `AuthGuard`; `POST /` → `createAndQueue`; `PUT :id` → `update`; `GET :id` → `findById`; `GET /` → `findAll` with `GetBotDto` query; `POST open` → `findOpenBots` with company + resources.
- **Service** (`src/resource-request/resource-request.service.ts`): `createAndQueue` inserts `ResourceRequest`, injects `_id` as `UpdateId` into UiPath queue payload, maps `gb` → `uk` for environment, obtains token and `addToQueue`. `findOpenBots` returns latest document per resource where `status` is `QUEUED` or `IN_PROGRESS` for the given company. `update` sets `status`, `failure_reason`, `bot_details`, then calls `SBMigrationService.pushRequest`, `CITService.pushRequest`, `XeroExportService.pushRequest` before `save()`.
- **Schema** (`src/resource-request/resource-request.schema.ts`): `status` enum `FAILED`, `SUCCESS`, `IN_PROGRESS`, `QUEUED`, `CREATED`; indexed `company`, `user`, `resource`; `payload`, `bot_details` objects; timestamps.
- **SB migration webhook** (`src/shared/services/sb-migration-webhook.service.ts`): for `resource == "sb_dext_setup"`, `POST` `${XERO_SB_URL}/migration/dext-setup/:id` with basic auth `sleek-bot` / `XERO_SB_TOKEN`.
- **CIT webhook** (`src/shared/services/cit-webhook.service.ts`): for `cit_noa_extraction` or `cit_eci_filling`, `PUT` `${CIT_BASE_URL}/api/eci/bot/:id`.
- **Xero export webhook** (`src/shared/services/xero-export-webhook.service.ts`): for `bsm_export_bank_statement_xero`, `POST` `{country}_BSM_BASE_URL` + `/api/bank-transaction-export/xero-export-webhook` with `{country}_BSM_TOKEN` header; `country` from `payload.itemData.SpecificContent.Country`, default `SG`.
- **Auth** (`src/shared/guards/auth.guard.ts`): compares request `Authorization` or `query.api_key` to `SLEEK_BOT_PILOT_API_KEY`.
