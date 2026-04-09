# Migrate opening balance sheet from Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate opening balance sheet from Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | After Xero-to-SleekBooks migration work, operators can confirm that balance sheet aggregates in SleekBooks align with Xero for the checked fiscal years, reducing the risk of opening-position drift between systems. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API under `migrate/:companyId/balance-sheet` (authenticated via Sleek Back); used from back-office / migration orchestration that holds the Xero-connected tenant context (`request.xero`). |
| **Short Description** | On create, the service loads the Xero organisation’s financial year end, selects a two-year validation window, pulls Xero Balance Sheet reports per period, resolves the matching SleekBooks fiscal year, fetches or queues an ERPNext Balance Sheet report, and compares total assets, liabilities, and equity (including provisional P&L in equity) to Xero within a small tolerance. Success and failure are written to the app logger. The GET endpoint for status currently returns a fixed in-progress message rather than stored progress. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Xero Reports API (`getReportBalanceSheet`), organisation FY end (`getOrganisationFromXero`). **Downstream:** SleekBooks/ERPNext fiscal year lookup (`getFiscalYear`), balance sheet report read/queue (`getBSReport`, `queueBSReport`, `checkBSReport`, `getBSReportQueue`). **Adjacent:** Fiscal year migration (periods must exist), chart of accounts and other migration steps that feed reported balances. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `Migration` (read via `getLastestMigration` for the active migration record); `AppLogger` (write via `createLog` for `balancesheet` success/error). No balance-sheet-specific writes to `Migration` in this path. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | GET `/:companyId/balance-sheet` returns the literal string `Balance Sheet in progress` and does not reflect validation outcome or company from query; confirm intended UX. Validation uses hardcoded calendar-year windows around 2021–2023 relative to “today” and several company-name special cases for fiscal year naming—confirm product expectations vs implementation. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/migrate/migrate.controller.ts`**
  - `POST /migrate/:companyId/balance-sheet` — `startBalanceSheetMigration`: `SleekBackAuthGuard`, `ValidationPipe`, passes `request.xero` to `MigrateService.createBalanceSheetMigration`, responds `201` with `newBSMigration`.
  - `GET /migrate/:companyId/balance-sheet` — `getBSMigration`: `SleekBackAuthGuard`, calls `getBSProgress(query)`, responds `200` with `bsMigration`.
  - `@ApiOperation` summaries: “Create Balance Sheet Migration”, “Get Status of Company Balance Sheet”.
- **`src/migrate/migrate.service.ts`**
  - `createBalanceSheetMigration`: `getLastestMigration` → `xeroService.getOrganisationFromXero` → derives `fyStartYear` / `fyEndYear` from FY end month/day vs current date → `performBSValidation(...)` → on success `appLoggerService.createLog(..., 'balancesheet', ...)` with `BS_SUCCESS`; tenant missing logs `TENANT_NOT_FOUND` and throws.
  - `performBSValidation`: For each FY end in range, calls `xeroService.getReportBalanceSheet(xeroTenantId, endFY, 1, 'YEAR')`, parses rows via `processXeroBS` (totals for bank, assets, liabilities, equity); resolves SleekBooks FY with `sleekBooksService.getFiscalYear(startFY, endFY)`; loads BS via `getBSReport` or queues with `queueBSReport` / polls `checkBSReport` (up to ~10 minutes); compares ERPNext report lines (`Total Asset (Debit)`, `Total Liability (Credit)`, `Total Equity (Credit)`, provisional P&L line) to Xero totals within ±0.1; returns `[bsheetMatched, errorMsg]` when both years produce three-way matches (`fyMatchCount === 2`).
  - `processXeroBS` / `extractRowType`: Walk Xero report `Section` / `Row` / `SummaryRow` structure to extract aggregate totals.
  - `getBSProgress`: logs and returns static `'Balance Sheet in progress'`.
- **`SleekBackAuthGuard`**: Same back-office auth surface as other `migrate` routes (validates caller against Sleek Back).

**Usage confidence rationale:** The POST path implements full Xero-vs-SleekBooks aggregate reconciliation for the coded year window; the GET status path is a placeholder, so “observe migration status” in product terms is not fully supported in code.

**Criticality rationale:** Balance sheet alignment is central to migration sign-off and financial statement integrity across the two systems.
