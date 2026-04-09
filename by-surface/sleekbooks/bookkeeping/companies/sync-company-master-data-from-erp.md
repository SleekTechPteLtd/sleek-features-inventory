# Sync company master data from ERP

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync company master data from ERP |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Company records used by bookkeeping integrations stay aligned with ERPNext, enriched with Sleek and analytics identifiers, and ERPNext gains registration details when they exist only in Sleek. |
| **Entry Point / Surface** | `sleek-erpnext-service` HTTP API: `GET /companies/list` (filter local store by name, UEN, sleek_id, pagination query params), `POST /companies/create-list` (Bearer `authorization` required) to run the batch sync with optional `limit` / `offset`. Exact Sleek app navigation is not defined in this repo. |
| **Short Description** | Operators trigger a paginated batch that reads companies from ERPNext, matches each to Sleek Back via the internal companies API, pulls Hubdoc and Dext identifiers from BigQuery, upserts documents in MongoDB (`bulkWrite` on company name), and when ERPNext lacks `registration_details` but Sleek has a UEN, updates the ERPNext company via `savedocs`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: ERPNext Company doctype (`getCompaniesByFilter`, `updateCompanyInErpNext`). **Enrichment**: Sleek Back `POST /internal/companies` (service basic auth). **Analytics**: BigQuery datasets (`getDextAccountIds`, `getHubdocId` / `getIDOfCompany` on Dext and Hubdoc tables). **Downstream**: Other `sleek-erpnext-service` flows that rely on company UEN, Hubdoc link_id, or Dext `accountCrn` lists stored locally. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | `companies` (Mongoose schema `Companies`; default pluralised collection name) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `GET /companies/list` passes `limit` to `skip` and `offset` to `limit` on the Mongoose query (likely reversed). `updateCompaniesInDBAndErp` contains `return true` inside the per-company loop, so only the first company may be sent to ERPNext update in practice — confirm intent. `getCompanyByNameFromSleekBack` accepts `token` but uses internal basic auth only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/companies/companies.controller.ts`

- **`@Controller('companies')`** — base path `/companies`.
- **`GET /list`** → `getAllCompanies`: query `name`, `uen`, `sleek_id`, `limit`, `offset` → `CompaniesService.getCompaniesFromDB`. No auth decorator.
- **`POST /create-list`** → `updateCompaniesUEN`: requires non-empty `authorization` header (manual check, not Nest guard) → `CompaniesService.updateCompaniesInDB(...)` is **not** `await`ed; response returns immediately with `201` and message that the task is in progress. `@ApiOperation` summary says "Update Existing Company".

### `src/companies/companies.service.ts`

- **`@InjectModel(Companies.name)`** — Mongo `Companies` model.
- **`getCompaniesFromDB`**: `find` with dynamic filter on `name` / `uen` / `sleek_id`; pagination uses `.limit` / `.skip` from query (see open questions).
- **`processAndUpdateInDB`**: `bulkWrite` with `updateOne` keyed by `name`, `upsert: true` — fields: `name`, `uen`, `sleek_id`, `ledger`, `last_sync` (set `null`), `hubdoc_id`, `current_fye`, `dext_account_ids`.
- **`getCompaniesData`**: calls `sleekBackService.getCompanyByNameFromSleekBack`, `bqService.getDextAccountIds`, `bqService.getHubdocId`; builds `erpObj`, `dbObj`, and `updateInErp` when ERP registration was empty but Sleek returned a UEN.
- **`updateCompaniesInDBAndErp`**: `processAndUpdateInDB` then loops companies; if `updateInErp`, calls `erpnextService.updateCompanyInErpNext` (see open questions on loop).
- **`processAndSaveCompanies`**: for each ERP company, `getCompaniesData` then `updateCompaniesInDBAndErp`.
- **`updateCompaniesInDB`**: do/while loop — `erpnextService.getCompaniesByFilter('', queryLimit, queryOffset)` to page all companies when registration filter is empty; advances offset; calls `processAndSaveCompanies`.

### `src/erpnext/erpnext.service.ts`

- **`getCompaniesByFilter(registerationNumber, limit, offset)`**: `GET` Frappe `Company` resource; when `registerationNumber` is empty, uses `limit_page_length` / `limit_start` body params; when set, filters `[["registration_details", "=", "..."]]`.
- **`updateCompanyInErpNext(companyName, companyData)`**: loads existing doc via `getCompanyByNameFromErpNext`, merges, `POST` `frappe.desk.form.save.savedocs` with `action: Save`.

### `src/sleek-back/sleek-back.service.ts`

- **`getCompanyByNameFromSleekBack(token, companyName, uen)`**: `POST` `https://${SLEEK_BACK_API_BASE_URL}/internal/companies` with body `{ uen }`, basic auth `sleek-erpnext` / `SLEEK_SERVICE_CLIENT_SECRET`; returns `response.data.data` or `[]` on error.

### `src/biqquery/bigquery.service.ts`

- **`getDextAccountIds(companyName)`**: unions `accountCrn` from four Dext inbox/archived cost/sales tables via `getIDOfCompany`, `uniq` — used for company’s Dext account identifiers.
- **`getHubdocId` / `getIDOfCompany`**: queries `tb_hubdoc_directload_extracted` by `link_id` (UEN) or `cie_name` (lowercased company name) for Hubdoc `link_id`.
- Class path is `@app/biqquery` (folder spelling `biqquery` in repo).

### `src/companies/schemas/companies.schema.ts`

- **`Companies`**: `name`, `sleek_id`, `uen`, `last_sync`, `status`, `dext_account_ids`, `ledger` (`xero` | `sb`), `hubdoc_id`, `incorporation_date`, `current_fye`, `sync_start_date`; timestamps.
