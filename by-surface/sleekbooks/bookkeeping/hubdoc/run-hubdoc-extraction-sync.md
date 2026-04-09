# Sync Hubdoc extractions into bookkeeping

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Hubdoc extractions into bookkeeping |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (queued **hubdoc** extraction tasks); Operations User when driving CLI/cron-style task creation in **tasks** layer |
| **Business Outcome** | Hubdoc direct-load rows in BigQuery are turned into bookkeeping records in ERPNext (SleekBooks) for each client company in scope, and the linked extraction run is advanced to a terminal status so operations know the job finished. |
| **Entry Point / Surface** | **sleek-erpnext-service**: task orchestration picks the next **`hubdoc`** extraction with **`posted`** status (`TasksService.handleHubdocInterval`), or **`handleHubDocCron`** creates a run and invokes sync; Nest **`GET /hubdoc`** delegates to **`HubdocService.runSync`** (called with `{}` from the controller — not a full extraction document). Related CLI path: **`script:hubdoc-to-sleekbooks`** (see **tasks-command** inventory). No Sleek App screen identified for this path. |
| **Short Description** | For a given extraction task window, the service marks the MongoDB extraction **`inprogress`**, loads all companies from the company store, normalizes each name, and for each company counts and reads **`tb_hubdoc_directload_extracted`** in BigQuery (filtering by **`link_id`** when **`hubdoc_id`** is set, else **`cie_name`**). Paginated rows feed **`extractFromHubdoc`**, which creates **Purchase Invoices** from **`invoice_payable`** lines when missing in ERPNext. On success the extraction is **`completed`**; on error **`aborted`**. |
| **Variants / Markets** | **SG** (default **`region`** on programmatic extraction payloads); **`Extraction`** schema allows **HK**, **AU**, **UK**. |
| **Dependencies / Related Flows** | **Upstream** — Hubdoc data in BigQuery **`tb_hubdoc_directload_extracted`** (project/dataset from env). **Downstream** — **ERPNext** via **`ErpnextService`** (`createPurchaseInvoiceFromHubdoc`, `getInvoice`). **Related** — **`CompaniesService`** company master and **`hubdoc_id`** / **`sync_start_date`**; shared **`extractions`** model with Dext/Xero flows; **Google BigQuery** region **`asia-southeast1`**. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | **`extractions`** (Mongoose **`Extraction`**: status transitions **`posted` → inprogress → completed \| aborted`). **`companies`** (Mongoose **`Companies`**: reads **`name`**, **`hubdoc_id`**, **`sync_start_date`**, etc.). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | **`getTotalCountHubdoc`** receives **`syncStartDate`** / **`syncEndDate`** from **`HubdocService`** but the count query only filters **`created_at`** by the extraction **`startDate`** / **`endDate`** — are the sync parameters intended to be applied? Are **`invoice_receivable`** and **`spendmoney`** branches intentionally no-ops (log only)? Should **`GET /hubdoc`** pass a real extraction task id instead of **`{}`**? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/hubdoc/hubdoc.controller.ts`

- **`@Controller('hubdoc')`** — **`GET /hubdoc`** → **`hubdocService.runSync({})`**.

### `src/hubdoc/hubdoc.service.ts`

- **`runSync(extractionTask)`** — **`extractionModel.findByIdAndUpdate`** → **`status: 'inprogress'`**; **`startDate`** / **`endDate`** from task; **`companiesService.getCompaniesFromDB(null, null, null, '0', '0')`** for full company list; per-row name normalization (suffix stripping); **`bqService.getTotalCountHubdoc`** / **`extractFromHubdoc`** on table **`tb_hubdoc_directload_extracted`** with **`row.hubdoc_id`** and per-company **`sync_start_date`** window args; final **`completed`** or **`aborted`**.

### `src/biqquery/bigquery.service.ts`

- **`getTotalCountHubdoc`** — **`SELECT count(*)`** from **`${bgproject}.${dataset}.${table}`**; **`WHERE link_id`** vs **`LOWER(cie_name)`**; **`created_at`** between **`startDate`** and **`endDate`**.
- **`extractFromHubdoc`** — paginated **`LIMIT 100`**, **`switch (row.xero_actions_doc_type)`**: **`invoice_payable`** → **`getInvoice('Purchase', …)`** then **`createPurchaseInvoiceFromHubdoc`** if no rows; other cases **`console.log`** only.

### `src/companies/companies.service.ts`

- **`getCompaniesFromDB`** — **`companiesModel.find(dbQuery)`** with optional filters; used with empty filters for Hubdoc sync listing.

### Related orchestration (not in FEATURE_LINE file list)

- **`src/tasks/tasks.service.ts`** — **`handleHubdocInterval`**: **`findOne({ extractionType: 'hubdoc', status: 'posted' })`** → **`hubdocService.runSync(hubdocExtraction)`**; **`handleHubDocCron`**: creates **`hubdoc`** extraction then **`await this.hubdocService.runSync(hubdocExtraction)`**.

### `src/extraction/schemas/extraction.schema.ts`

- **`extractionType`**, **`status`** enum (**`inprogress`**, **`completed`**, **`aborted`**, …), **`startDate`**, **`endDate`**, **`region`**.
