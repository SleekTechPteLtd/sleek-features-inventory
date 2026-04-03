# Manage bookkeeping migration records

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage bookkeeping migration records |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Each client’s Xero-to-SleekBooks migration is represented as a durable record with status, pipeline steps, and comments so operations and services can run, monitor, and audit migrations consistently. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API under `@Controller('migration')` (base path `/migration`). Authenticated with `SleekBackAuthGuard` for operator-facing routes and `M2MAuthGuard` for service-to-service create/update hooks. Exact Sleek app or back-office screen navigation is not defined in this repo. |
| **Short Description** | Operators and backend services upsert migration documents (by UEN `companyRegNo` or M2M by `companyId`), list and filter companies in migration, fetch one migration by Mongo id or by UEN (with region-specific step definitions for SG vs HK), update step/status fields, start a migration by UEN, append UEN-scoped comments, delete by id, and pull paginated migration logs per company. Updates by UEN can trigger Sleek Back company sync. |
| **Variants / Markets** | `SG`, `HK` (step lists and `readMigrationSteps()` branch on `process.env.PLATFORM`; SG includes Dext setup, HK ends after COA). Schema allows `AU`, `UK` as region enums; deployment focus in code is SG/HK. |
| **Dependencies / Related Flows** | **Same repo**: `XeroService.getCompanyDataFromBQ` for tenant data; `SleekbooksService.checkCompanyInSB`; `HttpService` to `${SLEEK_BACK_API_BASE_URL}/v2/sb-migration/companies` for company sync; `AppLoggerService` for step and lifecycle logs; `MigrateService` / `CreateCompanyService` / `TasksService` for downstream migration execution (related, outside this CRUD slice). **External**: Sleek Back migration companies API, Xero BQ/tenant resolution. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` (Mongoose model `Migration`; default pluralised collection). Reads migration audit lines via `AppLoggerService` / `AppLogger` model for `get-logs/:companyId`. `xeroauthtokens` touched only in unrelated Xero init paths, not for core CRUD. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST /migration/trigger-coa-cron` has no auth guard — intentional test-only endpoint or exposure risk? `GET /migration` passes query straight to `find(query)` — confirm expected query shape and abuse controls. `updateByUen` can early-return without JSON response when skipping Dext setup paths (`return;` after logging) — clients should confirm handling. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/migration/migration.controller.ts`

- **`@Controller('migration')`** — base path `/migration`; `@ApiTags('migration')`.
- **`POST /update`** — `SleekBackAuthGuard`, body `Migration` → `MigrationService.create` (upsert by `companyRegNo`, enriches from Xero BQ, sets `initiatedBy` from `request.user.email`).
- **`POST /create`** — `M2MAuthGuard`, body `Migration` → `createMigrationData` (upsert by `companyId`).
- **`GET /`** — `SleekBackAuthGuard`, query passed through → `readAll`.
- **`GET /:id`** — `readById`.
- **`GET /uen/:id`** — `readByRegisterationId` + `readMigrationSteps` (returns `migration` and `migrationSteps`).
- **`PUT /:id`** — `update` by document id.
- **`PUT /uen/:id`** — `updateByUen` then `syncCompaniesFromSleekBack('all','all', companyId)`.
- **`PUT /uen/:id/start`** — `startMigrationByUEN`.
- **`DELETE /:id`** — `delete` (`findByIdAndRemove`).
- **`GET /get-logs/:companyId`** — pagination query → `getLogsByCompanyId`.
- **`PUT /uen/:id/comment`** — `updateCommentByUen` (sets `comment`).
- **`PUT /uen/:id/build-coa`**, **`GET /sync/:companyId`**, **`POST /update/company`**, **`POST /dext-setup/:id`**, **`GET /list/companies`**, **`GET /list/account-managers`**, **`GET /list/accountants`**, **`POST /trigger-coa-cron`** — related listing, sync, Dext, and cron triggers (broader migration ops surface).

### `src/migration/migration.service.ts`

- **`@InjectModel(Migration.name)`** — all persistence through `migrationModel`.
- **`create`**: `findOneAndUpdate({ companyRegNo }, { $set: migrationData }, { upsert: true, new: true })`.
- **`createMigrationData`**: upsert by `companyId` with `$currentDate` for `time` when `migratedDate` provided.
- **`readMigrationSteps`**: returns `migrationStepSG` vs `migrationStepHK` based on `PLATFORM === 'sg'`.
- **`updateByUen`**: `findOneAndUpdate({ companyRegNo: id }, { $set: data })` with step logging via `AppLoggerService` and conditional Dext-skip logic using `stepStatus` / `UpdateMigrationDTO.receiptSystemStatus`.
- **`updateCommentByUen`**: `findOneAndUpdate({ companyRegNo: id }, { $set: { comment } })`.
- **`syncCompaniesFromSleekBack` / `updateCompaniesFromSleekBack`**: HTTP GET/POST to Sleek Back and `updateOne`/`upsert` on `migrations` with Xero tenant from `getCompanyDataFromBQ`.

### `src/migration/schemas/migration.schema.ts`

- **Collection**: Mongoose class `Migration` — default collection name `migrations`.
- **Key fields**: `companyRegNo` (unique index), `companyId`, `status`, `currentStep` / `currentStepStatus` / `currentStepAction`, `comment`, `region`, ownership and assignment fields, COA/Dext-related flags and dates.
- **Regional step metadata**: `migrationStepSG` (company → fiscalyear → coa → dextsetup), `migrationStepHK` (company → fiscalyear → coa).

### `src/migration/dtos/create-migration.dto.ts`

- **`CreateMigrationDto`**: validated fields for company and migration metadata used when creating/updating from user-initiated payloads (aligned with `Migration` shape for create flow).

### `src/migration/dtos/update-migration.dto.ts`

- **`UpdateMigrationDTO`**: `PartialType(Migration)` plus `receiptSystemStatus` for UEN updates that affect Dext step handling.
