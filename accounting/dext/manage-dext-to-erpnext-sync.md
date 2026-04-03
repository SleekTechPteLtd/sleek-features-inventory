# Sync Dext costs and sales into ERPNext

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Dext costs and sales into ERPNext |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System |
| **Business Outcome** | Client companies’ Dext-sourced purchase and sales documents in BigQuery are reflected as ERPNext purchase and sales invoices so bookkeeping stays aligned with captured receipts and invoices. |
| **Entry Point / Surface** | Internal Nest API `GET /dext`, `POST /dext/sync`, `POST /dext/report`; CLI `script:dext-to-sleekbooks` (`TasksService.handleDextCron`); scheduled/queued extraction tasks (`extractionType: dext`, status `posted`) via `TasksService.handleDextInterval` when enabled — no end-user app navigation in this repo. |
| **Short Description** | Loads companies from MongoDB (optionally filtered by UEN), reads Dext direct-load tables in BigQuery (inbox/archived costs and sales), resolves the ERPNext company, and creates missing purchase or sales invoices in ERPNext. A separate path syncs expense-report rows into purchase invoices. Task runs update extraction status and company `last_sync` / `sync_start_date`. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | Google BigQuery (Dext tables, `asia-southeast1`); Xero BigQuery dataset (`active_tenants` for FYE-aware windowing); ERPNext via `ErpnextService` (create/get invoices); company roster and `dext_account_ids` from MongoDB; `CompaniesService.updateCompaniesInDB` before cron Dext run; SleekBack/indirect company enrichment when companies are refreshed from ERPNext. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | `companies`, `extractions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `GET /dext` calling `runSync({})` is intentional for operations or legacy; controller has no method-level auth decorators — confirm global guards / network isolation. `PlatformService` is injected into `DextService` but not referenced in the reviewed file. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Surfaces and orchestration

- **`dext/dext.controller.ts`**: `GET /dext` → `DextService.runSync({})`. `POST /dext/sync` → `runApiSync(start_date, end_date, uen)` for targeted sync. `POST /dext/report` → `testRunExpenseReportSync` (company name + date range).
- **`tasks/tasks.service.ts`**: `handleDextCron` refreshes companies then creates a `dext` extraction document and awaits `runSync` and `runExpenseReportSync`. `handleDextInterval` loads the latest posted `dext` extraction and invokes both (non-awaited in snippet — fire-and-forget). CLI `script:dext-to-sleekbooks` triggers `handleDextCron` (`tasks.command.ts`).
- **`dext/dext.service.ts`**:
  - **`runApiSync`**: `CompaniesService.getCompaniesFromDB(null, uen, …)`; for each company, `BQService.getCompanyFromErpNext`, then four pipelines: `tb_dext_directload_inbox_costs`, `inbox_sales`, `archived_costs`, `archived_sales` — each `getTotalCountDext` then `extractFromDext` when count &gt; 0.
  - **`runSync` (extraction-driven)**: Sets extraction status `inprogress` → loads all companies (`getCompaniesFromDB` with null filters); skips companies synced in the last 120 minutes; adjusts `startDate` using `current_fye`, Xero active tenant check (`getCompanyAccountingTool`), and `sync_start_date`; same four BigQuery tables; updates `sync_start_date`, `last_sync`, extraction `completed` / `aborted`.
  - **`runExpenseReportSync` / `testRunExpenseReportSync`**: Expense-report view `vw_dext_directload_costs_expensereports` joined to archived costs; `getTotalCountExpenseReportDext` / `extractExpenseFromDext`.

### BigQuery and ERPNext

- **`biqquery/bigquery.service.ts`**: `getTotalCountDext`, `extractFromDext` (paginated LIMIT 100) — maps `costsKind` / `salesKind` to ERPNext: `INVOICE`/`RECEIPT` → purchase invoice (`createPurchaseInvoiceFromDext`), `SALES_INVOICE` → sales invoice (`createSalesInvoiceFromDext`), skip if invoice already exists. Filters by `dext_account_ids` (`accountCrn`) when present, else `starts_with` on `company_name`. `getCompanyFromErpNext` resolves ERP company by UEN or name. `getCompanyAccountingTool` uses Xero BQ `active_tenants`. `extractExpenseFromDext` → `createPurchaseInvoiceFromDextExpenseReport`.

### Companies

- **`companies/companies.service.ts`**: `getCompaniesFromDB` Mongo query by name/UEN/sleek_id with limit/skip (note: Dext passes `'0','0'` for limit/offset — verify intended pagination). `getCompaniesData` / `processAndUpdateInDB` populate `dext_account_ids` from `BQService.getDextAccountIds` for ongoing company sync.

### Schemas

- **`extraction/schemas/extraction.schema.ts`**: `extractionType`, `status` (`posted` → `inprogress` → `completed` / `aborted`), `startDate`, `endDate`, `region` enum SG/HK/AU/UK.
- **`companies/schemas/companies.schema.ts`**: `name`, `uen`, `dext_account_ids`, `last_sync`, `sync_start_date`, `current_fye`, etc.
