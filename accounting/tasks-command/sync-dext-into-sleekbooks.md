# Sync Dext into SleekBooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Dext into SleekBooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can refresh SleekBooks-side company data and pull Dext receipt and expense data through the service layer so bookkeeping records stay aligned with ERPNext, Sleek Back, and BigQuery-sourced Dext pipelines. |
| **Entry Point / Surface** | **CLI (operational):** NestJS Command `script:dext-to-sleekbooks` — `TaskCommand.dextSync()` sets `GlobalService.isStartFromCommand = true`, logs start/end, and exits the process with code 0 or 1. Not a Sleek App screen or HTTP route. |
| **Short Description** | The script runs `handleDextCron`: it paginates through ERPNext companies and upserts the local company cache (enriched from Sleek Back and BigQuery, including Dext account ids), creates a MongoDB extraction run of type `dext`, then runs Dext receipt sync (`runSync`) and expense-report sync (`runExpenseReportSync`) which query BigQuery Dext tables and push extracted rows into the ERP path via `BQService`. Company rows get `last_sync` / `sync_start_date` updates; extraction documents move through `posted` → `inprogress` → `completed` or `aborted`. |
| **Variants / Markets** | SG (extraction payload in `handleDextCron` sets `region: 'SG'`; schema allows HK, AU, UK but this command path fixes SG). |
| **Dependencies / Related Flows** | **Upstream:** `ErpnextService` (company list for DB refresh), `SleekBackService` + `BQService` (company enrichment, Dext account ids, Hubdoc links inside `CompaniesService`). **Pipeline:** `BQService` — `getCompanyFromErpNext`, `getCompanyAccountingTool`, `getTotalCountDext` / `extractFromDext` across `tb_dext_directload_*` tables, and `getTotalCountExpenseReportDext` / `extractExpenseFromDext` for `vw_dext_directload_costs_expensereports`. **Sibling:** `script:hubdoc-to-sleekbooks` and commented cron/interval handlers in `TasksService`. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | `extractions`: insert via `ExtractionService.create` (type `dext`, status `posted`); `DextService` updates same document by id to `inprogress`, then `completed` or `aborted`. `companies`: read via `getCompaniesFromDB`; `updateCompaniesInDB` upserts from ERPNext/Sleek Back/BQ; Dext sync loops update `last_sync`, `sync_start_date`, and per-row saves after extraction. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `runExpenseReportSync` breaks after the first company in the loop (line 444), so only one company is processed per run — confirm if intentional. `runSync` and `runExpenseReportSync` both update the same extraction document’s status; clarify expected sequencing vs double-writes. `updateCompaniesInDB` is called with an empty token string — confirm Sleek Back enrichment still behaves as intended for production runs. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`tasks/tasks.command.ts`**
  - `@Command({ command: 'script:dext-to-sleekbooks', describe: 'sync Dext to SleekBooks' })` → `dextSync()` → `taskService.handleDextCron()`, `GlobalService.isStartFromCommand = true`, `process.exit(0|1)`.
- **`tasks/tasks.service.ts`**
  - `handleDextCron()`: `companiesService.updateCompaniesInDB('', '10', '0')`; builds `extraction` `{ status: 'posted', schedule: 'test', startDate: 1970-01-01, endDate: end of today, region: 'SG' }`; `extractionService.create({ extractionType: dext, ... })`; `dextService.runSync(dextExtraction)`; `dextService.runExpenseReportSync(dextExtraction)`.
  - `handleDextInterval()` (commented interval): finds latest posted `dext` extraction and calls `runSync` + `runExpenseReportSync` without the company refresh step.
- **`extraction/extraction.service.ts`**
  - `create`: normalizes `startDate`/`endDate`, persists `Extraction` Mongoose document.
- **`companies/companies.service.ts`**
  - `updateCompaniesInDB(token, limit, offset)`: loops `erpnextService.getCompaniesByFilter` with pagination, `processAndSaveCompanies` → `getCompaniesData` (Sleek Back, `getDextAccountIds`, `getHubdocId`) → `processAndUpdateInDB` bulk upsert on company name key.
  - `getCompaniesFromDB`: Mongo find with optional filters; the fourth argument is applied to `.skip` and the fifth to `.limit` (parameter names `limit`/`offset` are inverted relative to Mongoose). Dext calls use `'0','0'` → skip 0, limit 0; Mongoose treats `limit(0)` as no cap, so all matching companies are returned.
- **`dext/dext.service.ts`**
  - `runSync(extractionTask)`: sets extraction `inprogress`; loads all companies from DB; per company skips if `last_sync` within 120 minutes; derives date window from `current_fye` / Xero active tenant vs `sync_start_date`; for each Dext table family (`inbox_costs`, `inbox_sales`, `archived_costs`, `archived_sales`) calls `bqService.getTotalCountDext` and `bqService.extractFromDext`; updates company `sync_start_date` / `last_sync`; extraction → `completed` or on error `aborted`.
  - `runExpenseReportSync(extractionTask)`: similar status updates; `getTotalCountExpenseReportDext` / `extractExpenseFromDext` targeting `vw_dext_directload_costs_expensereports` and archived costs table; **`break` after first matching company**.
  - `runApiSync` (parametric API-style sync with explicit date range and UEN) — related but not used by `handleDextCron`.

**Usage confidence rationale:** The CLI command and method chain are explicit; confidence is medium because pagination/`limit` semantics for `getCompaniesFromDB('0','0')`, empty token on refresh, and the expense-report `break` need operational confirmation.

**Criticality rationale:** Dext-to–SleekBooks ingestion underpins receipt and expense data used downstream for bookkeeping; failures leave data stale or extraction runs stuck.
