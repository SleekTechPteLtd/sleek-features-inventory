# Advance Xero migration workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Advance Xero migration workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can drive each company’s Xero-to-SleekBooks migration by UEN, keep step and status aligned with reality, recover chart-of-accounts builds, and test COA batch processing without losing audit trail. |
| **Entry Point / Surface** | Back-office operations (Sleek Back–authenticated migration API); M2M hooks for system-driven create/sync where noted |
| **Short Description** | Exposes CRUD and UEN-scoped flows for migration records: start by UEN, update current step/status and comments, fetch step definitions (SG vs HK), sync company facts from Sleek Back, build COA manually when eligible, and read migration logs. A scheduled COA job retries failed COA steps; a separate test endpoint invokes the same COA handler for manual batch testing. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Sleek Back (`/v2/sb-migration/companies` for sync and auto-eligible lists); Xero (tenant resolution via `getCompanyDataFromBQ`, token refresh via `XeroAuthToken`); SleekBooks (`MigrateService` / `CreateCompanyService` for company, fiscal year, COA, Dext); `AppLoggerService` for step/company logs; interval-driven `runSync` for posted migrations |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` (Migration schema); `xeroauthtokens` (COA cron Xero session init) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `POST /migration/trigger-coa-cron` has no auth guard in code—confirm whether this is intentionally open in non-prod only; exact product UI labels for “Sleek Back” migration screens not in this repo |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `migration/migration.controller.ts`

- **Auth**: Most routes use `SleekBackAuthGuard`; `POST /migration/create`, `POST /migration/update/company`, `POST /migration/dext-setup/:id` use `M2MAuthGuard`. `POST /migration/trigger-coa-cron` has **no** `@UseGuards` in source.
- **UEN / start / COA**: `GET /migration/uen/:id` returns migration by `companyRegNo` plus `readMigrationSteps()`; `PUT /migration/uen/:id/start` calls `startMigrationByUEN`; `PUT /migration/uen/:id/build-coa` calls `buildCOAManual`.
- **Step updates**: `PUT /migration/uen/:id` with `UpdateMigrationDTO` calls `updateByUen` then `syncCompaniesFromSleekBack('all','all', companyId)`.
- **COA test trigger**: `POST /migration/trigger-coa-cron` → `tasksService.handleBuildCOA()` (Swagger: “Test endpoint to manually trigger COA cron job”).
- **Lists / logs**: `GET /migration/list/companies`, `list/account-managers`, `list/accountants`; `GET /migration/get-logs/:companyId` for app logger output.

### `migration/migration.service.ts`

- **Persistence**: `InjectModel(Migration.name)` for all migration reads/writes; `startMigrationByUEN` sets status `posted`, owner/initiator fields, logs via `appLoggerService`.
- **Steps**: `readMigrationSteps()` returns `migrationStepSG` vs `migrationStepHK` from schema based on `process.env.PLATFORM`.
- **UEN updates**: `updateByUen` patches `currentStep`, `currentStepStatus`, `currentStepAction`, `status`, Dext skip logging branches, optional COA failure reschedule via `getCOAScheduledDate()`.
- **Manual COA**: `buildCOAManual` validates step index vs `coa`, delegates to `buildCOA` when `currentStepStatus === 'failed'`.
- **Automated COA**: `buildCOA` → `migrateService.createCOAMigration`, retries/abort fields on failure.
- **External**: `syncCompaniesFromSleekBack` / `updateCompaniesFromSleekBack` HTTP to Sleek Back; `xeroService.getCompanyDataFromBQ`; `sleekbooksService.checkCompanyInSB`.

### `tasks/tasks.service.ts`

- **`handleBuildCOA`**: `@Cron` in Asia/Singapore; calls `migrationService.initializeXeroConfig()`, skips if `GlobalService.isStartFromCommand`, iterates cursor `currentStep: 'coa', currentStepStatus: 'failed', remainingRetries > 0`, calls `migrationService.buildCOA` per task.
- **`handleMigrationInterval`**: Picks `posted` / `inprogress` work and invokes `migrationService.runSync` for the migration pipeline (company → fiscal year/COA → Dext on SG when COA complete).

### `migration/schemas/migration.schema.ts`

- **Steps**: `stepStatus` / `stepStatusHK` define order (`company` → `fiscalyear` → `coa` [→ `dextsetup` SG]); `migrationStepSG` / `migrationStepHK` metadata for UI/API consumers.
- **Regions enum** includes SG, HK, AU, UK; runtime lists above focus SG vs HK for step arrays.
