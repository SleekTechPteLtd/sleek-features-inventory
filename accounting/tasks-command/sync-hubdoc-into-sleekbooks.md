# Sync Hubdoc into SleekBooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Hubdoc into SleekBooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Hubdoc-derived document data is loaded into SleekBooks (ERPNext) bookkeeping so purchase invoices and related records exist for companies that use Hubdoc ingestion, without manual re-keying. |
| **Entry Point / Surface** | **sleek-erpnext-service** NestJS CLI: command **`script:hubdoc-to-sleekbooks`** (`nestjs-command`), described as “sync Hubdoc to SleekBooks”. Sets `GlobalService.isStartFromCommand = true`. There is no Sleek App HTTP route for this path; the commented `handleHubdocInterval`/`handleTaskCron` schedules are not active as the primary surface. |
| **Short Description** | On each run, creates a new **`hubdoc`** extraction run (MongoDB), marks it **in progress**, iterates companies from the company store, and for each company queries Google BigQuery table **`tb_hubdoc_directload_extracted`** for rows in the extraction window. When rows exist, paginated batches are read and, for **`invoice_payable`**, ERPNext creates a **Purchase Invoice** from Hubdoc if one does not already exist. The extraction task ends **completed** or **aborted** on failure. |
| **Variants / Markets** | **SG** (hardcoded `region: 'SG'` on the cron payload); schema allows **HK**, **AU**, **UK** but this script path does not vary them. |
| **Dependencies / Related Flows** | **Upstream** — Hubdoc data landed in BigQuery (`tb_hubdoc_directload_extracted`). **Downstream** — **ERPNext** via `ErpnextService` (`createPurchaseInvoiceFromHubdoc`, `getInvoice`). **Related** — Dext sync (`script:dext-to-sleekbooks`) and shared extraction model; **Google BigQuery** (`asia-southeast1`). **Companies** — `CompaniesService.getCompaniesFromDB` supplies `hubdoc_id`, `sync_start_date`, and normalized names. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | **`extractions`** (Mongoose model `Extraction`; default collection name). **`companies`** (MongoDB model `Companies` — reads `name`, `hubdoc_id`, `sync_start_date`, etc.). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Are `invoice_receivable` and `spendmoney` Hubdoc branches intentionally no-ops (console only)? Should `handleHubDocCron` accept region or date range via CLI args instead of fixed `1970`–end-of-today and `SG`? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/tasks/tasks.command.ts`

- **`@Command({ command: 'script:hubdoc-to-sleekbooks', describe: 'sync Hubdoc to SleekBooks' })`**
- **`hubDocSync()`** — `GlobalService.isStartFromCommand = true` → **`TaskService.handleHubDocCron()`**

### `src/tasks/tasks.service.ts`

- **`handleHubDocCron()`** — builds extraction payload `{ status: 'posted', schedule: 'test', startDate: 1970-01-01, endDate: end of today, region: 'SG' }`
- **`extractionService.create({ extractionType: extractionTypes.hubdoc, ... })`** → **`hubdocService.runSync(hubdocExtraction)`**
- **`handleHubdocInterval()`** (commented `@Interval`) — finds latest **`hubdoc`** extraction with **`status: 'posted'`** and calls **`hubdocService.runSync`**

### `src/extraction/extraction.service.ts`

- **`create()`** — normalizes `startDate`/`endDate` to day boundaries; **`save()`** on **`Extraction`** model

### `src/extraction/schemas/extraction.schema.ts`

- **`extractionType`** (enum includes hubdoc), **`status`** (`posted` → `inprogress` → `completed` / `aborted`), **`region`** (`SG` default in schema enum)

### `src/hubdoc/hubdoc.service.ts`

- **`runSync(extractionTask)`** — updates extraction to **`inprogress`**; **`companiesService.getCompaniesFromDB(null, null, null, '0', '0')`**; per company normalizes name; **`bqService.getTotalCountHubdoc`** / **`bqService.extractFromHubdoc`** on **`tb_hubdoc_directload_extracted`** with **`hubdoc_id`** / `cie_name` filters; final status **`completed`** or **`aborted`**

### `src/biqquery/bigquery.service.ts` (referenced)

- **`extractFromHubdoc`** — batches of 100 rows; **`switch (row.xero_actions_doc_type)`** — **`invoice_payable`** → **`erpnextService.getInvoice`** then **`createPurchaseInvoiceFromHubdoc`** if missing; other doc types logged only
