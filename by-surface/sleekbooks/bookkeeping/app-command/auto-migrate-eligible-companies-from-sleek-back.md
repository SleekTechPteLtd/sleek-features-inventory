# Auto-migrate eligible companies from Sleek Back

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Auto-migrate eligible companies from Sleek Back |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | FYE-eligible companies from Sleek Back get migration records created or advanced to a posted state so automated bookkeeping migration can run without operators creating each migration manually. |
| **Entry Point / Surface** | Scheduled or manual CLI: NestJS command `migrate:eligible-companies` (`nestjs-command`). Runs only when `ENABLE_AUTO_MIGRATION=true` (otherwise exits immediately). Not a Sleek app screen; typically invoked by infrastructure cron. |
| **Short Description** | The service calls Sleek Back for companies eligible by financial year end (`filterByFYE=true`), skips companies already present in SleekBooks or missing Xero tenant data from BQ, then either upserts a new migration with `status: posted` and `isAutoMigrate: true` or, if a migration already exists in `review` or `ready`, updates it to `posted` and logs a start event so downstream migration workers can proceed. |
| **Variants / Markets** | `SG`, `HK` (repo deploys with `PLATFORM`; eligibility list comes from Sleek Back; company payloads carry `country` and region-aligned fields). |
| **Dependencies / Related Flows** | **External**: Sleek Back `GET /v2/sb-migration/companies?filterByFYE=true` (basic auth via `SLEEK_SERVICE_CLIENT_ID` / `SLEEK_SERVICE_CLIENT_SECRET`). **Same repo**: `XeroService.getCompanyDataFromBQ(companyRegNo)` for `xeroTenantId`; `SleekbooksService.checkCompanyInSB(companyRegNo)` to avoid duplicate SB companies; `AppLoggerService.createLog` for migration start logging. **Related**: `Migration` document lifecycle and `runSync` / task processing for posted migrations (`manage-bookkeeping-migration-records`, migration pipeline capabilities). |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` (Mongoose `Migration` model: `findOne`, `updateOne`, `findOneAndUpdate` with upsert). `apploggers` (Mongoose default plural for `AppLogger`) via `AppLoggerService.createLog` on successful enqueue. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | FYE eligibility rules are enforced on Sleek Back; not visible in this repo. Cron frequency and failure alerting are deployment concerns not defined here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/app.command.ts`

- **`@Command({ command: 'migrate:eligible-companies', describe: 'migrate eligible companies from sleek-back' })`** → `migrateEligibleCompanies()`.
- Sets `GlobalService.isStartFromCommand = true`.
- Early return unless `process.env.ENABLE_AUTO_MIGRATION === 'true'`.
- Calls `migrationService.autoMigrateEligibleCompaniesFromSleekback()`; logs start/end; `process.exit(0|1)`.

### `src/migration/migration.service.ts`

- **`autoMigrateEligibleCompaniesFromSleekback()`** (lines ~739–837):
  - `HttpService.get(\`${SLEEK_BACK_API_BASE_URL}/v2/sb-migration/companies?filterByFYE=true\`)` with Sleek service basic auth.
  - Iterates `data.data`; requires `companyRegNo`; skips if `sleekbooksService.checkCompanyInSB` is true; skips if `xeroService.getCompanyDataFromBQ` returns falsy (no tenant).
  - **Existing migration**: if `findOne({ companyRegNo })` exists, logs status; if status is `review` or `ready`, `updateOne` sets `initiatedBy`, owner names, `status: 'posted'`, `isAutoMigrate: true`, then `appLoggerService.createLog('info', ..., 'start', ..., 'company')`.
  - **No existing migration**: `findOneAndUpdate({ companyRegNo }, { $set: migrationData }, { upsert: true, new: true })` with fields including `companyName`, `targetTool: 'sb'`, `companyId`, `companyTenantId` from BQ, `status: 'posted'`, `isAutoMigrate: true`, then `createLog` for start.
- Per-company errors are logged; outer failure logs `Failed when auto migrate eligible companies`.

### Related command (same file, separate script)

- `script:deleteMigrationInReviewOrReady` → `deleteMigrationInReviewOrReady()` deletes documents with `status` in `['review','ready']` — maintenance utility, not part of the auto-migrate eligibility flow.
