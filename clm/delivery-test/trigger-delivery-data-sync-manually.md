# Trigger Delivery Data Sync Manually

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Trigger Delivery Data Sync Manually |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User / Developer (admin profile required) |
| **Business Outcome** | Allows operators to immediately propagate user and company records from MongoDB into the service delivery PostgreSQL database without waiting for the next scheduled hourly sync, ensuring the delivery platform reflects the latest CRM data on demand. |
| **Entry Point / Surface** | Sleek Admin App > Developer Tools > Triggers tab > One-Time Sync > Sync Users / Sync Companies |
| **Short Description** | Provides manual one-time triggers for full data sync of both users and companies from MongoDB to PostgreSQL. The operator clicks "Sync Users" or "Sync Companies" in the Developer Tools panel; each button calls the corresponding `POST /seed/sync/users` or `POST /seed/sync/companies` endpoint. Unlike the scheduled incremental sync (last 1 hour delta), the manual trigger performs a full collection scan and upserts all records. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | MongoDB `users` and `companies` collections (source); service delivery PostgreSQL `users` and `companies` tables (target); BullMQ / Redis (queue backend for scheduled sync — this feature bypasses the queue and runs synchronously inline); scheduled hourly incremental sync (this feature replaces its delta with a full scan) |
| **Service / Repository** | sleek-billings-frontend (UI), sleek-service-delivery-api (backend) |
| **DB - Collections** | MongoDB: `users`, `companies`; PostgreSQL: `users` table (via `PostgresUser` entity), `companies` table (via `PostgresCompany` entity) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is this screen accessible in production or only staging/dev environments (page is labeled "Developer Tools" and lives under `TestDelivery`)? Are there guardrails preventing concurrent manual syncs? Why is the SeedController excluded from Swagger (`@ApiExcludeController`)? Should companies and users sync always be triggered together, or are they intentionally separate actions? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

| File | Key evidence |
|---|---|
| `src/seed/seed.controller.ts:9–11` | `@ApiExcludeController()`, `@Controller('seed')`, `@SleekBackAuth('admin')` — excluded from public Swagger; requires admin sleek-back auth token |
| `src/seed/seed.controller.ts:45–55` | `POST /seed/sync/companies` → `companiesScheduler.syncAllCompanies()`; `POST /seed/sync/users` → `usersScheduler.syncAllUsers()` — two separate trigger endpoints |
| `src/schedulers/users.scheduler.ts:49–120` | `syncAllUsers()` — full MongoDB scan: all `@sleek.com` users (excluding `+` addressing and `autotest` prefix), plus master user by `SLEEK_MASTER_AUTHORIZATION_KEY`; upserts to PostgreSQL via `external_ref_id` |
| `src/schedulers/companies.scheduler.ts:50–82` | `syncAllCompanies()` — full MongoDB scan: all non-draft companies; upserts to PostgreSQL via `external_ref_id` |
| `src/schedulers/queues/users-sync.processor.ts:56–69` | Scheduled processor (BullMQ) does **incremental** sync (last 1 hour delta via `updatedAt`); manual trigger does full scan — key behavioural difference |
| `src/schedulers/queues/companies-sync.processor.ts:52–76` | Same pattern for companies: scheduled = incremental, manual = full |
| `src/schedulers/schemas/user.schema.ts:6` | MongoDB collection: `@Schema({ collection: 'users' })` — fields: `_id`, `first_name`, `middle_name`, `last_name`, `email`, `status`, `auth_token` |
| `src/schedulers/schemas/company.schema.ts:6` | MongoDB collection: `@Schema({ collection: 'companies' })` — fields: `_id`, `name`, `status`, `company_type`, `uen`, `incorporation_date` |
| `src/schedulers/queues/users-sync-queue.service.ts:57–76` | `triggerSync()` adds a one-off BullMQ job (`users-sync-manual-{timestamp}`) for queue-based manual trigger (alternate path, not used by the seed controller) |
| `src/schedulers/queues/companies-sync-queue.service.ts:59–77` | Same pattern for companies queue-based manual trigger |
| `src/pages/Delivery/TestDelivery.jsx` (sleek-billings-frontend) | UI entry point: "One-Time Sync" section with "Sync Users" and "Sync Companies" buttons; page titled "Developer Tools" under Delivery module |
| `src/services/service-delivery-api.js` (sleek-billings-frontend) | `syncUsers()` → `POST /seed/sync/users`; `syncCompanies()` → `POST /seed/sync/companies`; API client uses `VITE_SERVICE_DELIVERY_API_URL` with Bearer token auth |
