# Migrate fiscal year from Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate fiscal year from Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | SleekBooks fiscal year periods match the connected Xero organisation’s financial year end so books and reports use the same fiscal boundaries as the source tenant. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API under `migrate/:companyId/fiscal-year` (authenticated via Sleek Back); Xero organisation settings supply `financialYearEndMonth` / `financialYearEndDay` through the Xero API. |
| **Short Description** | On create, the service loads the Xero organisation, derives fiscal year start/end dates from the FY end month and day (including leap-year edge cases), and creates each required fiscal year in SleekBooks via the ERP integration. Success and failure are written to the app logger. A GET endpoint exists for status but currently returns a fixed message rather than persisted progress. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Xero OAuth-connected tenant (`getOrganisationFromXero`). **Downstream:** SleekBooks/ERPNext fiscal year creation (`addFYToSB`). **Adjacent:** Other migration steps in the same controller (COA, manual journals, invoices, bank transactions, profit and loss, balance sheet) that depend on fiscal periods being present. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | None for this capability path — fiscal year migration does not read or write the `Migration` Mongo model; it relies on Xero and SleekBooks APIs and structured logging. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | GET `/:companyId/fiscal-year` returns the literal string `Fiscal year in progress` and does not correlate query parameters to company or read stored state; `getFiscalYearProgress` is typed as `companyId: string` but receives the full `query` object from the controller. Confirm intended UX for “check progress” vs current implementation. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`migrate/migrate.controller.ts`**
  - `POST /migrate/:companyId/fiscal-year` — `startFYMigration`: `SleekBackAuthGuard`, `ValidationPipe`, calls `MigrateService.createFiscalYearMigration({ companyTenantId: id })`, responds `201` with `newFiscalMigration` (async result from service).
  - `GET /migrate/:companyId/fiscal-year` — `getFYProgress`: `SleekBackAuthGuard`, calls `getFiscalYearProgress(query)`, responds `200` with `fiscalMigration`.
  - `@ApiOperation` summaries: “Create Fiscal Year Migration”, “Get Status of Company Fiscal Year”.
- **`migrate/migrate.service.ts`**
  - `createFiscalYearMigration`: `getLastestMigration` → `xeroService.getOrganisationFromXero(tenantId)` → reads `financialYearEndMonth`, `financialYearEndDay` → builds year range from 2020 through a computed `nextYearEnd` → for each period computes `startFY` / `endFY` (handles Feb 28/29 leap logic) → `sleekBooksService.addFYToSB(companyName, companyRegNo, startFY, endFY)` → on success `appLoggerService.createLog(..., 'fiscalyear', ...)` with `FYE_SUCCESS`; on missing data or errors logs and throws.
  - `getFiscalYearProgress`: logs and returns static `'Fiscal year in progress'` (no DB or job polling).
- **`SleekBackAuthGuard`**: Validates `Authorization` header against `${SLEEK_BACK_API_BASE_URL}/users/me` — operator/back-office style access to the migration API.

**Usage confidence rationale:** Create path is fully implemented against Xero and SleekBooks; status endpoint is a placeholder, so confidence in “check progress” as described in product language is not High.

**Criticality rationale:** Fiscal periods underpin reporting, migration validation, and downstream steps; misalignment with Xero would affect accounting integrity.
