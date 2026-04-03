# Sync Dext expense reports

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Dext expense reports |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can pull Dext expense-report data for a company and period from BigQuery into ERPNext as purchase invoices so consolidated expense reports match archived cost lines in the books. |
| **Entry Point / Surface** | **HTTP:** `POST /dext/report` (Nest `DextController`) with JSON body `company_name`, `start_date`, `end_date` → `DextService.testRunExpenseReportSync`. **Batch:** `TasksService.handleDextCron` creates a `dext` extraction and awaits `runExpenseReportSync(extraction)` after the main Dext `runSync` — not a Sleek App screen. |
| **Short Description** | Queries BigQuery view `vw_dext_directload_costs_expensereports` for distinct expense-report codes by company and publish window, joins to `tb_dext_directload_archived_costs` on `item_code`, and creates ERPNext purchase invoices via `createPurchaseInvoiceFromDextExpenseReport`. The on-demand HTTP path uses a single named company and optional widened date window (start defaults to end minus 24 months when provided). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** MongoDB `companies` (scheduled path), Google BigQuery Dext dataset (`BQPROJECTID` / `BQDATASET`, region `asia-southeast1`). **Downstream:** `ErpnextService.createPurchaseInvoiceFromDextExpenseReport`. **Related:** Full Dext inbox/archived cost and sales sync (`extractFromDext`, `runSync`, `runApiSync`) and `manage-dext-to-erpnext-sync` inventory note. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | `extractions`: `runExpenseReportSync` sets `inprogress` then `completed` or `aborted`; `testRunExpenseReportSync` has a commented “inprogress” step but only calls `findByIdAndUpdate` for `completed` / `aborted` (no-op if `_id` missing). `companies`: `runExpenseReportSync` updates `sync_start_date` and `last_sync` for the first company processed only (`break`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `runExpenseReportSync` exits the company loop after the first company (`break` after processing), so only one company runs per extraction — confirm operational intent. `testRunExpenseReportSync` updates `extractions` by `extractionTask._id` but `POST /dext/report` does not supply an extraction id; confirm whether status updates are no-ops or errors in production. `extractExpenseFromDext` returns inside the per-report loop after the first `Expensereport_code`, which may truncate multi-report batches — verify intended behaviour. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`sleek-erpnext-service/src/dext/dext.controller.ts`**
  - `@Post('/report')` → `testRunExpenseReportSync({ company_name, start_date, end_date })`.
- **`sleek-erpnext-service/src/dext/dext.service.ts`**
  - **`runExpenseReportSync(extractionTask)`**: Sets extraction `inprogress`; loads companies via `getCompaniesFromDB`; skips if `last_sync` within 120 minutes; `companyNameTrim(row.name.toLowerCase())`; `getTotalCountExpenseReportDext(companyName, 'vw_dext_directload_costs_expensereports', …)` → `extractExpenseFromDext(..., 'tb_dext_directload_archived_costs', …)`; updates company timestamps; **`break`** after first iteration.
  - **`testRunExpenseReportSync(extractionTask)`**: Uses `extractionTask.company_name`; optional `startDate`/`endDate` with start defaulting to end minus 24 months when set; `syncStartDate`/`syncEndDate` set to “now”; same BQ methods and target tables; non-`test` `NODE_ENV` loads Google Sheet row count for logging only; does not perform the initial `inprogress` update present in `runExpenseReportSync` (comment placeholder only).
- **`sleek-erpnext-service/src/biqquery/bigquery.service.ts`** (import path `biqquery`, not `bigquery`)
  - **`getTotalCountExpenseReportDext`**: `SELECT Expensereport_code FROM …vw_dext_directload_costs_expensereports` with `company_name =`, optional `publish_date` bounds, `GROUP BY Expensereport_code`.
  - **`extractExpenseFromDext`**: Joins expense-report view to `tb_dext_directload_archived_costs` on `code = item_code`, filters by `Expensereport_code`, calls `erpnextService.createPurchaseInvoiceFromDextExpenseReport(rows)` when rows exist.

**Usage confidence rationale:** Controller and BQ → ERPNext chain are explicit; medium because of loop `break`, possible early `return` in `extractExpenseFromDext`, and HTTP path vs extraction document id mismatch.

**Criticality rationale:** Expense-report lines feed ERPNext purchase invoices; failures leave reported expenses out of books or runs stuck in wrong status.
