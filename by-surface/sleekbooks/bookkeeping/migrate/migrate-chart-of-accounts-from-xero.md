# Migrate chart of accounts from Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate chart of accounts from Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | The company’s active Xero accounts are recreated (or matched) in SleekBooks with correct ERP account groups and Xero account IDs stored where needed, so downstream migration and bookkeeping use aligned ledgers. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API `POST` / `GET` `/migrate/:companyId/coa` (Sleek Back auth). COA extraction is also driven from the migration orchestration layer (`MigrationService.buildCOA`, `buildCOAManual`, automated migration tasks) which passes a full migration record into `MigrateService.createCOAMigration`. |
| **Short Description** | Loads active accounts from Xero (`getCOAs`), maps each Xero account type to SleekBooks parent groups (with SG vs HK branching via `PLATFORM`), creates or resolves accounts and linked bank accounts through the SleekBooks integration, and stores Xero `AccountID` on ERP accounts when missing. Success and failure are logged to the app logger. The GET status route currently returns a fixed in-progress message rather than reading migration document state. |
| **Variants / Markets** | `SG`, `HK` (account group mapping branches on `process.env.PLATFORM` / `site === 'hk'` for several types, e.g. direct costs, sales, revenue, other income) |
| **Dependencies / Related Flows** | **Upstream:** Xero Accounting API accounts (`XeroService.getCOAs`), OAuth tenant access (middleware prepares `xero-node` client on `/migrate` routes). **Downstream:** SleekBooks/ERPNext account and bank APIs (`SleekbooksService.checkCoa`, `checkBankAccount`, `getAccountByResourceName`, `updateAccountID`). **Adjacent:** Migration workflow documents (`Migration` model: `currentStep` includes `coa`, `isCOACompleted`, `coaScheduledDate`) and manual build-COA endpoints on the migration module; fiscal year migration often precedes COA in step order. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` — read via `getLastestMigration` when the caller supplies a document `_id` (orchestrated flows). COA run logs to app logger (Mongoose `AppLogger` schema / configured collection). No COA-specific write to `Migration` inside `createCOAMigration` in the reviewed path; step completion flags are handled in `migration.service.ts`. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `POST /migrate/:companyId/coa` passes `request.xero` (`{ xero, tenants }` from `LoggerMiddleware`) into `createCOAMigration`, which expects migration fields such as `companyTenantId` and optionally `_id` for `getLastestMigration` — unlike `POST .../fiscal-year`, which passes `{ companyTenantId: id }`. Confirm whether this route is dead code, wrapped by another client that mutates the request, or broken. GET status does not return structured progress; is operator visibility intended to come from the migration API / Sleek Back only? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/migrate/migrate.controller.ts`**
  - `POST /migrate/:companyId/coa` — `startCOAMigration`: `SleekBackAuthGuard`, `ValidationPipe`, calls `MigrateService.createCOAMigration(request.xero)`, responds `201` with `newCOAMigration`.
  - `GET /migrate/:companyId/coa` — `getCOAMigration`: `SleekBackAuthGuard`, calls `getCOAProgress(query)`, responds `200` with `coaMigration`.
  - `@ApiOperation` summaries: “Create COA Migration”, “Get Status of Company COA”.
- **`src/migrate/migrate.service.ts`**
  - `createCOAMigration`: `getLastestMigration` → `xeroService.getCOAs({ xeroTenantId })` (throws if no accounts) → `extractCOA(accounts, companyInfo)` → on success `appLoggerService.createLog(..., 'coa', ...)` with `COA_SUCCESS`; errors logged with `'coa'`.
  - `extractCOA`: iterates Xero accounts; `switch` on Xero account type (`BANK`, `EXPENSE`, `DIRECTCOSTS`, `CURRENT`, `SALES`, `EQUITY`, etc.) → `sleekBooksService.checkCoa` with mapped parent (`Current Assets`, `Expenses`, `Income` vs `Revenue`, etc.); for `BANK`, also `checkBankAccount`, optionally `getAccountByResourceName` + `updateAccountID` to persist Xero `AccountID`; returns `[count, 'Done']` or `[count, 'Error']` if processed vs successful counts diverge.
  - `getCOAProgress`: logs and returns static `'COA in progress'` (no DB polling).
- **`src/common/middleware/logger.middleware.ts`**
  - Applied to `/migrate` in `app.module.ts`; sets `req['xero'] = { xero, tenants }` after token refresh and tenant resolution.
- **`src/migration/schemas/migration.schema.ts`**
  - Pipeline steps include `coa`; fields `isCOACompleted`, `coaScheduledDate` support migration tracking outside the migrate controller’s GET placeholder.
- **`src/xero/xero.service.ts`**
  - `getCOAs`: Xero Accounting API list accounts with default `whereClause` active accounts.

**Usage confidence rationale:** Core import logic is implemented end-to-end from Xero to SleekBooks helpers; HTTP POST wiring and GET status are weak or placeholder relative to the described operator journey, hence Medium.

**Criticality rationale:** Chart of accounts underpins all migrated transactions, reporting, and reconciliation; mis-mapping would corrupt books.
