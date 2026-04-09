# Migrate invoices, bank transactions, and P&L from Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate invoices, bank transactions, and P&L from Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Purchase and sales invoices, bank activity, and profit-and-loss figures from Xero are reproduced in SleekBooks (ERPNext) so operators can complete a Xero-to-SleekBooks migration with traceable logging; bank migration also records the latest Xero transaction date on the migration record for continuity. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API: `POST` / `GET` under `migrate/:companyId/invoices`, `migrate/:companyId/bank-transaction`, and `migrate/:companyId/profit-and-loss`. All routes use `SleekBackAuthGuard` (back-office style access). Exact product UI path in Sleek App or admin tooling is not defined in this repo. |
| **Short Description** | **Invoices:** Fetches invoices from Xero, creates or matches purchase (`ACCPAY`) and sales (`ACCREC`) invoices in SleekBooks, submits drafts, replays payments and credit notes, and syncs attachments. **Bank:** Loads authorised bank transactions from Xero, creates and submits bank transactions in SleekBooks, drives reconciliation paths (manual journals, transfers, multicurrency checks), syncs attachments, and updates the migration document with `lastXeroTransactionDate`. **P&L:** Derives fiscal windows from the Xero organisation FY end, pulls Xero P&L reports and queued SleekBooks P&L reports, and compares totals (income, expenses, net profit) within tolerance. Success and errors for each stream are written to the app logger. GET endpoints for all three streams currently return fixed “in progress” placeholder strings rather than per-stream persisted status. |
| **Variants / Markets** | SG, HK, AU, UK (company `region` on `Migration` schema; COA logic elsewhere branches on `PLATFORM` / HK — these three paths do not duplicate that branching but run in the same regional migration programme). |
| **Dependencies / Related Flows** | **Upstream:** Xero API via `XeroService` (invoices, bank transactions, organisation, profit and loss report). **Downstream:** SleekBooks/ERPNext via `SleekbooksService` (invoice CRUD, payments, bank transactions, journals, reports, attachments). **Adjacent:** Fiscal year and COA migrations (same `MigrateService`); `getLastestMigration` reloads the `Migration` document by `_id` before each operation. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` — `findOneAndUpdate` on bank transaction migration sets `lastXeroTransactionDate` (and `getLastestMigration` reads by `_id` for all three streams). `apploggers` — structured logs for events `invoices`, `banktransaction`, and `reports` (P&L). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | GET handlers return static strings (`getInvoiceMigrationDetails`, `getBankTransactionDetails`, `getPnLReportStatus`) with comments referencing future front-end design — confirm roadmap for real per-stream status vs operational reliance on logs and API responses from POST only. P&L fiscal-year window logic uses hard-coded base years (`2021`–`2023` range derived from `2022` anchor); confirm whether this should track wall-clock or tenant-specific rollover. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/migrate/migrate.controller.ts`

- **Invoices**
  - `POST /migrate/:companyId/invoices` — `startInvoices`: `SleekBackAuthGuard`, `ValidationPipe`, body passed to `createInvoicesMigration`.
  - `GET /migrate/:companyId/invoices` — `getInvoicesExtractionDetails`: `getInvoiceMigrationDetails(query)`.
  - `@ApiOperation`: “Create Purchase and sales Invoices Migration”, “Get Status of Purchase and sales Invoices Migration”.
- **Bank transactions**
  - `POST /migrate/:companyId/bank-transaction` — `createBankTransactions` → `createBankTransactionsMigration(body)`.
  - `GET /migrate/:companyId/bank-transaction` — `getBankTransactionMigrationDetails` → `getBankTransactionDetails(query)`.
  - `@ApiOperation`: “Create Bank Transaction Migration”, “Get Status of Bank Transaction Migration”.
- **Profit and loss**
  - `POST /migrate/:companyId/profit-and-loss` — `createPnLReport` → `createPnLReports(body)`.
  - `GET /migrate/:companyId/profit-and-loss` — `getPnLReportStatus` → `getPnLReportStatus(query)`.
  - `@ApiOperation`: “Create Profit and Loss Report Migration”, “Get Status of Profit and loss Migration”.

### `src/migrate/migrate.service.ts`

- **`createInvoicesMigration`**: `getLastestMigration` → `xeroService.getInvoices(companyTenantId)` → `extractDirectXeroInvoice` (purchase/sales creation from Xero detail, payments, credit notes, attachment download/upload via `checkDownloadDirecXeroInvoice`) → `appLoggerService.createLog(..., 'invoices', ...)` with `INVOICES_SUCCESS` or error.
- **`getInvoiceMigrationDetails`**: returns static `'Invoices extraction in progress'`.
- **`createBankTransactionsMigration`**: `getLastestMigration` → `xeroService.getBankTranscations` → persists `lastXeroTransactionDate` via `migrationModel.findOneAndUpdate({ companyRegNo }, { $set: { lastXeroTransactionDate } }, { upsert: true, new: true })` → `extractDirectXeroBankTrans` (create/submit bank transactions, reconciliation paths, `checkDownloadDirecXeroBanktran`) → `appLoggerService.createLog(..., 'banktransaction', ...)` with `BT_SUCCESS` or error.
- **`getBankTransactionDetails`**: returns static `'Bank transactions extraction in progress'`.
- **`createPnLReports`**: `getLastestMigration` → `getOrganisationFromXero` for FY end month/day → computes `fyStartYear` / `fyEndYear` → `performPNLValidation` (Xero `getReportProfitAndLoss`, SleekBooks `getPnLReport` / `queuePnLReport` / polling, `processXeroPnL` vs ERP totals) → on thrown path `appLoggerService.createLog(..., 'reports', ...)`; successful path returns `[plostMatched, errorMsg]` from `performPNLValidation` without a success log in the shown `createPnLReports` try block (errors log in `catch`).
- **`getPnLReportStatus`**: returns static `'PROFIT AND LOSS extraction in progress'`.

### Supporting types

- **`src/migration/schemas/migration.schema.ts`**: `lastXeroTransactionDate` on `Migration`; `region` enum includes SG, HK, AU, UK.
- **`src/migrate/migrate.module.ts`**: Registers `MigrateController`, `MigrateService`, Mongoose `Migration` model, `AppLogger`, `XeroService`, `SleekbooksService`.

**Usage confidence rationale:** POST flows are substantial and integrated with Xero and SleekBooks; GET “status” endpoints are placeholders, so end-to-end “status visibility per stream” in the API is not yet High.

**Criticality rationale:** Moves core accounting artefacts (invoices, bank lines, P&L validation); errors affect data completeness and cutover trust.
