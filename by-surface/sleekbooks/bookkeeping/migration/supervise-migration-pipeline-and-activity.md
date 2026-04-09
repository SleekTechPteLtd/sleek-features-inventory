# Supervise migration pipeline and activity

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Supervise migration pipeline and activity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can see which companies are in scope for Xero-to-SleekBooks migration, who owns each relationship, current pipeline status, and detailed audit logs so they can steer and troubleshoot the migration program. |
| **Entry Point / Surface** | Operator-facing tooling (Sleek Back–authenticated) calling **xero-sleekbooks-service** HTTP routes under `/migration`: `GET /migration/list/companies`, `GET /migration/list/account-managers`, `GET /migration/list/accountants`, `GET /migration/get-logs/:companyId`. All use `SleekBackAuthGuard`. Exact product screen or menu path is not defined in this repo. |
| **Short Description** | Returns a paginated, filterable list of migration-eligible companies (status, account manager, accountant, name/UEN search, optional renewal date range, abort reason when status is aborted). Supplies distinct account manager and accountant values for filters. Loads paginated migration activity logs for a company from the shared app logger, with optional grouped aggregation. |
| **Variants / Markets** | SG, HK (migration step definitions vary by `PLATFORM`; oversight APIs read the same `Migration` store and logger regardless of region) |
| **Dependencies / Related Flows** | **Upstream**: Company and ownership fields populated from Sleek Back (`syncCompaniesFromSleekBack`, `updateCompaniesFromSleekBack`, auto-migrate flows) and Xero tenant resolution via `XeroService`. **This feature**: read-only oversight plus `AppLoggerService.getAllByCompanyRegisterationId` for logs. **Related**: Full migration execution (`runSync`, `buildCOA`, Dext setup) and other `/migration` mutations are separate capabilities. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` (Mongoose model `Migration`); `apploggers` (Mongoose model `AppLogger` — logs retrieved by company registration id via `AppLoggerService`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `getMigrationCompanies` always sets `$and` with `{ $or: statusQuery }`; if `status` query param is omitted, `statusQuery` is empty — confirm expected MongoDB behaviour and whether the UI always sends status filters. Whether `limit` on account-manager/accountant list queries unintentionally truncates distinct values when `limit` is non-zero. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/migration/migration.controller.ts`

- **`GET /migration/list/companies`** — `GetEligibleCompanies` → `migrationService.getMigrationCompanies(request)`. `@UseGuards(SleekBackAuthGuard)`. `@ApiOperation`: list of companies with pagination and migration status.
- **`GET /migration/list/account-managers`** → `getAccountManagers(request)`. `SleekBackAuthGuard`.
- **`GET /migration/list/accountants`** → `getAccountants(request)`. `SleekBackAuthGuard`.
- **`GET /migration/get-logs/:companyId`** — `getMigrationLogsByRegNo` → `getLogsByCompanyId(id, page, pageSize, isGrouped)`. Query: `pageSize`, `page`, `isGrouped`. `SleekBackAuthGuard`. `@ApiOperation`: get migration logs by company id.

### `src/migration/migration.service.ts`

- **`getMigrationCompanies`**: Reads `limit`, `offset`, `search`, `accountmgr`, `accountant`, `status`, `reason`, `startdate`, `enddate` from `req.query`. Builds Mongo query on `migrationModel`: statuses in `failed`, `aborted`, `inprogress`, `posted`, `review`, `ready`; optional filters on `accountManager`, `accountant`, status/reason (including aborted + `notMigratedReason`), renewal date range; name/UEN regex search. Projects `companyName`, `companyRegNo`, `status`, `accountManager`, `accountant`, `renewalDate`, `comment`, `notMigratedReason`, `companyId`. Sort `updatedAt` desc, skip/limit pagination. Returns `{ total, data }`.
- **`getAccountManagers`**: `migrationModel.find` where `accountManager` not null/empty; optional `limit` on cursor; `union` of distinct `accountManager` strings.
- **`getAccountants`**: Same pattern for `accountant`.
- **`getLogsByCompanyId`**: Parses `pageSize`/`page` as numeric limits/offsets; `isGrouped` defaults to grouped unless `isGrouped === 'false'`. Delegates to `appLoggerService.getAllByCompanyRegisterationId(id, apiLimit, apiOffset, isGroupedData)`.

### `src/migration/schemas/migration.schema.ts`

- **Relevant fields** for oversight list: `status`, `companyName`, `companyRegNo`, `accountManager`, `accountant`, `renewalDate`, `comment`, `notMigratedReason`, `companyId`, timestamps via `@Schema({ timestamps: true })`.

### `src/migration/migration.module.ts`

- Registers `Migration` and `AppLogger` schemas for `MigrationService` and `AppLoggerService`.

### `src/app-logger/schemas/app-logger.schema.ts`

- Log documents include `companyUen`, `companyId`, `step`, `type`, `message`, user fields, `event`, `action`, `isAutoMigrate` — supports migration audit trail consumed by `getLogsByCompanyId`.
